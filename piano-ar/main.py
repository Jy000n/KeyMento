import cv2

from camera.capture import open_camera
from calibration.calibrator import calibrate
from utils.transform import get_matrix, warp

cap = open_camera()
points = calibrate(cap)
matrix = get_matrix(points)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    warped = warp(frame, matrix)

    cv2.imshow("Warped", warped)

    if cv2.waitKey(1) == 27:
        break