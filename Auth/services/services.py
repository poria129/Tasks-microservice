import pika
from fastapi import BackgroundTasks


def send_jwt_through_rabbitmq(access_token: str, background_tasks: BackgroundTasks):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_delete(queue="jwt_queue")
    channel.queue_declare(queue="jwt_queue", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="jwt_queue",
        body=access_token,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ),
    )

    connection.close()
