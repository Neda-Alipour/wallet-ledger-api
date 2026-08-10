from pydantic import BaseModel, EmailStr, Field, field_validator
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