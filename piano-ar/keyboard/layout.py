WHITE_KEYS = 19

# 흰 건반 19개 기준 검은 건반이 있는 위치 (0-indexed)
# C D E F G A B C D E F G A B C D E F G
# 검은건반: C#=0, D#=1, F#=3, G#=4, A#=5, C#=7, D#=8, F#=10, G#=11, A#=12, C#=14, D#=15, F#=17
BLACK_KEY_POSITIONS = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12, 14, 15, 17]


def white_key(i, width, height, white_count):
    key_w = width / white_count
    return (
        int(i * key_w),
        0,
        int((i + 1) * key_w),
        height
    )


def black_keys(whites, height):
    blacks = []
    key_w = whites[1][0] - whites[0][0]  # 흰 건반 너비

    bw = int(key_w * 0.6)   # 검은 건반 너비: 흰 건반의 60%
    bh = int(height * 0.62) # 검은 건반 높이: 전체의 62%

    for i in BLACK_KEY_POSITIONS:
        # 검은 건반은 i번째와 (i+1)번째 흰 건반 경계에 중앙 정렬
        border_x = whites[i][2]  # i번째 흰 건반의 오른쪽 끝
        cx = border_x            # 경계선을 중심으로

        bx1 = cx - bw // 2
        bx2 = cx + bw // 2

        blacks.append((bx1, 0, bx2, bh))

    return blacks