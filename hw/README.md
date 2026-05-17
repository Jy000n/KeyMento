# KeyMento Hardware Modules

PC에서 촬영한 AR 영상을 Raspberry Pi 3B에 연결된 HDMI LCD로 무선 전송하는 모듈입니다.

- `pi_display/pc_sender.py` — PC에서 실행. 카메라로 AR 영상을 만들어 Wi-Fi로 전송.
- `pi_display/pi_receiver.py` — 라즈베리파이에서 실행. 영상을 받아 LCD에 출력.

---

## 필요 환경

| 항목 | 버전 |
|------|------|
| Python | 3.8 이상 |
| 패키지 | `numpy`, `opencv-python` |

---

## 설치

### PC (Windows)

```powershell
cd C:\project\Keymento
python -m venv venv
venv\Scripts\activate
pip install -r hw\pi_display\requirements.txt
```

### 라즈베리파이

```bash
cd ~/Keymento
bash hw/pi_display/pi_setup.sh
```

---

## 실행 순서

### 1단계 — 라즈베리파이 IP 확인

라즈베리파이 터미널에서:

```bash
ip addr show wlan0
```

출력에서 `inet 192.168.x.x` 형태의 주소를 메모해 둡니다.

### 2단계 — 라즈베리파이에서 수신기 실행

```bash
cd ~/Keymento
source .venv/bin/activate
python3 hw/pi_display/pi_receiver.py
```

전체화면으로 띄우려면:

```bash
python3 hw/pi_display/pi_receiver.py --fullscreen
```

### 3단계 — PC에서 송신기 실행

```powershell
cd C:\project\Keymento
venv\Scripts\activate
python hw\pi_display\pc_sender.py --pi-ip 192.168.x.x
```

`192.168.x.x` 자리에 1단계에서 확인한 라즈베리파이 IP를 입력합니다.

PC 화면에도 미리보기를 띄우려면:

```powershell
python hw\pi_display\pc_sender.py --pi-ip 192.168.x.x --preview
```

---

## 주요 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--pi-ip` | (필수) | 라즈베리파이 IP 주소 |
| `--port` | 9999 | UDP 포트 |
| `--quality` | 70 | JPEG 압축 품질 (1~100) |
| `--camera` | 0 | 웹캠 장치 번호 |
| `--preview` | off | PC 미리보기 창 표시 |

---

## 종료

`q` 또는 `Esc` 키를 누르면 종료됩니다.

---

## 테스트

### 단계 1 — 환경 체크 (PC)

패키지 설치, 웹캠 인식 여부를 먼저 확인합니다.

```powershell
cd C:\project\Keymento
venv\Scripts\activate
python tests/check_env.py
```

웹캠 해상도와 OpenCV 버전이 정상 출력되면 환경은 OK입니다.

---

### 단계 2 — PC 단독 루프백 테스트 (Pi 없이 전체 파이프라인 확인)

Pi 없이 PC 한 대에서 송·수신기를 모두 띄워 영상이 정상 전달되는지 확인합니다.

**터미널 A** — 수신기 실행:

```powershell
cd C:\project\Keymento
venv\Scripts\activate
python hw\pi_display\pi_receiver.py
```

**터미널 B** — 송신기를 `127.0.0.1`(자기 자신)로 전송:

```powershell
cd C:\project\Keymento
venv\Scripts\activate
python hw\pi_display\pc_sender.py --pi-ip 127.0.0.1 --preview
```

터미널 A의 수신기 창에 카메라 영상이 나타나면 통신 파이프라인은 정상입니다.

---

### 단계 3 — 실제 Pi 연결 테스트

루프백이 통과된 뒤 Pi와 같은 Wi-Fi에 연결해 실제 전송을 확인합니다.

1. Pi IP 확인: `ip addr show wlan0`
2. Pi에서 수신기 실행 (단계 2 → 실행 순서 참고)
3. PC에서 실제 Pi IP로 송신:

```powershell
python hw\pi_display\pc_sender.py --pi-ip 192.168.x.x --preview
```

**체크리스트**

- [ ] PC 미리보기(`--preview`)와 Pi LCD 영상이 동일하게 보임
- [ ] 영상 끊김·지연이 허용 범위 내인지 확인 (`--quality` 값을 낮춰 개선 가능)
- [ ] `q` / `Esc` 로 양쪽 모두 정상 종료됨

---

## 라즈베리파이 부팅 시 자동 실행 (systemd)

```bash
sudo cp hw/pi_display/keymento.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable keymento.service
sudo systemctl start keymento.service
```

서비스 상태 확인:

```bash
sudo systemctl status keymento.service
```
