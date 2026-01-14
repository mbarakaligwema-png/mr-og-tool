from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta

import models, database, crud, auth

import models, database, crud, auth
import os



# Init DB
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "v1.6-DEBUG"}

@app.get("/debug")
def debug_info():
    import os
    return {
        "db_path_var": database.DB_PATH,
        "var_data_exists": os.path.exists("/var/data"),
        "cwd": os.getcwd(),
        "files_in_var_data": os.listdir("/var/data") if os.path.exists("/var/data") else "N/A",
        "env_render": os.getenv("RENDER", "Not Found")
    }

# Absolute Path Resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# Mount Static & Templates
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    try:
        if not crud.get_user(db, "mrogtool"):
            crud.create_user(db, "mrogtool", "dell", is_admin=True)
            print("--- DEFAULT ADMIN CREATED: mrogtool / dell ---")
    finally:
        db.close()

# --- WEB ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    # Always show Home Page now, user state handled in navbar
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/resellers", response_class=HTMLResponse)
async def resellers_page(request: Request):
    return templates.TemplateResponse("resellers.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    
    if not user.is_active:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Account is blocked. Contact Admin."})

    # Create Token
    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match"})
    
    if crud.get_user(db, username):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken"})
    
    try:
        crud.create_user(db, username, password, email=email)
        return RedirectResponse(url="/login?msg=registered", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"--- REGISTRATION ERROR: {e} ---")
        return templates.TemplateResponse("register.html", {"request": request, "error": f"Registration failed: {str(e)}"})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    users = crud.get_users(db)
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "users": users})

@app.post("/admin/users/add")
async def admin_add_user(request: Request, username: str = Form(...), password: str = Form(...), is_admin: bool = Form(False), db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if crud.get_user(db, username):
        users = crud.get_users(db)
        return templates.TemplateResponse("admin.html", {"request": request, "user": user, "users": users, "error": "User already exists"})
    
    crud.create_user(db, username, password, is_admin)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/{user_id}/toggle")
async def toggle_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    crud.toggle_user_active(db, user_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/{user_id}/delete")
async def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    crud.delete_user(db, user_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/{user_id}/extend")
async def extend_user(user_id: int, request: Request, duration: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    crud.extend_user_expiry(db, user_id, duration)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/{user_id}/reset_password")
async def reset_password(user_id: int, request: Request, new_password: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    crud.reset_user_password(db, user_id, new_password)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/{user_id}/reset_hwid")
async def reset_hwid(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    crud.reset_user_hwid(db, user_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

# --- API ENDPOINTS (For Desktop Tool) ---

@app.post("/api/v1/verify")
@app.post("/api/v1/verify")
async def verify_user(username: str = Form(...), password: str = Form(...), hwid: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
    
    if not user:
        return JSONResponse(content={"status": "BLOCK", "message": "User not found."}, status_code=404)
        
    if not auth.verify_password(password, user.hashed_password):
        return JSONResponse(content={"status": "BLOCK", "message": "Wrong Password."}, status_code=403)
    
    if not user.is_active:
        return JSONResponse(content={"status": "BLOCK", "message": "Account is BLOCKED."}, status_code=403)
    
    if user.is_expired():
        return JSONResponse(content={"status": "BLOCK", "message": "License Expired."}, status_code=403)
    
    # HWID Logic
    if user.hwid:
        if user.hwid != hwid:
            # Check if admin allows reset (Manual) or auto-block
            return JSONResponse(content={"status": "BLOCK", "message": "HWID Mismatch. Locked to another PC."}, status_code=403)
    else:
    # First time login = Bind HWID
        user.hwid = hwid
        db.commit()
    
    expiry_str = user.expiry_date.strftime('%Y-%m-%d %H:%M') if user.expiry_date else "LIFETIME"
    return JSONResponse(content={"status": "OK", "message": "Access Granted.", "expiry": expiry_str})


# --- HELPER ---
def get_current_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        scheme, _, param = token.partition(" ")
        payload = auth.jwt.decode(param, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except auth.JWTError:
        return None
    
    user = crud.get_user(db, username=username)
    return user
