
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Override host to 127.0.0.1 for testing
DB_HOST = '127.0.0.1' 
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

try:
    print(f"Connecting to {DB_HOST} with user {DB_USER}...")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("SUCCESS: Connected with 127.0.0.1")
    connection.close()
except Exception as e:
    print(f"FAILURE: {e}")
