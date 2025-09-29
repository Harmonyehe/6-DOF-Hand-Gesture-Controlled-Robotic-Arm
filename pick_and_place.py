
import time
import serial
from object_detection import detect_objects
import cv2
from your_ik_module import image_to_world, inverse_kinematics, send_angles  # reuse from main.py

SERIAL_PORT = 'COM3'
BAUDRATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

CAM = cv2.VideoCapture(0)

PICK_CLASS = "bottle"   # change to your object
PLACE_POSE = [120, 0, 80]  # x,y,z in mm - where to put object
HOME_ANGLES = [90,90,90,90,90,10]

def pick_and_place_cycle():
    # 1) search for object
    found = False
    target_world = None
    start = time.time()
    while time.time() - start < 10:  # scan for 10s
        ret, frame = CAM.read()
        if not ret: break
        dets = detect_objects(frame)
        for d in dets:
            if d['class'] == PICK_CLASS:
                cx, cy = d['centroid']
                # Convert image centroid to world coords:
                world = image_to_world(cx, cy, frame)  # implement camera intrinsics mapping
                target_world = world
                found = True
                break
        if found:
            break

    if not found:
        print("No object found")
        return False

    # 2) compute pre-pick pose (above object)
    px, py, pz = target_world
    prepick = [px, py, pz + 40]  # hover 40mm above
    pick_angles = inverse_kinematics(px, py, pz)
    prepick_angles = inverse_kinematics(prepick[0], prepick[1], prepick[2])

    # 3) move to prepick
    send_angles(ser, prepick_angles); time.sleep(1.0)
    # 4) move down and grip
    send_angles(ser, pick_angles); time.sleep(0.8)
    # close gripper
    pick_angles[5] = 70
    send_angles(ser, pick_angles); time.sleep(0.5)
    # 5) lift
    send_angles(ser, prepick_angles); time.sleep(0.8)
    # 6) move to place
    place_angles = inverse_kinematics(*PLACE_POSE)
    send_angles(ser, place_angles); time.sleep(1.0)
    # 7) open gripper
    place_angles[5] = 10
    send_angles(ser, place_angles); time.sleep(0.5)
    # 8) return home
    send_angles(ser, HOME_ANGLES); time.sleep(1.0)
    return True

if __name__ == "__main__":
    while True:
        ok = pick_and_place_cycle()
        print("Cycle result:", ok)
        time.sleep(1)
