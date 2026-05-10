# Raspberry Pi Display Module

This folder contains the hardware-facing code for the Raspberry Pi 3B and HDMI
LCD display module.

- `pc_sender.py`: run on the PC. It creates the AR video and sends it over WiFi.
- `pi_receiver.py`: run on the Raspberry Pi. It receives video and shows it on the LCD.
- `protocol.py`: shared UDP/JPEG packet rules used by both sides.

## Install

```bash
cd ~/Keymento
python3 -m venv .venv
source .venv/bin/activate
pip install -r hw/pi_display/requirements.txt
```

## Start Receiver

```bash
cd ~/Keymento
python3 hw/pi_display/pi_receiver.py --port 9999
```

Then run the PC sender:

```powershell
python hw\pi_display\pc_sender.py --pi-ip 192.168.0.50 --preview
```

Replace `192.168.0.50` with the Pi address from:

```bash
ip addr show wlan0
```

Press `q` or `Esc` to stop the receiver.

## Autostart With systemd

```bash
sudo cp hw/pi_display/keymento.service /etc/systemd/system/keymento.service
sudo systemctl daemon-reload
sudo systemctl enable keymento.service
sudo systemctl start keymento.service
```

If the service starts before the desktop display is ready, start it manually for
the demo or add a short startup delay in the unit file.
