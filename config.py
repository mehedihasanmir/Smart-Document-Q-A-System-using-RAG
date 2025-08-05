# config.py
import os
from dotenv import load_dotenv

# .env ফাইল থেকে এনভায়রনমেন্ট ভেরিয়েবল লোড করে
load_dotenv()

class Settings:
    """Stores all configuration settings for the application."""
    # .env ফাইল থেকে GEMINI_API_KEY লোড করে
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # এমবেডিং মডেলের নাম
    EMBEDDING_MODEL: str = 'all-MiniLM-L6-v2'
    
    # জেমিনি মডেলের জন্য API URL
    GEMINI_API_URL: str = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# পুরো অ্যাপ জুড়ে ব্যবহারের জন্য সেটিংসের একটি ইনস্ট্যান্স তৈরি করা
settings = Settings()

# যদি API key খুঁজে না পাওয়া যায় তবে একটি এরর দেখানো
if not settings.GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")