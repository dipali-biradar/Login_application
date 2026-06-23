
from sqlalchemy.sql import func

from database import Base

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)

    full_name = Column(String(255))

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    mobile = Column(String(20))

    password_hash = Column(String(255), nullable=False)

    role = Column(String(50), default="user")
    status = Column(String, default="active")
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)

    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    last_login_at = Column(DateTime(timezone=True), nullable=True)
























# from pydantic import BaseModel

# class RegisterUser(BaseModel):
#     first_name: str
#     middle_name: str = ""
#     last_name: str
#     email: str
#     mobile: str
#     password: str


# class LoginUser(BaseModel):
#     email: str
#     password: str

# class ForgotPasswordRequest(BaseModel):
#     email: str


# class ResetPasswordRequest(BaseModel):
#     token: str
#     new_password: str
    