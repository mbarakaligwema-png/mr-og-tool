from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    hwid = Column(String, nullable=True)
    last_hwid_reset = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True) # None = Lifetime
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def is_expired(self):
        if self.expiry_date and datetime.datetime.utcnow() > self.expiry_date:
            return True
        return False
