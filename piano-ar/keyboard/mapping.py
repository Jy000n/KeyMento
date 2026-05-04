from .layout import WHITE_KEYS, white_key, black_keys


def build_keys(width, height):
    whites = [
        white_key(i, width, height, WHITE_KEYS)
        for i in range(WHITE_KEYS)
    ]

    blacks = black_keys(whites, height)

    return whites, blacks