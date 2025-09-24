from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt, os

pwd = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET = os.environ.get("SECRET_KEY", "devsecret")
ALGO = "HS256"

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd.verify(password, hashed)

def make_token(sub: int, role: str, hours: int = 8) -> str:
    payload = {
        "sub": sub,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=hours),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)
