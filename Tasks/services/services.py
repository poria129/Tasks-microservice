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
    channel.queue_declare(queue="jwt_queue", durable=True)

    def callback(ch, method, properties, body):
        global user
        # print(f"Received JWT: {body}")
        user = get_current_user(body)
        # print(f"{user}")
        return user

    channel.basic_consume(
        queue="jwt_queue", on_message_callback=callback, auto_ack=True
    )

    print("Waiting for JWT. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        receive_jwt_from_rabbitmq()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
