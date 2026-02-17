import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

try:
    print(f"Connecting to MySQL at {DB_HOST} with user {DB_USER}...")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database '{DB_NAME}' created or already exists.")
    
    # Select DB to verify access
    connection.select_db(DB_NAME)
    print("Successfully connected and selected database.")

    connection.close()
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    print("Please ensure MySQL is running and credentials in .env are correct.")
