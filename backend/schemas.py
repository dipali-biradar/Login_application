from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterUser(BaseModel):
    first_name: str
    middle_name: str = ""
    last_name: str

    email: EmailStr

    mobile: str 
    password: str = Field(
        min_length=8
    )


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str

    new_password: str = Field(
        min_length=8
    )


class UpdateUser(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    # role: Optional[str] = None