import rtmidi
import time

# 🎯 우리가 정한 '정답 건반' (60 = 가운데 '도')
TARGET_NOTE = 60

def check_note(event, data=None):
    message, deltatime = event
    status = message[0]
    note = message[1]
    velocity = message[2]

    # 건반을 '누른' 상태인지 확인 (상태 코드가 144이고, 세기가 0보다 클 때)
    if status == 144 and velocity > 0:
        # 누른 건반이 정답 건반과 일치하는지 판정
        if note == TARGET_NOTE:
            print(f"✅ Correct! (누른 건반: {note})")
        else:
            print(f"❌ Wrong! (누른 건반: {note} / 정답: {TARGET_NOTE})")

def main():
    midi_in = rtmidi.MidiIn()
    
    try:
        # 포트 0번 강제 열기 (아까 성공했던 방식)
        midi_in.open_port(0)
        midi_in.set_callback(check_note)
        
        print("=========================================")
        print(f"피아노 판정 시스템 시작! 정답 건반은 '{TARGET_NOTE}번(도)' 입니다.")
        print("=========================================")
        
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        midi_in.close_port()

if __name__ == "__main__":
    main()