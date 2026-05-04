import cv2

from camera.capture import open_camera
from calibration.calibrator import calibrate
from utils.transform import get_matrix, warp
from keyboard.mapping import build_keys
from ar.overlay import render

# 카메라 (camera)
cap = open_camera()

# 캘리브레이션 (calibration)
points = calibrate(cap)

# 변환 행렬 (transform)
matrix = get_matrix(points)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 키보드 정면화 (transform)
    warped = warp(frame, matrix)
    
    # 키 생성 (keyboard)
    h, w = warped.shape[:2]
    whites, blacks = build_keys(w, h)

    for key in whites:
        x1, y1, x2, y2 = key
        cv2.rectangle(warped, (x1, y1), (x2, y2), (0, 255, 0), 1)

    for key in blacks:
        x1, y1, x2, y2 = key
        cv2.rectangle(warped, (x1, y1), (x2, y2), (50, 50, 50), -1)  
        cv2.rectangle(warped, (x1, y1), (x2, y2), (0, 200, 255), 1)  

    # AR 렌더 (ar)
    output = render(warped, whites, blacks)

    # 출력
    cv2.imshow("Piano AR", output)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()