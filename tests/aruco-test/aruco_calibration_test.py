import cv2
import numpy as np
import json

# 캘리브레이션 좌표 저장 파일
CALIB_FILE = "aruco_calibration_points.json"

# 노트북 카메라 열기
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# ArUco 마커 검출기 설정
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)


def save_points(points):
    # numpy int 타입을 JSON 저장 가능한 int 타입으로 변환
    serializable_points = [
        [int(x), int(y)] for x, y in points
    ]

    with open(CALIB_FILE, "w") as f:
        json.dump(serializable_points, f)


def detect_points(frame):
    # 현재 프레임에서 ArUco 마커 검출
    corners, ids, _ = detector.detectMarkers(frame)

    if ids is None:
        return None

    marker_centers = {}

    # 각 마커의 중심 좌표 계산
    for marker_corner, marker_id in zip(corners, ids.flatten()):
        pts = marker_corner[0]
        center = pts.mean(axis=0).astype(int)
        marker_centers[int(marker_id)] = tuple(center)

    required_ids = [0, 1, 2, 3]

    # ID 0,1,2,3이 모두 검출되어야 캘리브레이션 가능
    if not all(i in marker_centers for i in required_ids):
        return None

    # 마커 ID 순서대로 4점 정렬
    points = [
        marker_centers[0],  # 왼쪽 위
        marker_centers[1],  # 오른쪽 위
        marker_centers[2],  # 오른쪽 아래
        marker_centers[3],  # 왼쪽 아래
    ]

    return points


def draw_points(frame, points):
    # 검출된 마커 중심점과 사각형 표시
    display = frame.copy()

    if points is None:
        return display

    for idx, p in enumerate(points):
        cv2.circle(display, p, 6, (0, 255, 0), -1)
        cv2.putText(
            display,
            f"ID {idx}",
            (p[0] + 10, p[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    pts = np.array(points, dtype=np.int32)
    cv2.polylines(display, [pts], True, (0, 255, 255), 2)

    return display


while True:
    ret, frame = cap.read()

    if not ret:
        print("프레임 읽기 실패")
        break

    # 매 프레임마다 마커 4개 검출
    points = detect_points(frame)

    display = draw_points(frame, points)

    if points is not None:
        cv2.putText(
            display,
            "Calibration OK - Press ENTER to save",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )
    else:
        cv2.putText(
            display,
            "Show markers ID 0,1,2,3",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow("ArUco Calibration Test", display)

    key = cv2.waitKey(1) & 0xFF

    # ESC 종료
    if key == 27:
        break

    # ENTER 입력 시 현재 좌표 저장
    if key == 13 and points is not None:
        save_points(points)
        print("캘리브레이션 좌표 저장 완료")
        print(points)
        break

cap.release()
cv2.destroyAllWindows()