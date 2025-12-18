import os
from sqlalchemy import create_engine, text

def migrate():
    url = os.environ.get("DATABASE_URL", "postgresql+psycopg://sorftime:sorftime@db:5432/sorftime_dev")
    engine = create_engine(url)
    
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Ensure we are not in a transaction block for ALTER
        
        # Check if column exists
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='import_batches' AND column_name='file_hash';
        """)
        result = conn.execute(check_sql).fetchone()
        
        if not result:
            print("Adding file_hash column...")
            conn.execute(text("ALTER TABLE import_batches ADD COLUMN file_hash VARCHAR(64)"))
            conn.execute(text("CREATE INDEX ix_import_batches_file_hash ON import_batches (file_hash)"))
            print("Column added successfully.")
        else:
            print("Column file_hash already exists.")

if __name__ == "__main__":
    migrate()
