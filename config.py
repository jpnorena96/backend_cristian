import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')

    if db_user and db_host and db_name:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password or ''}@{db_host}/{db_name}"
    else:
        # Fallback to SQLite for development/testing if MySQL vars are missing
        print("WARNING: MySQL variables not found. Using SQLite fallback.")
        base_dir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Fix for MySQL server has gone away
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
