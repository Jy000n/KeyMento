import cv2

def render(frame, whites, blacks):
    overlay = frame.copy()

    test_white = [10, 11, 12]
    test_black = [0, 1, 2]

    # 흰 건반 LED
    for i in test_white:
        x1, y1, x2, y2 = whites[i]

        cx = int((x1 + x2) / 2)
        cy = int(y1 + (y2 - y1) * 0.75)

        key_width = x2 - x1
        key_height = y2 - y1

        r = int(min(key_width, key_height) * 0.22)

        cv2.circle(overlay, (cx, cy), r, (0, 255, 0), -1)

    # 검은 건반 LED
    for i in test_black:
        x1, y1, x2, y2 = blacks[i]

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        key_width = x2 - x1
        key_height = y2 - y1

        r = int(min(key_width, key_height) * 0.25)

        cv2.circle(overlay, (cx, cy), r, (0, 0, 255), -1)

    return cv2.addWeighted(overlay, 0.45, frame, 0.55, 0)