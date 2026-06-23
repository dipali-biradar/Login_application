import os
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User
load_dotenv()


# ---------------- JWT SETTINGS ----------------
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "SUPER_SECRET_KEY_123_CHANGE_ME_IN_PRODUCTION"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#  PASSWORD  
# Argon2 does NOT have bcrypt's 72-byte limit
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

#  PASSWORD FUNCTIONS 
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#  RANDOM TOKEN 
def generate_token() -> str:
    return secrets.token_urlsafe(32)

#  JWT CREATE 
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#  JWT DECODE 
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except JWTError as e:
        print("JWT ERROR:", str(e))
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
#  JWT SECURITY 

security = HTTPBearer()


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#  GET CURRENT USER 
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    print("TOKEN RECEIVED:", token)

    try:
        payload = decode_access_token(token)
    except Exception as e:
        print("DECODE ERROR:", e)
        raise HTTPException(401, "Token decode failed")

    email = payload.get("email")

    if not email:
        raise HTTPException(401, "Email missing in token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(401, "User not found")

    return user
#  ADMIN REQUIRED 

def admin_required(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user