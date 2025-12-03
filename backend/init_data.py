import logging
from app.db import SessionLocal
from app.models.user import User
from app.core import security

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init():
    db = SessionLocal()
    try:
        # Create admin user
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            user = User(
                username="admin",
                hashed_password=security.get_password_hash("password"),
                role="admin",
                is_active=True,
            )
            db.add(user)
            db.commit()
            logger.info("Created default user: admin/password (role: admin)")
        else:
            # Ensure admin has admin role
            if user.role != "admin":
                user.role = "admin"
                db.add(user)
                db.commit()
                logger.info("Updated admin user role to admin")
            logger.info("Default user admin already exists")

        # Create shangu user
        user_shangu = db.query(User).filter(User.username == "shangu").first()
        if not user_shangu:
            user_shangu = User(
                username="shangu",
                hashed_password=security.get_password_hash("password"),
                role="shangu",
                is_active=True,
            )
            db.add(user_shangu)
            db.commit()
            logger.info("Created operator user: shangu/password (role: shangu)")
        else:
            logger.info("Operator user shangu already exists")
    finally:
        db.close()

if __name__ == "__main__":
    init()
