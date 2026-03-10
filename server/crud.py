from sqlalchemy.orm import Session
import models, auth
import datetime

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).order_by(models.User.id.desc()).offset(skip).limit(limit).all()

def create_user(db: Session, username: str, password: str, email: str = None, is_admin: bool = False, is_active: bool = True):
    hashed_password = auth.get_password_hash(password)
    # Default to Lifetime (None) so they technically have a license, but will be blocked by is_active=False.
    default_expiry = None
    
    db_user = models.User(username=username, email=email, hashed_password=hashed_password, is_admin=is_admin, is_active=is_active, expiry_date=default_expiry)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def toggle_user_active(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_active = not user.is_active
        db.commit()
        return user
    return None

def extend_user_expiry(db: Session, user_id: int, duration_type: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    # Start from NOW if expired, or from current expiry if valid
    base_date = datetime.datetime.utcnow()
    if user.expiry_date and user.expiry_date > base_date:
        base_date = user.expiry_date
    
    if duration_type == "6_hours":
        user.expiry_date = base_date + datetime.timedelta(hours=6)
    elif duration_type == "2_months":
        user.expiry_date = base_date + datetime.timedelta(days=60)
    elif duration_type == "3_months":
        user.expiry_date = base_date + datetime.timedelta(days=90)
    elif duration_type == "6_months":
        user.expiry_date = base_date + datetime.timedelta(days=180)
    elif duration_type == "1_year":
        user.expiry_date = base_date + datetime.timedelta(days=365)
    elif duration_type == "lifetime":
        user.expiry_date = None # None means lifetime
        
    db.commit()
    return user

def reset_user_password(db: Session, user_id: int, new_password: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.hashed_password = auth.get_password_hash(new_password)
        db.commit()
        return user
    return None
    
def reset_user_hwid(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.hwid = None
        db.commit()
        return user
    return None

def set_user_admin_status(db: Session, user_id: int, is_admin: bool):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_admin = is_admin
        # If admin, usually we want to clear expiry or set to None (Unlimited)
        # But let's respect current logic.
        if is_admin:
            user.expiry_date = None # Auto Lifetime for Admin
        db.commit()
        return user
    return None

# --- NOTIFICATIONS ---
def create_notification(db: Session, message: str):
    db_notif = models.Notification(message=message)
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def get_latest_notifications(db: Session, limit: int = 20):
    return db.query(models.Notification).order_by(models.Notification.created_at.desc()).limit(limit).all()

def reset_user_expiry(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        # Set to 1 hour ago to expire it
        user.expiry_date = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        db.commit()
        return user
    return None

def mark_notifications_read(db: Session):
    db.query(models.Notification).update({models.Notification.is_read: True})
    db.commit()
