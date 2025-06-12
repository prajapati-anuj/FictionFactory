import os
from dotenv import load_dotenv

load_dotenv()  # ✅ Load environment variables right here

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
print("Loaded GEMINI_API_KEY in config.py:", GEMINI_API_KEY)  # Optional debug
