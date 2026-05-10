# hw/pi_display/pc_sender.py

from __future__ import annotations

import argparse

try:
    from .protocol import UdpFrameSender
except ImportError:
    from protocol import UdpFrameSender


class PiDisplaySender:
    def __init__(self, pi_ip: str, port: int = 9999, jpeg_quality: int = 70):
        self.sender = UdpFrameSender(
            host=pi_ip,
            port=port,
            jpeg_quality=jpeg_quality,
        )

    def send(self, frame):
        self.sender.send(frame)

    def close(self):
        self.sender.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send AR video frames to the Raspberry Pi display.")
    parser.add_argument("--pi-ip", required=True, help="Raspberry Pi IP address.")
    parser.add_argument("--port", type=int, default=9999, help="UDP port (default: 9999).")
    parser.add_argument("--quality", type=int, default=70, help="JPEG quality 1-100 (default: 70).")
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index (default: 0).")
    parser.add_argument("--preview", action="store_true", help="Show a local preview window on the PC.")
    return parser.parse_args()


def main() -> None:
    import cv2

    args = _parse_args()
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {args.camera}")

    sender = PiDisplaySender(pi_ip=args.pi_ip, port=args.port, jpeg_quality=args.quality)
    print(f"Sending to {args.pi_ip}:{args.port}  (quality={args.quality}, camera={args.camera})")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            sender.send(frame)

            if args.preview:
                cv2.imshow("KeyMento PC Preview", frame)
                if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
    finally:
        sender.close()
        cap.release()
        if args.preview:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
