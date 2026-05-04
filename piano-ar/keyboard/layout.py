WHITE_KEYS = 19

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
    key_w = whites[1][0] - whites[0][0] 

    bw = int(key_w * 0.6)  
    bh = int(height * 0.62)

    for i in BLACK_KEY_POSITIONS:
        border_x = whites[i][2]  
        cx = border_x            

        bx1 = cx - bw // 2
        bx2 = cx + bw // 2

        blacks.append((bx1, 0, bx2, bh))

    return blacks