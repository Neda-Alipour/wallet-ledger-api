from pydantic import BaseModel, EmailStr, Field, field_validator
from fastapi import Form
import re

class AuthBase(BaseModel):
    email: EmailStr
    password: str = Field(max_length=64)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        if len(password) < 4:
            raise ValueError("Password too short (min 4 characters)")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one number")
        return password

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        password: str = Form(...)
    ):
        return cls(email=email, password=password)

class SignupSchema(AuthBase):
    """Inherits everything from AuthBase"""
    pass

class LoginSchema(AuthBase):
    """Inherits everything from AuthBase"""
    pass

# class SignupSchema(AuthBase):
#     # 1. Add the new field specific to Signup
#     user_name: str = Field(..., min_length=3, max_length=20)

#     # 2. Override as_form to include user_name
#     @classmethod
#     def as_form(
#         cls,
#         email: EmailStr = Form(...),
#         password: str = Form(...),
#         user_name: str = Form(...) # Add this parameter
#     ):
#         return cls(email=email, password=password, user_name=user_name)