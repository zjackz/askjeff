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
                hashed_password=security.get_password_hash("admin666"),
                role="admin",
                is_active=True,
            )
            db.add(user)
            db.commit()
            logger.info("Created default user: admin/admin666 (role: admin)")
            # Ensure admin has admin role and correct password
            updated = False
            if user.role != "admin":
                user.role = "admin"
                updated = True
            
            # Verify/Update password
            # Note: We can't easily verify hash, so we just re-hash and update to be sure, 
            # or we could check verify_password if available. 
            # For simplicity in this init script, let's just update it to ensure it's correct.
            new_hash = security.get_password_hash("admin666")
            if user.hashed_password != new_hash: # This check might be naive if salt is random
                 user.hashed_password = new_hash
                 updated = True

            if updated:
                db.add(user)
                db.commit()
                logger.info("Updated admin user role/password")
            else:
                logger.info("Default user admin already exists and is up to date")

        # Create shangu user
        user_shangu = db.query(User).filter(User.username == "shangu").first()
        if not user_shangu:
            user_shangu = User(
                username="shangu",
                hashed_password=security.get_password_hash("shangu666"),
                role="shangu",
                is_active=True,
            )
            db.add(user_shangu)
            db.commit()
            logger.info("Created operator user: shangu/shangu666 (role: shangu)")
        else:
             # Update shangu password
            user_shangu.hashed_password = security.get_password_hash("shangu666")
            db.add(user_shangu)
            db.commit()
            logger.info("Updated operator user shangu password")
    finally:
        db.close()

if __name__ == "__main__":
    init()
