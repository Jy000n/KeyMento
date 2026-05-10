import mido
import rtmidi
import time

def get_answer_sheet(file_path):
    mid = mido.MidiFile(file_path)
    sheet = []
    absolute_time = 0.0
    for msg in mid:
        absolute_time += msg.time
        # 60번(가온 도) 이상의 음만 추출
        if msg.type == 'note_on' and msg.velocity > 0 and msg.note >= 60:
            sheet.append({'note': msg.note, 'time': absolute_time})
    return sheet

def main():
    filename = "head-shoulder-knee-and-toe.mid" 
    answers = get_answer_sheet(filename)
    
    if not answers:
        print("정답지가 비어있습니다. MIDI 파일을 확인해주세요.")
        return

    # 통계를 위한 변수 설정
    current_idx = 0
    correct_count = 0
    wrong_count = 0
    total_notes = len(answers)
    
    midi_in = rtmidi.MidiIn()
    midi_in.open_port(0)
    
    print(f"\n🎵 연주 시작! 총 {total_notes}개의 노트를 연주해야 합니다.")
    print("-" * 40)
    print(f"👉 첫 번째 목표 건반: {answers[0]['note']}")

    try:
        while current_idx < total_notes:
            timer_event = midi_in.get_message()
            
            if timer_event:
                message, _ = timer_event
                state, note, velocity = message
                
                # 건반을 누르는 신호(Note On) 확인
                if state == 144 and velocity > 0:
                    target = answers[current_idx]['note']
                    
                    if note == target:
                        print(f"✅ [Correct!] {note}번 성공")
                        correct_count += 1
                    else:
                        print(f"❌ [Wrong!] 입력:{note} / 정답:{target}")
                        wrong_count += 1
                    
                    # 맞든 틀리든 다음 노트 인덱스로 이동
                    current_idx += 1
                    
                    # 다음 음이 남아있다면 목표 출력
                    if current_idx < total_notes:
                        print(f"👉 다음 목표: {answers[current_idx]['note']}")
            
            time.sleep(0.01)

        # === 최종 결과 출력 ===
        print("\n" + "="*40)
        print("🎉 곡을 모두 완주하셨습니다!")
        print("="*40)
        
        accuracy = (correct_count / total_notes) * 100
        
        print(f"📊 나의 연주 결과")
        print(f"- 전체 건반 수: {total_notes}개")
        print(f"- 맞게 입력함: {correct_count}개")
        print(f"- 틀리게 입력함: {wrong_count}개")
        print(f"- 최종 정확도: {accuracy:.1f}%")
        print("="*40)

    except KeyboardInterrupt:
        print("\n연주가 중단되었습니다.")
    finally:
        midi_in.close_port()

if __name__ == "__main__":
    main()