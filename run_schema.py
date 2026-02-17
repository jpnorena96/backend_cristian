
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def run_schema():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        
        with open('schema.sql', 'r') as f:
            schema = f.read()
            
        # Split by ; and execute each command
        commands = schema.split(';')
        for command in commands:
            if command.strip():
                cursor.execute(command)
                
        connection.commit()
        print("Schema executed successfully.")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_schema()
