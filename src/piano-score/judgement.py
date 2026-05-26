import mido
import rtmidi
import time

# MIDI 노트 번호 → 음이름 변환
NOTE_NAMES = ['도', '도#', '레', '레#', '미', '파', '파#', '솔', '솔#', '라', '라#', '시']

# 다음 목표 렌더링 타이밍 조절 가능
HINT_AHEAD = 1.0  

def note_to_name(note):
    return NOTE_NAMES[note % 12]

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

    # === 통계 변수 초기화 ===
    total_notes = len(answers)
    pitch_correct = 0
    pitch_wrong = 0
    
    timing_stats = {'Perfect': 0, 'Great': 0, 'Good': 0, 'Miss': 0}
    current_idx = 0
    
    midi_in = rtmidi.MidiIn()
    midi_in.open_port(0)
    
    print(f"\n🎵 총 {total_notes}개의 노트를 연주해야 합니다.")
    print("준비하세요! 3초 뒤 연주를 시작합니다...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
        
    print("\n🎹 [START] 연주 시작!")
    print(f"👉 첫 번째 목표 건반: {note_to_name(answers[0]['note'])}")
    
    # 곡 시작 기준 시간 기록
    start_time = time.time()

    try:
        while current_idx < total_notes:
            timer_event = midi_in.get_message()
            
            # 현재 곡이 시작된 지 몇 초 지났는지 계산
            current_elapsed_time = time.time() - start_time
            target_time = answers[current_idx]['time']
            
            if timer_event:
                message, _ = timer_event
                state, note, velocity = message
                
                # 건반을 누르는 신호(Note On) 확인
                if state == 144 and velocity > 0:
                    target_note = answers[current_idx]['note']
                    
                    # 1. 음계(Pitch) 판정
                    if note == target_note:
                        pitch_correct += 1
                        pitch_msg = f"✅ [음정 O] {note_to_name(note)}"
                    else:
                        pitch_wrong += 1
                        pitch_msg = f"❌ [음정 X] 입력:{note_to_name(note)} 정답:{note_to_name(target_note)}"
                        
                    # 2. 박자(Timing) 판정
                    # 부호 있는 오차: 음수(-) = 빠름, 양수(+) = 늦음
                    time_diff_ms = (current_elapsed_time - target_time) * 1000 - 1000
                    abs_diff_ms = abs(time_diff_ms)
                    sign = f"+{time_diff_ms:.0f}" if time_diff_ms >= 0 else f"{time_diff_ms:.0f}"

                    if abs_diff_ms <= 1000:      # ±1000ms
                        timing_stats['Perfect'] += 1
                        timing_msg = f"✨ Perfect! ({sign}ms)"
                    elif abs_diff_ms <= 1500:    # ±1500ms
                        timing_stats['Great'] += 1
                        timing_msg = f"👍 Great!  ({sign}ms)"
                    elif abs_diff_ms <= 2000:    # ±2000ms
                        timing_stats['Good'] += 1
                        timing_msg = f"👌 Good!   ({sign}ms)"
                    else:                       # ±2000ms 초과
                        timing_stats['Miss'] += 1
                        timing_msg = f"☁️ Miss...  ({sign}ms)"
                    
                    # 실시간 결과 출력
                    print(f"[{current_idx+1}/{total_notes}] {pitch_msg}  |  {timing_msg}")
                    
                    # 무조건 다음 인덱스로 이동
                    current_idx += 1
                    
                    if current_idx < total_notes:
                        print(f"👉 다음 목표: {note_to_name(answers[current_idx]['note'])}")
            
            # CPU 과부하 방지용 미세 휴식 (0.001초 단위로 촘촘히 검사)
            time.sleep(0.001)

        # === 최종 결과 통계 산출 ===
        print("\n" + "="*50)
        print("🎉 곡 완주! 최종 분석 결과를 확인하세요 🎉")
        print("="*50)
        
        # 음계 정확도 계산
        pitch_accuracy = (pitch_correct / total_notes) * 100
        
        # 박자 정확도 계산 (가중치 부여: Perfect 100, Great 80, Good 50, Miss 0)
        timing_score_total = (timing_stats['Perfect'] * 100) + (timing_stats['Great'] * 80) + (timing_stats['Good'] * 50)
        timing_accuracy = timing_score_total / total_notes
        
        # 종합 정확도 계산 (음계 50% + 박자 50%)
        overall_accuracy = (pitch_accuracy + timing_accuracy) / 2
        
        print(f"🎵 전체 건반 수: {total_notes}개")
        print("-" * 50)
        print(f"🎹 [음계 분석] 정확도: {pitch_accuracy:.1f}%")
        print(f"   - 정답 건반: {pitch_correct}개")
        print(f"   - 오답 건반: {pitch_wrong}개")
        print("-" * 50)
        print(f"⏱️ [박자 분석] 정확도: {timing_accuracy:.1f}%")
        print(f"   - ✨ Perfect (±1000ms): {timing_stats['Perfect']}개")
        print(f"   - 👍 Great   (±1500ms): {timing_stats['Great']}개")
        print(f"   - 👌 Good    (±2000ms): {timing_stats['Good']}개")
        print(f"   - ☁️ Miss    (±2000ms↑): {timing_stats['Miss']}개")
        print("="*50)
        print(f"🏆 [최종 종합 점수]: {overall_accuracy:.1f} 점 / 100 점")
        print("="*50)

    except KeyboardInterrupt:
        print("\n연주가 중단되었습니다.")
    finally:
        midi_in.close_port()

if __name__ == "__main__":
    main()