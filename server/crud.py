from sqlalchemy.orm import Session
import models, auth
import datetime

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, username: str, password: str, is_admin: bool = False):
    hashed_password = auth.get_password_hash(password)
    # Default to NOW (Immediately Expired) so they need a package. 
    # If is_admin, maybe give lifetime? Let's keep it consistent, admin can give themselves time.
    # actually admin usually needs access.
    default_expiry = None if is_admin else datetime.datetime.utcnow()
    
    db_user = models.User(username=username, hashed_password=hashed_password, is_admin=is_admin, expiry_date=default_expiry)
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
