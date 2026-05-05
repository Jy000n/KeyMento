import cv2

points = []

def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x,y))
            
def calibrate(cap):
    global points
    points = []
    
    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("프레임 읽기 실패")
            break
        
        temp = frame.copy()
        
        for p in points:
            cv2.circle(temp, p, 5, (0,255,0), -1)
            
        cv2.imshow("Calibration", temp)
        
        if len(points) == 4:
            break
        
        if cv2.waitKey(1) == 27:
            break
        
    cv2.destroyWindow("Calibration")
    return points