import os
from sqlalchemy import create_engine, text

def migrate():
    url = os.environ.get("DATABASE_URL", "postgresql+psycopg://sorftime:sorftime@db:5432/sorftime_dev")
    engine = create_engine(url)
    
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        
        # Check if table exists
        check_sql = text("""
            SELECT to_regclass('public.users');
        """)
        result = conn.execute(check_sql).fetchone()
        
        if not result or not result[0]:
            print("Creating users table...")
            conn.execute(text("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR NOT NULL UNIQUE,
                    hashed_password VARCHAR NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """))
            conn.execute(text("CREATE INDEX ix_users_username ON users (username);"))
            conn.execute(text("CREATE INDEX ix_users_id ON users (id);"))
            conn.commit()
            print("Table users created successfully.")
        else:
            print("Table users already exists.")

if __name__ == "__main__":
    migrate()
