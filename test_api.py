import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_api():
    # 1. Login
    print("Testing Login...")
    try:
        res = requests.post(f"{BASE_URL}/login", json={"email": "admin@legaltech.com", "password": "admin"})
        if res.status_code == 200:
            user_data = res.json()
            print("Login Success:", user_data)
            user_id = user_data['user']['id']
        else:
            print("Login Failed:", res.text)
            return
    except Exception as e:
        print(f"Login Exception: {e}")
        return

    # 2. Chat
    print("\nTesting Chat...")
    try:
        res = requests.post(f"{BASE_URL}/chat", json={"userId": user_id, "message": "Hola, necesito un contrato laboral"})
        if res.status_code == 200:
            chat_data = res.json()
            print("Chat Response:", chat_data)
        else:
            print("Chat Failed:", res.text)
    except Exception as e:
        print(f"Chat Exception: {e}")

if __name__ == "__main__":
    test_api()
