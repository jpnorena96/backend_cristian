
from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'is_approved' not in columns:
                print("Adding is_approved column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT 0"))
                
                # Auto-approve existing admins and maybe existing users?
                # Let's auto-approve ALL existing users so they don't get locked out
                conn.execute(text("UPDATE users SET is_approved = 1"))
                conn.commit()
                print("Column added and existing users approved.")
            else:
                print("Column is_approved already exists.")
                
    except Exception as e:
        print(f"Error migrating database: {e}")
