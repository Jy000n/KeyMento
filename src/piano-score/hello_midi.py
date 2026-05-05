import rtmidi
import time

# MIDI 입력 객체 생성
midi_in = rtmidi.MidiIn()

# 연결된 장치 목록 확인
ports = midi_in.get_ports()
print(f"찾은 장치 목록: {ports}")

if ports:
    # Keystation 이름이 들어간 포트를 자동으로 찾아서 엽니다.
    target_port = 0
    for i, name in enumerate(ports):
        if "Keystation" in name:
            target_port = i
            break
            
    midi_in.open_port(target_port)
    print(f"[{ports[target_port]}] 연결 완료! 건반을 눌러보세요.")
else:
    print("MIDI 장치를 찾을 수 없습니다. 연결을 확인해주세요.")
    exit()

try:
    while True:
        # 미디 신호가 들어왔는지 확인 (메시지, 델타타임)
        timer_event = midi_in.get_message()
        
        if timer_event:
            message, deltatime = timer_event
            # message[1]은 노트 번호, message[2]는 누르는 세기(Velocity)
            print(f"신호 발생! -> 노트 번호: {message[1]}, 세기: {message[2]}")
            
        time.sleep(0.01) # CPU 과부하 방지
except KeyboardInterrupt:
    print("\n종료합니다.")
finally:
    midi_in.close_port()