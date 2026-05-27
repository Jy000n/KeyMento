"""UDP JPEG frame transport for the Raspberry Pi HDMI display module."""

from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Optional, Tuple


MAGIC = b"KMT1"
HEADER_FORMAT = "!4sIHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
DEFAULT_PORT = 9999
DEFAULT_CHUNK_SIZE = 1200
DEFAULT_JPEG_QUALITY = 70


@dataclass(frozen=True)
class UdpVideoPacket:
    frame_id: int
    chunk_index: int
    chunk_count: int
    payload: bytes


def encode_frame(frame: Any, jpeg_quality: int = DEFAULT_JPEG_QUALITY) -> bytes:
    import cv2

    quality = max(1, min(100, int(jpeg_quality)))
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise ValueError("Failed to encode frame as JPEG")
    return encoded.tobytes()


def decode_frame(encoded_frame: bytes) -> Any:
    import cv2
    import numpy as np

    buffer = np.frombuffer(encoded_frame, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Failed to decode JPEG frame")
    return frame


def iter_frame_packets(
    encoded_frame: bytes,
    frame_id: int,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> Iterator[bytes]:
    if chunk_size <= HEADER_SIZE:
        raise ValueError("chunk_size must be larger than the UDP video header")

    payload_size = chunk_size - HEADER_SIZE
    chunk_count = (len(encoded_frame) + payload_size - 1) // payload_size
    if chunk_count > 65535:
        raise ValueError("Encoded frame is too large for the UDP video protocol")

    for chunk_index in range(chunk_count):
        start = chunk_index * payload_size
        end = start + payload_size
        header = struct.pack(HEADER_FORMAT, MAGIC, frame_id, chunk_index, chunk_count)
        yield header + encoded_frame[start:end]


def parse_packet(packet: bytes) -> UdpVideoPacket:
    if len(packet) < HEADER_SIZE:
        raise ValueError("Packet is shorter than the UDP video header")

    magic, frame_id, chunk_index, chunk_count = struct.unpack(
        HEADER_FORMAT,
        packet[:HEADER_SIZE],
    )
    if magic != MAGIC:
        raise ValueError("Packet does not belong to the KeyMento UDP video protocol")
    if chunk_index >= chunk_count:
        raise ValueError("Packet chunk index is outside the declared chunk count")

    return UdpVideoPacket(
        frame_id=frame_id,
        chunk_index=chunk_index,
        chunk_count=chunk_count,
        payload=packet[HEADER_SIZE:],
    )


class UdpFrameSender:
    """Encodes OpenCV frames and sends them as chunked UDP packets."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        jpeg_quality: int = DEFAULT_JPEG_QUALITY,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        self.address: Tuple[str, int] = (host, port)
        self.jpeg_quality = jpeg_quality
        self.chunk_size = chunk_size
        self.frame_id = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, frame: Any) -> int:
        encoded_frame = encode_frame(frame, self.jpeg_quality)
        packet_count = 0
        for packet in iter_frame_packets(encoded_frame, self.frame_id, self.chunk_size):
            self.socket.sendto(packet, self.address)
            packet_count += 1

        self.frame_id = (self.frame_id + 1) % 2**32
        return packet_count

    def close(self) -> None:
        self.socket.close()


class UdpFrameAssembler:
    """Reassembles chunked UDP packets into complete JPEG frame bytes."""

    def __init__(self, stale_after_seconds: float = 1.0) -> None:
        self.stale_after_seconds = stale_after_seconds
        self._frames: Dict[int, Dict[str, object]] = {}

    def add_packet(self, packet_bytes: bytes) -> Optional[bytes]:
        packet = parse_packet(packet_bytes)
        now = time.monotonic()

        frame_state = self._frames.setdefault(
            packet.frame_id,
            {
                "created_at": now,
                "chunk_count": packet.chunk_count,
                "chunks": {},
            },
        )

        if frame_state["chunk_count"] != packet.chunk_count:
            self._frames.pop(packet.frame_id, None)
            return None

        chunks = frame_state["chunks"]
        assert isinstance(chunks, dict)
        chunks[packet.chunk_index] = packet.payload

        if len(chunks) == packet.chunk_count:
            encoded_frame = b"".join(chunks[i] for i in range(packet.chunk_count))
            self._frames.pop(packet.frame_id, None)
            self._drop_older_frames(packet.frame_id)
            return encoded_frame

        self.drop_stale_frames(now)
        return None

    def drop_stale_frames(self, now: Optional[float] = None) -> None:
        current_time = now if now is not None else time.monotonic()
        stale_ids = [
            frame_id
            for frame_id, frame_state in self._frames.items()
            if current_time - float(frame_state["created_at"]) > self.stale_after_seconds
        ]
        for frame_id in stale_ids:
            self._frames.pop(frame_id, None)

    def _drop_older_frames(self, newest_frame_id: int) -> None:
        older_ids = [frame_id for frame_id in self._frames if frame_id < newest_frame_id]
        for frame_id in older_ids:
            self._frames.pop(frame_id, None)
