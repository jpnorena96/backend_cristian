import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def update_schema():
    print(f"Connecting to {DB_NAME} at {DB_HOST}...")
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        
        # Check if columns exist
        cursor.execute("SHOW COLUMNS FROM users LIKE 'is_approved'")
        if not cursor.fetchone():
            print("Adding is_approved column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT FALSE")
        else:
            print("Column is_approved already exists.")

        cursor.execute("SHOW COLUMNS FROM users LIKE 'is_admin'")
        if not cursor.fetchone():
            print("Adding is_admin column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
        else:
            print("Column is_admin already exists.")
            
        connection.commit()
        print("Schema update complete.")
        connection.close()
        
    except Exception as e:
        print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
