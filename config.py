# GEMINI_API_KEY = "AIzaSyCHQ1MN7eASdfkiHEqIZ6CAdDBJj8GF4C8"
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get API Key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Raise an error if the key is missing
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing! Check your .env file.")
