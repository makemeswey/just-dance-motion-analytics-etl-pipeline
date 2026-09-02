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

        es.indices.create(index=INDEX_NAME, body=mapping)



    def callback(ch, method, properties, body):
        data = json.loads(body)

        song_name = data.get("song_name", "Unknown")
        timestamp = data.get("timestamp")

        print(f"Received song_name: '{data.get('song_name')}' | timestamp: {data.get('timestamp')}")

        document = {
                "song_name": song_name,
                "timestamp": timestamp,
                "ax":        data.get("ax", 0.0),
                "ay":        data.get("ay", 0.0),
                "az":        data.get("az", 0.0),
                "gx":        data.get("gx", 0.0),
                "gy":        data.get("gy", 0.0),
                "gz":        data.get("gz", 0.0),
                "la":        data.get("la", 0.0),
                "rs":        data.get("rs", 0.0),
                "tp":        data.get("tp", 0.0),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
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

    channel.queue_purge(queue='joycon_telemetry')
    print("[✓] Queue purged of legacy messages.")

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