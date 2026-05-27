import cv2
import os

SAVE_DIR = "markers"
os.makedirs(SAVE_DIR, exist_ok=True)

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

for marker_id in range(4):
    marker = cv2.aruco.generateImageMarker(
        aruco_dict,
        marker_id,
        400
    )

    filename = os.path.join(SAVE_DIR, f"marker_{marker_id}.png")
    cv2.imwrite(filename, marker)
    print(f"Saved: {filename}")