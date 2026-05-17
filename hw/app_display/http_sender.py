"""HTTP MJPEG stream sender — streams AR frames to any browser on the local network.

Open  http://<PC-IP>:8080/  in Safari on iPad, Chrome, or any browser.
No app installation required.
"""

from __future__ import annotations

import argparse
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Tuple

try:
    import cv2
except ImportError:
    cv2 = None  # type: ignore


_DEFAULT_PORT = 8080
_DEFAULT_QUALITY = 70
_BOUNDARY = "keymento_mjpeg"


class _FrameStore:
    """Thread-safe latest-frame buffer. Supports multiple concurrent clients."""

    def __init__(self) -> None:
        self._cond = threading.Condition()
        self._jpeg: Optional[bytes] = None
        self._seq: int = -1

    def put(self, jpeg: bytes) -> None:
        with self._cond:
            self._jpeg = jpeg
            self._seq += 1
            self._cond.notify_all()

    def wait_new(self, last_seq: int, timeout: float = 1.0) -> Tuple[int, Optional[bytes]]:
        with self._cond:
            self._cond.wait_for(lambda: self._seq != last_seq, timeout=timeout)
            return self._seq, self._jpeg


def _make_handler(store: _FrameStore):
    class _MjpegHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args) -> None:
            pass  # suppress per-request access logs

        def do_GET(self) -> None:
            if self.path == "/":
                self._serve_index()
            elif self.path == "/video":
                self._serve_stream()
            else:
                self.send_error(404)

        def _serve_index(self) -> None:
            html = (
                "<!DOCTYPE html><html><head>"
                "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                "</head><body style='margin:0;background:#000'>"
                "<img src='/video' style='width:100vw;height:100vh;object-fit:contain'>"
                "</body></html>"
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        def _serve_stream(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary={_BOUNDARY}")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Connection", "close")
            self.end_headers()

            last_seq = -1
            try:
                while True:
                    seq, jpeg = store.wait_new(last_seq, timeout=2.0)
                    last_seq = seq
                    if jpeg is None:
                        continue
                    header = (
                        f"--{_BOUNDARY}\r\n"
                        f"Content-Type: image/jpeg\r\n"
                        f"Content-Length: {len(jpeg)}\r\n\r\n"
                    ).encode()
                    self.wfile.write(header + jpeg + b"\r\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass  # client disconnected

    return _MjpegHandler


def _local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


class HttpDisplaySender:
    """Encodes OpenCV frames and streams them as MJPEG over HTTP.

    Drop-in alternative to PiDisplaySender for iPad / browser targets.

    Example::

        sender = HttpDisplaySender(port=8080)
        sender.start()
        while True:
            sender.send(ar_frame)
        sender.close()

    Then open  http://<PC-IP>:8080/  in Safari on iPad.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = _DEFAULT_PORT,
        jpeg_quality: int = _DEFAULT_QUALITY,
    ) -> None:
        self.host = host
        self.port = port
        self.jpeg_quality = jpeg_quality
        self._store = _FrameStore()
        self._server = HTTPServer((host, port), _make_handler(self._store))
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def start(self) -> None:
        self._thread.start()
        ip = _local_ip()
        print(f"MJPEG stream ready:")
        print(f"  Browser / iPad  ->  http://{ip}:{self.port}/")
        print(f"  Raw stream      ->  http://{ip}:{self.port}/video")

    def send(self, frame) -> None:
        if cv2 is None:
            raise RuntimeError("opencv-python is required. pip install opencv-python")
        quality = max(1, min(100, int(self.jpeg_quality)))
        ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if ok:
            self._store.put(encoded.tobytes())

    def close(self) -> None:
        self._server.shutdown()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream webcam / AR frames as MJPEG to iPad or browser.")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=_DEFAULT_PORT, help=f"HTTP port (default: {_DEFAULT_PORT}).")
    parser.add_argument("--quality", type=int, default=_DEFAULT_QUALITY, help="JPEG quality 1-100 (default: 70).")
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index (default: 0).")
    parser.add_argument("--preview", action="store_true", help="Show a local OpenCV preview window on the PC.")
    return parser.parse_args()


def main() -> None:
    if cv2 is None:
        raise RuntimeError("opencv-python is required. pip install opencv-python")

    args = _parse_args()
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {args.camera}")

    sender = HttpDisplaySender(host=args.host, port=args.port, jpeg_quality=args.quality)
    sender.start()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            sender.send(frame)
            if args.preview:
                cv2.imshow("KeyMento HTTP Preview", frame)
                if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
    finally:
        sender.close()
        cap.release()
        if args.preview:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
