from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Migrating database...")
    try:
        # Check if column exists, if not add it
        # This is a bit hacky specifically for SQLite/MySQL duality without Alembic
        # Attempting to add column. If it fails, likely exists.
        with db.engine.connect() as conn:
            # Determine DB type
            if 'sqlite' in str(db.engine.url):
                print("Detected SQLite.")
                # SQLite doesn't support IF NOT EXISTS in ADD COLUMN easily in all versions, 
                # but simplest way is catch the error
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                except Exception as e:
                    print(f"Column likely exists: {e}")
            else:
                print("Detected MySQL/Postgres.")
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
                except Exception as e:
                    print(f"Column likely exists: {e}")
            
            conn.commit()
            print("Migration attempt complete.")

    except Exception as e:
        print(f"Migration error: {e}")
