import pika
import sys
import os
import json
import csv
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from datetime import datetime, timezone 

def main():
    load_dotenv()

    es = Elasticsearch(
        os.getenv("ES_HOST"),
        basic_auth=(
            os.getenv("ES_USERNAME"),
            os.getenv("ES_PASSWORD")
        ),
        verify_certs=False,
        ssl_show_warn=False,
        request_timeout=30
    )

    if not es.ping():
        raise ConnectionError("Cannot reach Elasticsearch cluster")
    print("[✓] Connected to Elasticsearch")

    INDEX_NAME = "joycon_telemetry"

    if not es.indices.exists(index=INDEX_NAME):
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,       # fine for dev; raise in prod
            },
            "mappings": {
                "properties": {
                    "song_name": {"type": "keyword"},          # exact-match filtering
                    "timestamp": {"type": "date"},             # ISO-8601 or epoch_millis
                    "ax":        {"type": "float"},            # accelerometer x
                    "ay":        {"type": "float"},            # accelerometer y
                    "az":        {"type": "float"},            # accelerometer z
                    "gx":        {"type": "float"},            # gyroscope x
                    "gy":        {"type": "float"},            # gyroscope y
                    "gz":        {"type": "float"},            # gyroscope z
                    "la":        {"type": "float"},            # linear acceleration
                    "rs":        {"type": "float"},            # rotation speed
                    "tp":        {"type": "float"},            # temperature
                    "ingested_at": {"type": "date"},           # when ES received it
                }
            }
        }



    def callback(ch, method, properties, body):
        data = json.loads(body)

        document = {
            "song_name": data["song_name"],
            "timestamp": data["timestamp"],
            "ax":        data["ax"],
            "ay":        data["ay"],
            "az":        data["az"],
            "gx":        data["gx"],
            "gy":        data["gy"],
            "gz":        data["gz"],
            "la":        data["la"],
            "rs":        data["rs"],
            "tp":        data["tp"],
            "ingested_at": datetime.now(timezone.utc).isoformat(),   # extra metadata
        }

        response = es.index(index=INDEX_NAME, document=document)
        print(f"  → indexed doc  id={response['_id']}  result={response['result']}")

    credentials = pika.PlainCredentials(os.getenv("USERNAME"), os.getenv("PASSWORD"))
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                                        host=os.getenv("HOST_NAME"),
                                        port=os.getenv("PORT"),
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