import cv2
import json
import os
import numpy as np

points = []

# 캘리브레이션 좌표 저장 파일
CALIB_FILE = "calibration_points.json"


def mouse(event, x, y, flags, param):
    global points

    # 마우스 왼쪽 클릭 시 좌표 저장
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"{len(points)}번째 점 선택: ({x}, {y})")


def save_points(points):
    # 좌표 저장
    with open(CALIB_FILE, "w") as f:
        json.dump(points, f)


def load_points():
    # 저장된 좌표 불러오기
    if not os.path.exists(CALIB_FILE):
        return None

    try:
        with open(CALIB_FILE, "r") as f:
            loaded = json.load(f)

        loaded = [tuple(p) for p in loaded]

        if validate_points(loaded):
            return loaded
        else:
            print("저장된 캘리브레이션 좌표가 유효하지 않습니다.")

    except Exception as e:
        print("캘리브레이션 파일 로드 실패:", e)

    return None


def validate_points(points):
    # 4점 검증
    if len(points) != 4:
        print("4점을 모두 선택해야 합니다.")
        return False

    pts = np.array(points, dtype=np.float32)

    area = cv2.contourArea(pts)

    if area < 5000:
        print("선택한 영역이 너무 작습니다.")
        return False

    if not cv2.isContourConvex(pts):
        print("4점이 올바른 사각형 형태가 아닙니다.")
        return False

    tl, tr, br, bl = points

    # 점 순서 검증
    if not (tl[0] < tr[0]):
        print("2번째 점은 1번째 점보다 오른쪽에 있어야 합니다.")
        return False

    if not (br[1] > tr[1]):
        print("3번째 점은 2번째 점보다 아래쪽에 있어야 합니다.")
        return False

    if not (bl[0] < br[0]):
        print("4번째 점은 3번째 점보다 왼쪽에 있어야 합니다.")
        return False

    return True


def draw_points(frame, points):
    temp = frame.copy()

    # 선택한 점 화면에 표시
    for idx, p in enumerate(points):
        cv2.circle(temp, p, 5, (0, 255, 0), -1)
        cv2.putText(
            temp,
            str(idx + 1),
            (p[0] + 8, p[1] - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # 4점 연결
    if len(points) == 4:
        pts = np.array(points, dtype=np.int32)
        cv2.polylines(temp, [pts], True, (0, 255, 255), 2)

    return temp


def calibrate(cap):
    global points

    # 저장된 좌표 자동 로드
    saved_points = load_points()

    if saved_points is not None:
        print("저장된 캘리브레이션 좌표를 불러왔습니다.")
        return saved_points

    points = []

    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse)

    print("저장된 캘리브레이션 파일이 없습니다.")
    print("피아노 건반 영역의 4점을 순서대로 클릭하세요.")
    print("순서: 왼쪽 위 → 오른쪽 위 → 오른쪽 아래 → 왼쪽 아래")
    print("R: 다시 선택, ESC: 종료")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("프레임 읽기 실패")
            break

        temp = draw_points(frame, points)

        cv2.imshow("Calibration", temp)

        key = cv2.waitKey(1) & 0xFF

        # ESC 종료
        if key == 27:
            points = []
            break

        # R 키로 다시 선택
        if key == ord('r') or key == ord('R'):
            points = []
            print("점을 다시 선택합니다.")

        # 4점 선택 완료 시 검증 후 저장
        if len(points) == 4:
            if validate_points(points):
                save_points(points)
                print("캘리브레이션 좌표를 저장했습니다.")
                break
            else:
                print("잘못된 4점입니다. R을 눌러 다시 선택하세요.")

    cv2.destroyWindow("Calibration")
    return points