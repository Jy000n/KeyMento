import cv2
from camera.capture import open_camera

cap = open_camera()

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("프레임 읽기 실패")
        break
    
    cv2.imshow('Camera Test', frame)
    
    if cv2.waitKey(1) == 27:  # ESC 키를 누르면 종료
        break
    
cap.release()
cv2.destroyAllWindows()