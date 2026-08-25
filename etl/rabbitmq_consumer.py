import pika
import sys
import os

def main():
    # connection
    credentials = pika.PlainCredentials('swetha', 'Kitty123!!')

    # connection = pika.BlockingConnection(pika.ConnectionParameters(parameters))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',
                                        port = 5672,
                                        virtual_host= '/',
                                        credentials=credentials))
    channel = connection.channel()

    # decleare queue
    # channel.queue_declare(queue='joycon', durable=True, arguments={'x-queue-type': 'classic'})

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue='joycon',
                        auto_ack=True,
                        on_message_callback=callback)    


    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)