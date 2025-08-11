from dotenv import load_dotenv
import os

load_dotenv()

# Please create a .env file in the root of the project and add the following variables:
# SECRET_KEY=your-secret-key
# ACCESS_TOKEN_EXPIRE_MINUTES=30 (in minutes)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

CORS_ORIGIN = [
    "http://localhost:3000",
    "localhost:3000",
    "https://todo-list-web.vercel.app",
]
