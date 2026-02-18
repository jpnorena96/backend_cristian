
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client (DeepSeek Compatible)
api_key = os.getenv("DEEPSEEK_API_KEY") # Prioritize DeepSeek
if not api_key:
    api_key = os.getenv("OPENAI_API_KEY")
    BASE_URL = None
    MODEL_NAME = "gpt-3.5-turbo"
else:
    BASE_URL = "https://api.deepseek.com"
    MODEL_NAME = "deepseek-chat"

print(f"Testing DeepSeek...")
print(f"API Key: {api_key[:5]}...{api_key[-4:]}")
print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL_NAME}")

client = openai.OpenAI(api_key=api_key, base_url=BASE_URL)

try:
    response = client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {"role": "user", "content": "Hola"}
        ],
        temperature=0.3,
    )
    print("SUCCESS:", response.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)
