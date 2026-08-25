import pika
import sys
import os
import json
import csv

def main():
    filename = "telemetry_logs.csv"
    header = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "la", "rs"] # row headers

    with open(filename, mode="a", newline="", encoding="utf8") as f: # utf-8 supports universal characters
            writer = csv.writer(f) # Write data directly to csv file
    
            if os.stat(filename).st_size == 0: # If file is empty, write the row headers, stat - status
                writer.writerow(header)


    def callback(ch, method, properties, body):
        data = json.loads(body)

        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            
            writer.writerow([
                 data["timestamp"],
                 data["ax"],
                 data["ay"],
                 data["az"],
                 data["gx"],
                 data["gy"],
                 data["gz"],
                 data["la"],
                 data["rs"]
            ])

    credentials = pika.PlainCredentials('swetha', 'Kitty123!!')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',
                                        port = 5672,
                                        virtual_host= '/',
                                        credentials=credentials))
    channel = connection.channel()

    channel.basic_consume(queue='joycon_telemetry',
                        auto_ack=True,
                        on_message_callback=callback)    

    print(' [*] Waiting for joycon data. To exit press CTRL+C')
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