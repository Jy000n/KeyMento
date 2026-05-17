#!/usr/bin/env bash
# Raspberry Pi setup for the pi_midi module

set -e

echo "=== Keymento pi_midi 설정 ==="

# System dependencies for python-rtmidi
sudo apt-get update
sudo apt-get install -y libasound2-dev libjack-dev

# Python dependencies
pip install -r "$(dirname "$0")/requirements.txt"

echo ""
echo "=== 설정 완료 ==="
echo "실행 방법:"
echo "  python pi_sender.py --pc-ip <노트북IP>"
echo ""
echo "MIDI 장치 확인:"
echo "  python pi_sender.py --list-ports"
