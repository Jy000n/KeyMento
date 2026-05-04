import cv2

def render(frame, whites, blacks):
    overlay = frame.copy()

    # 흰 건반 테스트
    test_white = [10, 11, 12]

    for i in test_white:
        x1, y1, x2, y2 = whites[i]
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)

    # 검은 건반 테스트
    test_black = [0, 1, 2]  
    for i in test_black:
        x1, y1, x2, y2 = blacks[i]
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1)

    return cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)