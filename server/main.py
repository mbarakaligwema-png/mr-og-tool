from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

import models, database, crud, auth


import models, database, crud, auth
import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Init DB
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- ENABLE CORS (Allow everything to prevent freezing) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "v1.7.1-STABLE"}

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
downloads_dir = os.path.join(BASE_DIR, "downloads")
app.mount("/downloads", StaticFiles(directory=downloads_dir), name="downloads")
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
        # --- AUTO MIGRATION CHECK ---
        from sqlalchemy import text
        try:
            # Try to select the new column. If it fails, we need to add it.
            db.execute(text("SELECT last_hwid_reset FROM users LIMIT 1"))
        except Exception as e:
            print(f"--- MIGRATION NEEDED: {e} ---")
            print("--- ADDING COLUMN: last_hwid_reset ---")
            try:
                # Add Column (TIMESTAMP is safer for Postgres than DATETIME)
                db.rollback() # clear previous error state
                # Check if sqlite or postgres to be safe, but TIMESTAMP works for both usually (SQLite adapts)
                # But to be absolutely safe, let's just use generic SQL
                db.execute(text("ALTER TABLE users ADD COLUMN last_hwid_reset TIMESTAMP"))
                db.commit()
                print("--- MIGRATION SUCCESS! ---")
            except Exception as e2:
                print(f"--- MIGRATION FAILED: {e2} ---")
        
        # --- MIGRATION FOR EMAIL COLUMN ---
        try:
             db.execute(text("SELECT email FROM users LIMIT 1"))
        except Exception as e:
             print("--- MIGRATION: ADDING EMAIL COLUMN ---")
             try:
                 db.rollback()
                 db.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR"))
                 db.commit()
             except: pass
        
        # --- Create Default Admin & Assign Email ---
        admin_user = crud.get_user(db, "mrogtool")
        if admin_user:
            admin_user.email = "mbarakaligwema@gmail.com"  # Set for testing
            db.commit()
            print("--- ADMIN EMAIL UPDATED: mbarakaligwema@gmail.com ---")
        else:
            crud.create_user(db, "mrogtool", "dell", email="mbarakaligwema@gmail.com", is_admin=True)
            print("--- DEFAULT ADMIN CREATED WITH EMAIL ---")
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

