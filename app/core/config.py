import os
from dotenv import load_dotenv

CORS_ORIGIN = [
    "http://localhost:3000",
    "localhost:3000"
]

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


