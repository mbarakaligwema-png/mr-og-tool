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
import selcom_api
import palmpesa_api

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
    return templates.TemplateResponse(request, "home.html", {"user": user})

@app.get("/resellers", response_class=HTMLResponse)
async def resellers_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(request, "resellers.html", {"user": user})

@app.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(request, "shop.html", {"user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    message = None
    if msg == "registered":
        message = "Account Pending Admission. Lifetime License Ready."
    return templates.TemplateResponse(request, "login.html", {"msg": message, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid credentials", "msg": None})
    
    # Allow inactive users to login to website (for payment only)
    # They will be redirected to shop to pay and activate account
    access_token = auth.create_access_token(data={"sub": user.username})
    
    if not user.is_active:
        # Inactive: login but redirect to shop to pay
        response = RedirectResponse(url="/shop?msg=pay_to_activate", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response

    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"error": None})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    if password != confirm_password:
        return templates.TemplateResponse(request, "register.html", {"error": "Passwords mismatch"})
    if crud.get_user(db, username):
        return templates.TemplateResponse(request, "register.html", {"error": "Username taken"})
    if crud.get_user_by_email(db, email):
        return templates.TemplateResponse(request, "register.html", {"error": "Email already in use"})
    try:
        crud.create_user(db, username, password, email=email, is_active=False)
        crud.create_notification(db, f"New user: {username}")
        return RedirectResponse(url="/login?msg=registered", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return templates.TemplateResponse(request, "register.html", {"error": str(e)})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.get("/api/check-status")
async def check_user_status(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse({"active": False, "error": "unauthorized"}, status_code=401)
    return {"active": user.is_active}

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, "forgot_password.html", {})

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
    return templates.TemplateResponse(request, "dashboard.html", {"user": user})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: return RedirectResponse(url="/dashboard")
    users = crud.get_users(db)
    return templates.TemplateResponse(request, "admin.html", {"user": user, "users": users, "error": None})

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
        return templates.TemplateResponse(request, "admin.html", {"user": user, "users": users, "error": "Username already exists"})
    
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
    if not user.is_active: return JSONResponse({"status": "BLOCK", "message": "Account Pending Activation"}, status_code=403)
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
    return {
        "version": "1.7.5",
        "download_url": "https://mega.nz/file/vDYjFKiZ#3zZlP__DcX2CYXlowViJZjY-7pjRU369VHhfSGQFFto",
        "changelog": "v1.7.5 - New Premium DNS Engine, Samsung Buttons Renamed"
    }


@app.post("/admin/users/{user_id}/reset_expiry")
async def admin_reset_expiry(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not user.is_admin: raise HTTPException(status_code=403)
    crud.reset_user_expiry(db, user_id)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/api/pay/selcom/ussd")
async def initiate_selcom_payment(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    phone = data.get("phone")
    plan = data.get("plan")
    
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse({"status": "error", "message": "Unauthorized, please login first."}, status_code=401)
        
    if not phone or not plan:
        return JSONResponse({"status": "error", "message": "Missing phone number or plan"}, status_code=400)

    if plan == "12_months":
        amount = 54
        plan_code = "12"
    elif plan == "6_months":
        amount = 39
        plan_code = "6m"
    elif plan == "6_hours":
        amount = 4
        plan_code = "6h"
    else:
        amount = 39
        plan_code = "6m"

    # TZS conversion approx (assumed 2700 for simplicity or fixed price as per your logic)
    amount_tzs = amount * 2700 
    
    order_id = f"MR_{user.id}_{plan_code}_{int(datetime.now().timestamp())}"
    
    # Call Selcom API here
    result = selcom_api.initiate_ussd_push(phone, amount_tzs, order_id, user.email)
    
    if result.get("result") == "SUCCESS":
        return JSONResponse({"status": "pending", "message": f"Push request sent to {phone}. Please enter your PIN."})
    else:
        return JSONResponse({"status": "error", "message": result.get("message", "Payment initiation failed")}, status_code=500)

@app.post("/api/pay/palmpesa/ussd")
async def initiate_palmpesa_payment(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    phone = data.get("phone")
    plan = data.get("plan")
    
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse({"status": "error", "message": "Unauthorized"}, status_code=401)
        
    if not phone or not plan:
        return JSONResponse({"status": "error", "message": "Missing phone or plan"}, status_code=400)

    # Conversion logic similar to Selcom
    rates = {"12_months": 54, "6_months": 39, "6_hours": 4}
    amount_usd = rates.get(plan, 39)
    amount_tzs = amount_usd * 2700 
    
    plan_code = {"12_months": "12", "6_hours": "6h"}.get(plan, "6m")
    order_id = f"MR_PP_{user.id}_{plan_code}_{int(datetime.now().timestamp())}"
    
    result = palmpesa_api.initiate_ussd_push(
        phone_number=phone,
        amount_tzs=amount_tzs,
        order_id=order_id,
        buyer_name=user.username,
        buyer_email=user.email or "user@mrogtool.com"
    )
    
    if result.get("result") == "SUCCESS":
        return JSONResponse({"status": "pending", "message": result.get("message", f"PalmPesa: Push sent to {phone}. Confirm with your PIN.")})
    else:
        return JSONResponse({"status": "error", "message": result.get("message", "PalmPesa failed")}, status_code=500)

@app.post("/api/palmpesa/webhook")
async def palmpesa_webhook(request: Request, db: Session = Depends(get_db)):
    # PalmPay/PalmPesa Webhook
    try:
        data = await request.json()
        print(f"[PalmPesa Webhook] Received Data: {data}")
        
        # PalmPesa status fields
        status = data.get("status") or data.get("trade_status") or data.get("resultcode") or data.get("transaction_status")
        # PalmPesa order ID fields
        order_id = data.get("orderId") or data.get("merchant_order_id") or data.get("transaction_id") or data.get("reference")
        
        # Check for success indicators (000, 0, SUCCESS, success, approved, etc.)
        status_str = str(status).strip().upper() if status is not None else ""
        is_success = status_str in ["SUCCESS", "COMPLETED", "TRADE_SUCCESS", "000", "0", "APPROVED", "OK"]
            
        if is_success and order_id:
            # parsing order id: MR_PP_{user_id}_{planCode}_{timestamp}
            parts = str(order_id).split("_")
            if len(parts) >= 4 and parts[0] == "MR" and parts[1] == "PP":
                user_id = int(parts[2])
                plan_code = parts[3]
                
                plan_duration = {"12": "1_year", "6h": "6_hours"}.get(plan_code, "6_months")
                crud.extend_user_expiry(db, user_id, plan_duration)
                crud.create_notification(db, f"PalmPesa Payment Verified: User {user_id} plan {plan_duration}")
                print(f"[PalmPesa Webhook] Success processed for user {user_id}")
    except Exception as e:
        print(f"PalmPesa Webhook error: {e}")
            
    return JSONResponse({"status": "SUCCESS"})

@app.post("/api/selcom/webhook")
async def selcom_webhook(request: Request, db: Session = Depends(get_db)):
    # Called by Selcom when payment succeeds
    data = await request.json()
    status = data.get("payment_status")
    order_id = data.get("order_id") # e.g. MR_{user_id}_{timestamp}
    
    if status == "COMPLETED" and order_id:
        try:
            # parsing order id: MR_{user_id}_{planCode}_{timestamp}
            parts = order_id.split("_")
            user_id = int(parts[1])
            plan_code = parts[2]
            
            if plan_code == "12":
                plan_duration = "1_year"
            elif plan_code == "6h":
                plan_duration = "6_hours"
            else:
                plan_duration = "6_months"
                
            crud.extend_user_expiry(db, user_id, plan_duration)
        except Exception as e:
            print(f"Webhook error: {e}")
            
    return JSONResponse({"status": "success"})

# Helper
def get_current_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token: return None
    try:
        _, _, param = token.partition(" ")
        payload = auth.jwt.decode(param, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        return crud.get_user(db, username=payload.get("sub"))
    except: return None
