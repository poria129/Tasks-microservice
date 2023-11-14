from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from Tasks.services.services import receive_jwt_from_rabbitmq


SECRET_KEY = "0a98f67bb9f7c4e68d6f7e68d561c9f4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(token: str = Depends(receive_jwt_from_rabbitmq)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        id: str = payload.get("id")
        role: str = payload.get("role")
        if email is None or id is None or role is None:
            raise credentials_exception
        return {"email": email, "id": id, "role": role}
    except JWTError:
        raise credentials_exception


def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    return current_user


def get_current_staff_user(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Permission denied")
    return current_user
