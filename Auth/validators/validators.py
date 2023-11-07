from Auth.database import MongoDBManager
from enum import Enum
from fastapi import HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


def get_collection():
    with MongoDBManager() as db_manager:
        user_collection = db_manager.auth
        return user_collection


class EmailValidator(BaseModel):
    email: EmailStr = Field(
        alias="email",
        title="email",
        placeholder="something@something.com",
        description="Email of the user",
        min_length=8,
        max_length=32,
    )

    @field_validator("email")
    def validate_email(cls, email):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        is_valid = re.match(email_regex, email)
        if not is_valid:
            raise HTTPException(status_code=422, detail="Invalid email format")
        cls.is_unique(email)
        return email

    @classmethod
    def is_unique(cls, email):
        pipeline = [
            {"$match": {"email": email}},
            {
                "$group": {"_id": None, "count": {"$sum": 1}},
            },
        ]

        result = list(get_collection().aggregate(pipeline))

        if result and result[0]["count"] > 0:
            raise HTTPException(status_code=422, detail="Email already exists")
        return email


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordValidator(BaseModel):
    password: str = Field(
        alias="password",
        title="Password",
        description="User's password",
        min_length=8,
        max_length=32,
    )

    @field_validator("password")
    def validate_email(cls, password):
        password_regex = r"^(?=.*\d)(?=.*[a-z])(?=.*[@$!%*?&])(?=.*[A-Z]).{8,32}$"
        is_valid = re.match(password_regex, password)
        if not is_valid:
            raise HTTPException(status_code=422, detail="Invalid password format")
        return cls.hash_password(password)

    @classmethod
    def hash_password(cls, password: str):
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed_password: str):
        return pwd_context.verify(password, hashed_password)


class RoleChoices(str, Enum):
    admin = "admin"
    staff = "staff"
    guest = "guest"
