from pyjoycon import JoyCon, get_R_id, get_L_id
import time
import os
import pika
import json
from dotenv import load_dotenv
from features import calc_rotational_speed, calc_dynamic_acc, calc_power_proxy
from datetime import datetime, timezone 

def get_joycon_details():
    load_dotenv()
    credentials = pika.PlainCredentials(os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "localhost"), 
                                                                   port=int(os.getenv("RABBITMQ_PORT", 5672)), 
                                                                   virtual_host= '/', 
                                                                   credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue="joycon_telemetry", durable=True, arguments={'x-queue-type': 'classic'})

    try:

        joycon_id = get_R_id() or get_L_id() # gets ID of right joycon or left joycon
        joycon = JoyCon(*joycon_id) # Passes joycon id to JoyCon class as a dict

        song_name = str(input("Enter song name: "))
        while True:

            status = joycon.get_status() # Get joycon status values as dict
            accel = status.get('accel', {}) # Extract acceleration from dict
            gyro = status.get('gyro', {}) # Extract gyro from dict

            current_time = datetime.now(timezone.utc).isoformat() # Shows current day and time

            ax = round(accel.get('x')/4096,4)
            ay = round(accel.get('y')/4096, 4)
            az = round(accel.get('z')/4096, 4)

            gx = round(gyro.get('x')/4096, 4)
            gy = round(gyro.get('y')/4096, 4)
            gz = round(gyro.get('z')/4096, 4)

            la = calc_dynamic_acc(ax, ay, az) # dynamic acceleration
            rs = calc_rotational_speed(gx, gy, gz) # rotational speed

            tp = round(calc_power_proxy(ax, ay, az) + calc_power_proxy(gx, gy, gz), 4) # total power 

            payload = {
                "timestamp": current_time,
                "song_name": song_name,
                "ax": ax,
                "ay": ay,
                "az": az,
                "gx": gx,
                "gy": gy,
                "gz": gz,
                "la": la,
                "rs": rs,
                "tp": tp
            }

            channel.basic_publish(
                exchange='',
                routing_key="joycon_telemetry",
                body = json.dumps(payload), # converts dict to JSON string
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                )
            )

            time.sleep(0.1) 

    except ValueError:
        print("Joycon not found")

    finally:
        connection.close()

if __name__ == "__main__":
    get_joycon_details()
