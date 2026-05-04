# tests/check_env.py
import cv2
import mido
import rtmidi
import sys
from importlib.metadata import version

print("=" * 50)
print("KeyMento 환경 체크")
print("=" * 50)
print(f"Python: {sys.version.split()[0]}")
print(f"OpenCV: {cv2.__version__}")
print(f"mido:   {version('mido')}")           # 이렇게 변경
print(f"rtmidi: {version('python-rtmidi')}")  # 이것도 추가

# 웹캠 확인
print("\n[웹캠]")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        h, w = frame.shape[:2]
        print(f"  ✓ OK ({w}x{h})")
    cap.release()
else:
    print("  ✗ 웹캠 인식 실패 — 다른 앱이 사용 중인지 확인")

# MIDI 장치 확인
print("\n[MIDI 입력 장치]")
midi_in = rtmidi.MidiIn()
ports = midi_in.get_ports()
if ports:
    for i, p in enumerate(ports):
        print(f"  [{i}] {p}")
else:
    print("  - 미연결 (지금은 OK, Phase 3에서 필요)")
del midi_in

print("\n" + "=" * 50)
print("환경 구축 완료")
print("=" * 50)