@app.get("/active-license", response_class=HTMLResponse)
async def active_license_page(request: Request):
    return templates.TemplateResponse("active_license.html", {"request": request})

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
        new_user = crud.create_user(db, username, password, email=email)
        # Create Notification for Admin
        crud.create_notification(db, f"Mteja mpya amejiunga: {username}")
        return RedirectResponse(url="/login?msg=registered", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"--- REGISTRATION ERROR: {e} ---")
        return templates.TemplateResponse("register.html", {"request": request, "error": f"Registration failed: {str(e)}"})

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
    data = await request.json()
    email = data.get("email")
    
    # Check if user exists with this email
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return JSONResponse({"status": "error", "message": "No account found with this email."}, status_code=404)
    
    # Generate OTP
    otp = str(random.randint(100000, 999999))
    
    try:
        # Clear old resets for this email and save new one
        db.query(models.PasswordReset).filter(models.PasswordReset.email == email).delete()
        new_reset = models.PasswordReset(email=email, otp=otp)
        db.add(new_reset)
        db.commit()
    except Exception as e:
        db.rollback()
        return JSONResponse({"status": "error", "message": f"Database error: {str(e)}"}, status_code=500)
    
    # Send Email
    sender_email = "mbarakaligwema@gmail.com"
    app_password = "coff qchr kcrk nkwo"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🔐 MR OG TOOL - Reset Code"
    msg["From"] = f"MR OG TOOL ADMIN <{sender_email}>"
    msg["To"] = email
    
    html = f"""
    <div style="font-family: Arial; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #2196F3;">MR OG TOOL</h2>
        <p>Hello <b>{user.username}</b>,</p>
        <p>Your verification code to reset your password is:</p>
        <h1 style="background: #f4f4f4; padding: 10px; text-align: center; letter-spacing: 5px;">{otp}</h1>
        <p>This code will expire in 10 minutes. If you did not request this, please ignore this email.</p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email, msg.as_string())
        return {"status": "success", "message": "OTP Sent!"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Failed to send email: {str(e)}"}, status_code=500)

@app.post("/api/reset-password")
async def reset_password_api(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email = data.get("email")
    otp = data.get("otp")
    new_pass = data.get("new_password")
    
    # Verify OTP
    reset_entry = db.query(models.PasswordReset).filter(models.PasswordReset.email == email, models.PasswordReset.otp == otp).first()
    if not reset_entry:
        return JSONResponse({"status": "error", "message": "Invalid or expired OTP code."}, status_code=400)
    
    # Check if expired (10 mins)
    time_diff = datetime.utcnow() - reset_entry.created_at
    if time_diff.total_seconds() > 600:
        db.delete(reset_entry)
        db.commit()
        return JSONResponse({"status": "error", "message": "OTP has expired. Please request a new one."}, status_code=400)
    
    # Perform Reset
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        user.hashed_password = auth.get_password_hash(new_pass)
        db.delete(reset_entry) # Delete OTP after use
        db.commit()
        return {"status": "success", "message": "Password updated successfully!"}
    
    return JSONResponse({"status": "error", "message": "User not found."}, status_code=404)

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
    
    crud.create_user(db, username, password, email=None, is_admin=is_admin)
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
    
    if duration == "make_admin":
        crud.set_user_admin_status(db, user_id, True)
    elif duration == "revoke_admin":
        crud.set_user_admin_status(db, user_id, False)
    else:
        crud.extend_user_expiry(db, user_id, duration)
        
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/{user_id}/reset_password")
async def reset_password(user_id: int, request: Request, new_password: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    print(f"--- RESETTING PASSWORD FOR USER ID: {user_id} ---")
    updated_user = crud.reset_user_password(db, user_id, new_password)
    if updated_user:
        print(f"--- SUCCESS: Password updated for {updated_user.username} ---")
    else:
        print(f"--- FAILED: User {user_id} not found ---")
        
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/{user_id}/reset_hwid")
async def reset_hwid(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    crud.reset_user_hwid(db, user_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/api/v1/notifications")
async def get_notifications(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        return JSONResponse({"count": 0, "notifications": []})
    
    notifs = crud.get_latest_notifications(db)
    unread_count = len([n for n in notifs if not n.is_read])
    
    return {
        "count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "is_read": n.is_read,
                "time": n.created_at.strftime("%H:%M")
            } for n in notifs
        ]
    }

@app.post("/api/v1/notifications/read")
async def read_notifications(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin:
        return {"status": "error"}
    
    crud.mark_notifications_read(db)
    return {"status": "ok"}

# --- API ENDPOINTS (For Desktop Tool) ---


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
    # Note: datetime/timedelta should be at top level, but for now we import locally if needed or use stdlib
    from datetime import datetime
    
    if user.hwid:
        if user.hwid != hwid:
            # Check 12 Hour Rule
            now = datetime.utcnow()
            allow_reset = False
            remaining_hours = 0
            
            if user.last_hwid_reset:
                 time_diff = now - user.last_hwid_reset
                 # Check if time_diff is valid (it should be a timedelta)
                 total_seconds = time_diff.total_seconds()
                 if total_seconds > (12 * 3600): # 12 Hours
                     allow_reset = True
                 else:
                     remaining_hours = 12 - (total_seconds / 3600)
            else:
                 # First time reset is free
                 allow_reset = True
            
            if allow_reset:
                user.hwid = hwid
                user.last_hwid_reset = now
                db.commit()
            else:
                return JSONResponse(content={"status": "BLOCK", "message": f"HWID Mismatch. Reset cooldown: {int(remaining_hours)}h remaining."}, status_code=403)
    else:
        # First time login = Bind HWID
        user.hwid = hwid
        # IMPORTANT: Do NOT set last_hwid_reset here, 
        # so their first REAL reset (to a 2nd PC) is always allowed.
        user.last_hwid_reset = None 
        db.commit()
    
    expiry_str = user.expiry_date.strftime('%Y-%m-%d %H:%M') if user.expiry_date else "LIFETIME"
    return JSONResponse(content={"status": "OK", "message": "Access Granted.", "expiry": expiry_str})

@app.get("/api/v1/latest_version")
async def latest_version():
    return {
        "version": "1.7.1", 
        "download_url": "https://www.mediafire.com/file/yl428z37lwyvrt9/MR_OG_TOOL_Setup_v1.7.1.exe/file",
        "changelog": "★ MR OG TOOL v1.7.1 ★\n\n- NEW: Samsung A06 KG BYPASS (Supported U8 / U9)\n- NEW: ZTE A35 QR CODE FIX (100% Working)\n- IMPROVED: KG 2025 Premium Logic\n- FIXED: Setup Installation Issues\n- ADDED: Video Guide Integration"
    }


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
