
import csv
import time
import serial
import math

SERIAL_PORT = 'COM3'   
BAUDRATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

def send_angles(angles):
    cmd = "S:" + ",".join(str(int(a)) for a in angles) + "\n"
    ser.write(cmd.encode())

def prompt_record(filename="calib_data.csv"):
    print("Calibration tool")
    print("Enter entries as: angle1,angle2,angle3,angle4,angle5,angle6  OR 'q' to quit")
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["a1","a2","a3","a4","a5","a6","x_mm","y_mm","z_mm","note"])
        while True:
            s = input("Angles (or q): ").strip()
            if s.lower() == 'q':
                break
            parts = s.split(',')
            if len(parts) < 6:
                print("need 6 comma-separated angles")
                continue
            angles = [int(p) for p in parts[:6]]
            send_angles(angles)
            print("Sent angles. Wait for arm to settle...")
            time.sleep(1.0)
          
            x = input("Measured X (mm): ")
            y = input("Measured Y (mm): ")
            z = input("Measured Z (mm): ")
            note = input("Note: ")
            writer.writerow(angles + [x,y,z,note])
            print("Recorded.")
    print("Calibration finished.")

if __name__ == "__main__":
    prompt_record()
    ser.close()
