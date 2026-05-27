import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

while True:
    ret, frame = cap.read()

    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    corners, ids, _ = detector.detectMarkers(frame)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for marker_corner, marker_id in zip(corners, ids.flatten()):
            pts = marker_corner[0]

            center = pts.mean(axis=0).astype(int)
            cx, cy = center

            cv2.circle(frame, (cx, cy), 6, (0, 255, 0), -1)
            cv2.putText(
                frame,
                f"ID: {marker_id}",
                (cx + 10, cy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            print(f"Detected ID {marker_id} at center ({cx}, {cy})")

    cv2.imshow("ArUco Test", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()