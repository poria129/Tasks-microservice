from bson import ObjectId
from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWSError, jwt
from typing import Annotated


from database import MongoDBManager
from Auth.models.models import EditUser, UserCreate
from Auth.services.services import send_jwt_through_rabbitmq
from Auth.validators.validators import EmailValidator, PasswordValidator

router = APIRouter(prefix="/auth", tags=["auth"])


def get_collection():
    with MongoDBManager() as db_manager:
        user_collection = db_manager.auth
        return user_collection


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(email: EmailValidator, password: PasswordValidator, user: UserCreate):
    get_email = dict(email)
    get_password = dict(password)
    get_user = dict(user)

    result_dict = {**get_email, **get_password, **get_user}
    get_collection().insert_one(result_dict)


@router.get("/", status_code=status.HTTP_200_OK)
def get_users():
    pipeline = [{"$match": {}}]

    users = list(get_collection().aggregate(pipeline))

    user_list = [{**user, "_id": str(user["_id"]), "password": None} for user in users]

    return user_list


@router.put("/{id}", status_code=status.HTTP_200_OK)
def edit_user(id: str, fields: EditUser):
    try:
        result = get_collection().find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": dict(fields)}, return_document=True
        )
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: str):
    try:
        result = get_collection().find_one_and_delete({"_id": ObjectId(id)})

        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Login for JWT and dependencies

SECRET_KEY = "0a98f67bb9f7c4e68d6f7e68d561c9f4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        id: str = payload.get("id")
        role: str = payload.get("role")
        if email is None or id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate"
            )
        return {"email": email, "id": id, "role": role}
    except JWSError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate"
        )


def get_user_by_email(email: str):
    aggregation_pipeline = [{"$match": {"email": email}}]

    cursor = get_collection().aggregate(aggregation_pipeline)

    for user in cursor:
        return user

    return None


@router.post("/token", status_code=status.HTTP_200_OK)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    user = get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not PasswordValidator.verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "id": str(user["_id"]), "role": user["role"]},
        expires_delta=access_token_expires,
    )

    background_tasks.add_task(
        send_jwt_through_rabbitmq,
        access_token,
        background_tasks,
    )

    return {"access_token": access_token, "token_type": "bearer"}
