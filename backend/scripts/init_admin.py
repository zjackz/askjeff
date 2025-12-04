"""
初始化默认用户

运行此脚本创建默认账户：
1. 管理员：admin / admin666
2. 运营人员：shangu / shangu666
"""
from app.core.security import get_password_hash
from app.db import SessionLocal
from app.models.user import User


def create_user_if_not_exists(db, username: str, password: str, role: str = "admin"):
    """创建用户（如果不存在）"""
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"  ⊙ 用户 '{username}' 已存在，跳过")
        return existing_user
    
    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        is_active=True,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"  ✓ 创建用户 '{username}' (角色: {role}, ID: {user.id})")
    return user


def init_default_users():
    """初始化默认用户"""
    db = SessionLocal()
    try:
        print("初始化默认用户...")
        print()
        
        # 1. 创建管理员账户
        print("1. 管理员账户:")
        create_user_if_not_exists(db, "admin", "admin666", "admin")
        
        # 2. 创建运营人员账户
        print()
        print("2. 运营人员账户:")
        create_user_if_not_exists(db, "shangu", "shangu666", "operator")
        
        print()
        print("=" * 50)
        print("默认账户信息:")
        print("  管理员   - 用户名: admin   密码: admin666")
        print("  运营人员 - 用户名: shangu  密码: shangu666")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_default_users()
