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

# Changed from 24 hours to 30 days (60 minutes * 24 hours * 30 days)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  

# Password hashing context using bcrypt
pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ... (Keep your hash_password, verify_password, and create_access_token functions exactly the same below this)


def hash_password(password: str) -> str:
    """Hashes a plain text password."""
    return pw_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a stored hash."""
    return pw_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)