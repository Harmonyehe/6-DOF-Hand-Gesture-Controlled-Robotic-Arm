
import cv2
import numpy as np
import time

PROTOTXT = "MobileNetSSD_deploy.prototxt"
MODEL = "MobileNetSSD_deploy.caffemodel"

CLASSES = ["background","aeroplane","bicycle","bird","boat",
           "bottle","bus","car","cat","chair","cow","diningtable",
           "dog","horse","motorbike","person","pottedplant","sheep",
           "sofa","train","tvmonitor"] 

NET = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

def detect_objects(frame, conf_threshold=0.5):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843,
                                 (300, 300), 127.5)
    NET.setInput(blob)
    detections = NET.forward()
    results = []
    for i in range(detections.shape[2]):
        conf = float(detections[0, 0, i, 2])
        if conf > conf_threshold:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            cx = int((startX + endX) / 2)
            cy = int((startY + endY) / 2)
            results.append({
                "class": CLASSES[idx] if idx < len(CLASSES) else str(idx),
                "conf": conf,
                "bbox": (startX, startY, endX, endY),
                "centroid": (cx, cy)
            })
    return results

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret: break
        res = detect_objects(frame, conf_threshold=0.6)
        for r in res:
            (sx, sy, ex, ey) = r["bbox"]
            cv2.rectangle(frame, (sx, sy), (ex, ey), (0,255,0), 2)
            cv2.circle(frame, r["centroid"], 5, (0,0,255), -1)
            cv2.putText(frame, f"{r['class']}:{r['conf']:.2f}", (sx, sy-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.imshow("Det", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
