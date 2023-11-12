import os
import sys
from fastapi import HTTPException, status, Depends
from jose import jwt, JWSError
import pika

import main


SECRET_KEY = "0a98f67bb9f7c4e68d6f7e68d561c9f4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(token: str):
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


def receive_jwt_from_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="auth_queue")

    method_frame, header_frame, body = channel.basic_get(queue="auth_queue")
    if method_frame:
        channel.basic_ack(method_frame.delivery_tag)
        jwt = body.decode("utf-8")
        content_type = header_frame.content_type
        expiration = header_frame.expiration
    else:
        jwt = None

    connection.close()

    return get_current_user(jwt)
