from pyjoycon import JoyCon, get_R_id
import time
import keyboard
import csv
import os

# Helper function to calculate vector magnitude rounded to 4dp
def calc_vector_magnitude(x,y,z):
    return round((x*x + y*y + z*z) ** 0.5, 4)

def get_joycon_acc_gyro():
    filename = "continuous_log.csv"
    header = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "la", "rs"] # row headers

    with open(filename, mode="a", newline="", encoding="utf8") as f: # utf-8 supports universal characters
        writer = csv.writer(f) # Write data directly to csv file

        if os.stat(filename).st_size == 0: # If file is empty, write the row headers, stat - status
            writer.writerow(header)
            f.flush() # Forces from memory buffers to immedieately write into disk or output stream

        try:

            joycon_id = get_R_id() # gets ID of right joycon
            joycon = JoyCon(*joycon_id) # Passes joycon id to JoyCon class as a dict

            while True:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S") # Shows current day and time

                status = joycon.get_status() # Get joycon status values as dict
                accel = status.get('accel', {}) # Extract acceleration from dict
                gyro = status.get('gyro', {}) # Extract gyro from dict

                data_row = [
                        current_time, 
                        round(accel.get('x')/4096,4), 
                        round(accel.get('y')/4096, 4), 
                        round(accel.get('z')/4096, 4), 
                        round(gyro.get('x')/4096, 4), 
                        round(gyro.get('y')/4096, 4), 
                        round(gyro.get('z')/4096, 4), 
                        calc_vector_magnitude(accel.get('x')/4096, accel.get('y')/4096, accel.get('z')/4096), 
                        calc_vector_magnitude(gyro.get('x')/4096, gyro.get('y')/4096, gyro.get('z')/4096)
                    ]

                writer.writerow(data_row) # Write data as a row in csv
                f.flush()

                # print("JOY-CON READINGS")

                # Print out values on terminal
                # print(f"Accelerometer: X={accel.get('x')}, Y={accel.get('y')}, Z={accel.get('z')}")
                # print(f"Gyroscope: X={gyro.get('x')}, Y={gyro.get('y')}, Z={gyro.get('z')}")
                # print(f"Linear Acceleration: {calc_vector_magnitude(accel.get('x'), accel.get('y'), accel.get('z'))}")
                # print(f"Rotational Speed: {calc_vector_magnitude(gyro.get('x'), gyro.get('y'), gyro.get('z'))}")

                # print("\n")
                # if keyboard.is_pressed("q"):
                #     break

                time.sleep(0.1) # Wait 0.1s 

        except ValueError:
            print("Joycon not found")

if __name__ == "__main__":
    get_joycon_acc_gyro()
