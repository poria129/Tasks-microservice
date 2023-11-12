import pika
from fastapi import BackgroundTasks


def send_jwt_through_rabbitmq(access_token: str, background_tasks: BackgroundTasks):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.exchange_declare(exchange="auth_exchange", exchange_type="direct")
    channel.queue_declare(queue="auth_queue")
    channel.queue_bind(
        exchange="auth_exchange", queue="auth_queue", routing_key="auth_key"
    )

    channel.basic_publish(
        exchange="auth_exchange",
        routing_key="auth_key",
        body=access_token,
        properties=pika.BasicProperties(content_type="text/plain", expiration="900000"),
    )

    connection.close()
