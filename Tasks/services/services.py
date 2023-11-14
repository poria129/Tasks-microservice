import pika


def receive_jwt_from_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="auth_queue")

    method_frame, header_frame, body = channel.basic_get(queue="auth_queue")
    if method_frame:
        # channel.basic_ack(method_frame.delivery_tag)
        jwt = body.decode("utf-8")
        content_type = header_frame.content_type
        expiration = header_frame.expiration
    else:
        jwt = None

    connection.close()

    return jwt
