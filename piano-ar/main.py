from camera.capture import open_camera

cap = open_camera()

from calibration.calibrator import calibrate

points = calibrate(cap)
print("선택된 좌표:", points)