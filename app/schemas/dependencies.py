from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginSchema, SignupSchema


# Define a reusable type
signup_dependency = Annotated[SignupSchema, Depends(SignupSchema.as_form)] 
login_dependency = Annotated[LoginSchema, Depends(LoginSchema.as_form)] 

db_dependency = Annotated[Session, Depends(get_db)]