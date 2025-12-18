import logging

from app.db import SessionLocal
from app.models.user import User
from app.core import security

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            user.hashed_password = security.get_password_hash("password")
            db.add(user)
            db.commit()
            logger.info("Reset password for user 'admin' to 'password'")
        else:
            logger.error("User 'admin' not found")
            
        user_shangu = db.query(User).filter(User.username == "shangu").first()
        if user_shangu:
            user_shangu.hashed_password = security.get_password_hash("password")
            db.add(user_shangu)
            db.commit()
            logger.info("Reset password for user 'shangu' to 'password'")
        else:
            logger.error("User 'shangu' not found")
            
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
