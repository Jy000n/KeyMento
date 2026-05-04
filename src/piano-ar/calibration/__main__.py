import cv2
import numpy as np

from .calibration import KeyboardCalibrator
from .compute import is_black, note_name

_SAVE_PATH = "data/calibration.json"
_WINDOW = "Calibration Test"


def _draw_labels(frame, key_regions: dict) -> None:
    for note, pts in key_regions.items():
        cx = sum(p[0] for p in pts) // 4
        cy = sum(p[1] for p in pts) // 4
        color = (80, 80, 255) if is_black(note) else (255, 220, 0)
        cv2.putText(frame, note_name(note), (cx - 12, cy + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)


def _draw_hud(frame, highlight: set, white_notes: list) -> None:
    lines = [
        "A: 전체 토글  C: 재캘리브레이션  S: 저장  Q: 종료",
        "  ".join(f"{i+1}={note_name(n)}" for i, n in enumerate(white_notes[:7])),
    ]
    for i, text in enumerate(lines):
        cv2.putText(frame, text, (16, 32 + i * 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)


def main() -> int:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("웹캠을 열 수 없습니다")
        return 1

    calib = KeyboardCalibrator(num_white_keys=14, start_note=60)

    if calib.load(_SAVE_PATH):
        print("기존 캘리브레이션 로드됨 — C를 누르면 재캘리브레이션")
    else:
        print("저장된 캘리브레이션 없음 — 4점을 클릭해 주세요")
        if not calib.calibrate(cap):
            cap.release()
            return 1
        calib.save(_SAVE_PATH)

    white_notes = sorted(n for n in calib.key_regions if not is_black(n))
    highlight: set = set()

    print("\n[테스트 모드]")
    print("  A: 전체 토글  |  1~7: 흰건 토글  |  C: 재캘리브레이션  |  S: 저장  |  Q: 종료\n")

    cv2.namedWindow(_WINDOW)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = calib.draw_keys(frame, highlight)
        _draw_labels(result, calib.key_regions)
        _draw_hud(result, highlight, white_notes)

        cv2.imshow(_WINDOW, result)
        key = cv2.waitKey(1) & 0xFF

        try:
            closed = cv2.getWindowProperty(_WINDOW, cv2.WND_PROP_VISIBLE) < 1
        except cv2.error:
            closed = True
        if closed or key == ord('q'):
            break

        if key in (ord('a'), ord('A')):
            highlight = set() if highlight else set(calib.key_regions)
        elif key in (ord('c'), ord('C')):
            if calib.calibrate(cap):
                calib.save(_SAVE_PATH)
                white_notes = sorted(n for n in calib.key_regions if not is_black(n))
                highlight.clear()
        elif key in (ord('s'), ord('S')):
            calib.save(_SAVE_PATH)
        elif ord('1') <= key <= ord('7'):
            idx = key - ord('1')
            if idx < len(white_notes):
                highlight ^= {white_notes[idx]}

    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
