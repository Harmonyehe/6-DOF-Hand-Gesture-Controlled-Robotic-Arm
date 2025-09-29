import cv2
import mediapipe as mp
import serial
import time
import numpy as np

arduino = serial.Serial('COM6', 9600)  
time.sleep(2)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

def send_command(motor, angle):
    command = f"{motor} {int(angle)}\n"
    arduino.write(command.encode())
    print(f"Sent: {command}")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            wrist = hand_landmarks.landmark[0]
            index_finger = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]
            middle_finger = hand_landmarks.landmark[12]

            # Convert hand positions to angles
            x_pos = int(index_finger.x * 180)  
            y_pos = int(index_finger.y * 180)  
            z_pos = int((1 - index_finger.z) * 180)  

            send_command("BASE", x_pos)
            send_command("SHOULDER", y_pos)
            send_command("ELBOW", z_pos)

            # Wrist pitch & yaw control
            pitch_angle = int(middle_finger.y * 180)
            yaw_angle = int(index_finger.x * 180)

            send_command("PITCH", pitch_angle)
            send_command("YAW", yaw_angle)

            # Gripper control based on thumb-index finger distance
            grip_distance = np.linalg.norm(
                [thumb_tip.x - index_finger.x, thumb_tip.y - index_finger.y]
            )
            if grip_distance < 0.05:
                send_command("GRIPPER", 30)  # Close
            else:
                send_command("GRIPPER", 0)  # Open

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
