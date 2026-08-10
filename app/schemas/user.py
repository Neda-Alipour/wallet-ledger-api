from pydantic import BaseModel, EmailStr

class UserRead(BaseModel):
    email: EmailStr