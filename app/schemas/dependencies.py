from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginSchema, SignupSchema

from app.services.auth import AuthService

DatabaseDep = Annotated[Session, Depends(get_db)]

def get_auth_service(db: DatabaseDep):
    return AuthService(db)

# why Annotated not just Session = Depends(get_db)? because we want to specify the type of db parameter as Session for better type hinting and editor support 

# Define a reusable type
SignupDep = Annotated[SignupSchema, Depends(SignupSchema.as_form)] 
LoginDep = Annotated[LoginSchema, Depends(LoginSchema.as_form)] 

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]