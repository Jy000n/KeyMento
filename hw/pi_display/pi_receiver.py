"""Raspberry Pi-side receiver for the HDMI display module."""

from __future__ import annotations

import argparse
import socket
from importlib import import_module


try:
    from .protocol import UdpFrameAssembler, decode_frame
except ImportError:
    from protocol import UdpFrameAssembler, decode_frame


def require_opencv():
    try:
        return import_module("cv2")
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required. Install dependencies with "
            "`pip install -r hw/pi_display/requirements.txt`."
        ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Receive KeyMento AR video frames.")
    parser.add_argument("--host", default="0.0.0.0", help="Address to bind on the Raspberry Pi.")
    parser.add_argument("--port", type=int, default=9999, help="UDP port to listen on.")
    parser.add_argument("--buffer-size", type=int, default=65535, help="UDP receive buffer size.")
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Show the receiver window in fullscreen mode.",
    )
    parser.add_argument("--width", type=int, default=0, help="Force output width in pixels (0 = auto).")
    parser.add_argument("--height", type=int, default=0, help="Force output height in pixels (0 = auto).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cv2 = require_opencv()
    window_name = "KeyMento Pi Receiver"
    assembler = UdpFrameAssembler()

    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind((args.host, args.port))

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    if args.fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    screen_w = args.width
    screen_h = args.height
    if args.fullscreen and (screen_w == 0 or screen_h == 0):
        rect = cv2.getWindowImageRect(window_name)
        screen_w, screen_h = rect[2], rect[3]

    print(f"Listening for KeyMento video on {args.host}:{args.port}")

    try:
        while True:
            packet, _ = receiver.recvfrom(args.buffer_size)
            encoded_frame = assembler.add_packet(packet)
            if encoded_frame is None:
                continue

            frame = decode_frame(encoded_frame)
            if args.fullscreen and screen_w > 0 and screen_h > 0:
                frame = cv2.resize(frame, (screen_w, screen_h))
            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    finally:
        receiver.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
