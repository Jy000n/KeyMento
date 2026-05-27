import mido

def extract_answer_sheet(file_path):
    print(f"🎵 '{file_path}' 파일 분석을 시작합니다...")
    
    try:
        # 미디 파일 불러오기
        mid = mido.MidiFile(file_path)
    except FileNotFoundError:
        print(f"❌ 에러: '{file_path}' 파일을 찾을 수 없습니다! 폴더 위치를 확인해주세요.")
        return []

    answer_sheet = []
    absolute_time = 0.0  # 곡 시작부터 경과된 전체 시간(초)

    # 미디 파일 안의 모든 메시지를 순서대로 읽기
    for msg in mid:
        # mido에서 msg.time은 '이전 메시지로부터 경과된 시간(초)'을 의미합니다.
        # 따라서 이를 계속 더해주면 곡이 시작된 후의 '절대 시간'이 됩니다.
        absolute_time += msg.time

        # 우리가 필요한 건 '건반을 누르는(Note On)' 정보뿐입니다.
        # (velocity가 0인 경우는 건반을 떼는 Note Off와 같으므로 제외)
        if msg.type == 'note_on' and msg.velocity > 0:
            note_data = {
                'note': msg.note,
                'time': round(absolute_time, 3), # 소수점 3자리(밀리초)까지 반올림
                'velocity': msg.velocity
            }
            answer_sheet.append(note_data)

    print(f"✅ 분석 완료! 총 {len(answer_sheet)}개의 노트(정답)를 추출했습니다.\n")
    return answer_sheet

# --- 테스트 실행 부분 ---
if __name__ == "__main__":
    # 준비한 파일 이름 입력
    test_file = "head-shoulder-knee-and-toe.mid" 
    
    # 함수 실행해서 정답지 받아오기
    my_answer_sheet = extract_answer_sheet(test_file)
    
    # 추출된 정답 중 처음 5개만 화면에 출력해보기
    print("--- 📝 정답지 미리보기 (처음 5개 노트) ---")
    for i, data in enumerate(my_answer_sheet[:5]):
        print(f"[{i+1}번째 노트] 누를 시간: {data['time']}초 | 건반: {data['note']}번 | 세기: {data['velocity']}")