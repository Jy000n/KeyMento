# 🎹 Piano AR (Webcam-based Piano Key Overlay)

웹캠을 이용해 피아노 건반을 인식하고,
각 건반 위에 LED처럼 색상을 AR 오버레이

---

## 📌 Features

- 📷 USB 웹캠 지원
- 🎯 4점 클릭 기반 캘리브레이션
- 🎹 자동 건반 좌표 매핑 (흰 건반 + 검은 건반)
- 🌈 실시간 AR 오버레이 (LED 효과)
- 🧠 손 가림(occlusion) 문제 없이 동작 (좌표 고정 방식)

---

## 🛠️ Tech Stack

- Python
- OpenCV
- NumPy

---

## 📂 Project Structure

```
piano-ar/
│
├── main.py                  # 프로그램 실행 파일
│
├── camera/                  # 카메라 관련
│   └── capture.py           # 웹캠 연결
│
├── calibration/             # 초기 설정
│   └── calibrator.py        # 4점 클릭으로 키보드 영역 지정
│
├── keyboard/                # 건반 로직
│   ├── layout.py            # 건반 구조 정의 (흰/검 패턴)
│   └── mapping.py           # 좌표 계산
│
├── ar/                      # AR 렌더링
│   └── overlay.py           # 건반 위 LED 표시
│
├── utils/                   # 유틸
│   └── transform.py         # perspective transform
│
└── README.md
```

---

## ⚙️ Installation

```bash
pip install opencv-python numpy
```

---

## ▶️ Usage

```bash
python main.py
```

### 실행 과정

1. 카메라 실행
2. 피아노 건반의 네 꼭짓점 클릭 (좌상 → 우상 → 우하 → 좌하)
3. 자동으로 키보드 평면 변환
4. 건반 위에 AR LED 표시

---

## 📷 Camera Setup

### USB Webcam

```python
open_camera(0)
```

---

## 🧠 Core Idea

매 프레임마다 건반을 인식하지 않고,
초기 캘리브레이션을 통해 좌표를 고정하는 방식 사용

→ 손이 건반을 가려도 정확하게 동작

---

## ⚠️ Notes

- 카메라는 반드시 고정해야 합니다
- 조명이 일정해야 정확도가 높습니다
- 키보드 전체가 화면에 보여야 합니다

---

## 🚀 Future Work

- 🎵 MIDI 입력 연동 (실제 연주 반응)
- ✋ 손 추적 (MediaPipe Hands)
- 🎼 악보 기반 자동 가이드
- 🌐 Web 버전 (React + Canvas)

---

## 📌 Summary

카메라 입력을 기반으로 피아노 건반을 좌표화하고
그 위에 AR 오버레이를 적용

1. 캘리브레이션 (4점 클릭)
2. 좌표 변환 (Perspective Transform)
3. AR 렌더링

---
