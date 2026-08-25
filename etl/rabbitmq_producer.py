import pika
from datetime import datetime
# connection
credentials = pika.PlainCredentials('swetha', 'Kitty123!!')

# connection = pika.BlockingConnection(pika.ConnectionParameters(parameters))
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',
                                       port = 5672,
                                       virtual_host= '/',
                                       credentials=credentials))
channel = connection.channel()

# decleare queue
channel.queue_declare(queue='joycon', durable=True, arguments={'x-queue-type': 'classic'})

for i in range(1, 11):
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    body = str(i) + ' - Joy con data world! - '  + formatted_date
    # print(body)
    # send message
    channel.basic_publish(exchange='', routing_key='joycon', body = body)



# print(" [x] Sent 'Joyvon World!'")

connection.close()