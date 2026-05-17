# App Display Module

iPad / 브라우저로 AR 영상을 Wi-Fi로 스트리밍합니다. 앱 설치 없이 Safari에서 바로 볼 수 있습니다.

## 설치

```powershell
pip install -r hw/app_display/requirements.txt
```

## 실행

```powershell
python hw\app_display\http_sender.py --preview
```

iPad Safari 또는 PC 브라우저에서 아래 주소로 접속하세요:

```
http://<PC-IP>:8080/
```

PC IP는 실행 시 터미널에 자동으로 출력됩니다.

## 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--port` | 8080 | HTTP 포트 |
| `--quality` | 70 | JPEG 품질 (1-100) |
| `--camera` | 0 | 웹캠 인덱스 |
| `--preview` | off | PC 로컬 미리보기 창 표시 |

## AR 코드와 통합

```python
from hw.app_display.http_sender import HttpDisplaySender

sender = HttpDisplaySender(port=8080, jpeg_quality=70)
sender.start()

# AR 루프 안에서
sender.send(ar_frame)

# 종료 시
sender.close()
```

`PiDisplaySender`와 인터페이스가 동일하므로 교체만 하면 됩니다.
