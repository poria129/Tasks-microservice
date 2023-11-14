from pydantic import BaseModel, EmailStr
from Auth.validators.validators import EmailValidator, PasswordValidator, RoleChoices


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    is_active: bool
    role: RoleChoices


class GetUser(UserCreate):
    email: EmailStr


class EditUser(UserCreate):
    email: EmailStr
