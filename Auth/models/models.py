from fastapi import Depends
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from Auth.validators.validators import (
    EmailValidator,
    PasswordValidator,
    RoleChoices,
)


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    is_active: bool
    role: RoleChoices


class GetUser(UserCreate):
    email: EmailStr
