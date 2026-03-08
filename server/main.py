from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import smtplib
import random
import datetime
from datetime import timedelta, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx
import models, database, crud, auth

app = FastAPI()

# Enable CORS to prevent browser hanging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB Migration & Initialization
@app.on_event("startup")
def startup_db():
    try:
        models.Base.metadata.create_all(bind=database.engine)
        db = database.SessionLocal()
        try:
            # HWID Reset Column Migration
            try: db.execute(text("SELECT last_hwid_reset FROM users LIMIT 1"))
            except:
                db.rollback()
                db.execute(text("ALTER TABLE users ADD COLUMN last_hwid_reset TIMESTAMP"))
                db.commit()
            
            # Email Column Migration
            try: db.execute(text("SELECT email FROM users LIMIT 1"))
            except:
                db.rollback()
                db.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR"))
                db.commit()

            # Ensure admin has email for testing OTP
            admin = crud.get_user(db, "mrogtool")
            if admin and not admin.email:
                admin.email = "mbarakaligwema@gmail.com"
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Startup error: {e}")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")
downloads_dir = os.path.join(BASE_DIR, "downloads")

# Mounts
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/downloads", StaticFiles(directory=downloads_dir), name="downloads")
templates = Jinja2Templates(directory=templates_dir)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- WEB ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    
    if not user.is_active:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Account blocked."})

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
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords mismatch"})
    if crud.get_user(db, username):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username taken"})
    try:
        crud.create_user(db, username, password, email=email, is_active=False)
        crud.create_notification(db, f"New user: {username}")
        return RedirectResponse(url="/login?msg=registered", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.post("/api/send-otp")
async def send_otp(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        email = data.get("email")
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user: return JSONResponse({"status": "error", "message": "Email not found"}, status_code=404)
        
        otp = str(random.randint(100000, 999999))
        db.query(models.PasswordReset).filter(models.PasswordReset.email == email).delete()
        db.add(models.PasswordReset(email=email, otp=otp))
        db.commit()
        
        # BREVO API SETTINGS (Reading from Railway Variables for security)
        BREVO_API_KEY = os.getenv("BREVO_API_KEY")
        
        if not BREVO_API_KEY:
             return JSONResponse({"status": "error", "message": "Server Config Error: Missing API Key."}, status_code=500)

        payload = {
            "sender": {"name": "MR OG TOOL", "email": "mbarakaligwema@gmail.com"},
            "to": [{"email": email}],
            "subject": "🔐 MR OG TOOL - Reset Code",
            "htmlContent": f"""
            <div style="font-family: Arial; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2196F3;">MR OG TOOL</h2>
                <p>Hello <b>{user.username}</b>,</p>
                <p>Your verification code to reset your password is:</p>
                <h1 style="background: #f4f4f4; padding: 10px; text-align: center; letter-spacing: 5px;">{otp}</h1>
                <p>This code will expire in 10 minutes. If you did not request this, please ignore this email.</p>
            </div>
            """
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": BREVO_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json=payload,
                timeout=15.0
            )
            
        if response.status_code in [200, 201]:
            return {"status": "success", "message": "OTP Sent!"}
        else:
            return JSONResponse({"status": "error", "message": f"Brevo API Error: {response.text}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Server Error: {str(e)}"}, status_code=500)

@app.post("/api/reset-password")
async def reset_password_api(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email, otp, new_pass = data.get("email"), data.get("otp"), data.get("new_password")
    reset = db.query(models.PasswordReset).filter(models.PasswordReset.email == email, models.PasswordReset.otp == otp).order_by(models.PasswordReset.id.desc()).first()
    if not reset or (datetime.utcnow() - reset.created_at).total_seconds() > 600:
        return JSONResponse({"status": "error", "message": "Invalid/Expired OTP"}, status_code=400)
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        user.hashed_password = auth.get_password_hash(new_pass)
        db.delete(reset)
        db.commit()
        return {"status": "success", "message": "Password updated!"}
    return JSONResponse({"status": "error", "message": "User not found"}, status_code=404)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user: return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: return RedirectResponse(url="/dashboard")
    users = crud.get_users(db)
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "users": users})

# --- ADMIN ACTIONS ---
@app.post("/admin/users/{user_id}/toggle")
async def toggle_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: raise HTTPException(status_code=403)
    crud.toggle_user_active(db, user_id)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/users/{user_id}/delete")
async def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: raise HTTPException(status_code=403)
    crud.delete_user(db, user_id)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/users/{user_id}/extend")
async def extend_user(user_id: int, request: Request, duration: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: raise HTTPException(status_code=403)
    
    if duration == "make_admin":
        crud.set_user_admin_status(db, user_id, True)
    elif duration == "revoke_admin":
        crud.set_user_admin_status(db, user_id, False)
    else:
        crud.extend_user_expiry(db, user_id, duration)
        
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/users/add")
async def add_user_admin(request: Request, 
                         username: str = Form(...), 
                         password: str = Form(...), 
                         is_admin: bool = Form(False), 
                         db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: raise HTTPException(status_code=403)
    
    if crud.get_user(db, username):
        users = crud.get_users(db)
        return templates.TemplateResponse("admin.html", {"request": request, "user": user, "users": users, "error": "Username already exists"})
    
    crud.create_user(db, username, password, is_admin=is_admin)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/users/{user_id}/reset_password")
async def admin_reset_password(user_id: int, request: Request, new_password: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: raise HTTPException(status_code=403)
    
    crud.reset_user_password(db, user_id, new_password)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/users/{user_id}/reset_hwid")
async def reset_hwid(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: raise HTTPException(status_code=403)
    crud.reset_user_hwid(db, user_id)
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/api/v1/notifications")
async def get_notifications(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: return {"count": 0, "notifications": []}
    notifs = crud.get_latest_notifications(db)
    return {"count": len([n for n in notifs if not n.is_read]), "notifications": [{"id": n.id, "message": n.message, "is_read": n.is_read, "time": n.created_at.strftime("%H:%M")} for n in notifs]}

# --- DESKTOP API ---
@app.post("/api/v1/verify")
async def verify_user(username: str = Form(...), password: str = Form(...), hwid: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
    if not user: return JSONResponse({"status": "BLOCK", "message": "No User"}, status_code=404)
    if not auth.verify_password(password, user.hashed_password): return JSONResponse({"status": "BLOCK", "message": "Wrong Pass"}, status_code=403)
    if not user.is_active: return JSONResponse({"status": "BLOCK", "message": "Account Blocked"}, status_code=403)
    if user.is_expired(): return JSONResponse({"status": "BLOCK", "message": "Expired"}, status_code=403)
    
    now = datetime.utcnow()
    if user.hwid and user.hwid != hwid:
        if user.last_hwid_reset and (now - user.last_hwid_reset).total_seconds() < 12*3600:
            return JSONResponse({"status": "BLOCK", "message": "HWID Cooldown"}, status_code=403)
        user.hwid, user.last_hwid_reset = hwid, now
        db.commit()
    elif not user.hwid:
        user.hwid = hwid
        db.commit()
    return {"status": "OK", "message": "Access Granted", "expiry": user.expiry_date.strftime('%Y-%m-%d') if user.expiry_date else "LIFETIME"}

@app.get("/api/v1/latest_version")
async def latest_version():
    return {"version": "1.7.2", "download_url": "https://www.mediafire.com/file/wywu9fbj3jrw13d/MR_OG_TOOL_Setup_v1.7.2.exe/file", "changelog": "v1.7.2 Platinum - Stability Fix"}

# Helper
def get_current_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token: return None
    try:
        _, _, param = token.partition(" ")
        payload = auth.jwt.decode(param, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        return crud.get_user(db, username=payload.get("sub"))
    except: return None
