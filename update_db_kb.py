from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Migrating database for Knowledge Base...")
    try:
        # Create table if it doesn't exist.
        # SQLAlchemy create_all is safe, it only creates missing tables.
        db.create_all()
        print("Database tables updated (KnowledgeBase added if missing).")

    except Exception as e:
        print(f"Migration error: {e}")
