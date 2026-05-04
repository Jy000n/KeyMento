import cv2

from camera.capture import open_camera
from calibration.calibrator import calibrate
from utils.transform import get_matrix, warp
from keyboard.mapping import build_keys


cap = open_camera()

points = calibrate(cap)
matrix = get_matrix(points)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    warped = warp(frame, matrix)
    h, w = warped.shape[:2]
    whites, blacks = build_keys(w, h)

    for key in whites:
        x1, y1, x2, y2 = key
        cv2.rectangle(warped, (x1, y1), (x2, y2), (0, 255, 0), 1)

    for key in blacks:
        x1, y1, x2, y2 = key
        cv2.rectangle(warped, (x1, y1), (x2, y2), (50, 50, 50), -1)  
        cv2.rectangle(warped, (x1, y1), (x2, y2), (0, 200, 255), 1)  

    cv2.imshow("Warped", warped)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()