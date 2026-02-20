import requests
import json
import random

def test_register():
    url = "http://localhost:5000/api/register"
    email = f"testuser_{random.randint(1000, 9999)}@example.com"
    payload = {
        "email": email,
        "password": "password123",
        "name": "Test User"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("Registration Successful!")
        elif response.status_code == 400 and "already registered" in response.text:
            print("User already registered (expected if repeated).")
        else:
            print("Registration Failed.")

    except Exception as e:
        print(f"Error connecting to API: {e}")

if __name__ == "__main__":
    test_register()
