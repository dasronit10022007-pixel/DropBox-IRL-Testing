import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Pull the secure key from .env (with a fallback just in case it fails to load)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-do-not-use-in-prod")
ALGORITHM = "HS256"

# 30 days expiration (60 minutes * 24 hours * 30 days)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  

# Password hashing context using bcrypt
pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Explicitly truncate to 72 characters to bypass the strict bcrypt 4.0.0+ length bug
    truncated_password = password[:72]
    return pw_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate the incoming plain password to match the hashing logic
    truncated_password = plain_password[:72]
    return pw_context.verify(truncated_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt