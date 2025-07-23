import streamlit as st
from streamlit.components.v1 import html
import json # JSON 모듈 임포트

st.set_page_config(layout="wide") # 넓은 레이아웃으로 설정

st.title("자동 영상 수강 시간 감지 & 포인트 지급")

# 세션 변수 초기화
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'watched' not in st.session_state:
    st.session_state.watched = False
if 'video_current_time' not in st.session_state:
    st.session_state.video_current_time = 0.0 # 실제 비디오 재생 시간을 저장할 변수
if 'last_received_message' not in st.session_state:
    st.session_state.last_received_message = "" # JS에서 받은 마지막 메시지 저장용

# 1. 영상 + JS : 영상 재생시간 주기적 전달, 종료 시점 전달
# HTML 내부에서 JS가 부모에게 메시지를 보내도록 함
video_html = """
<video id="video" width="100%" height="auto" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
</video>
<script>
const video = document.getElementById('video');

// 비디오 현재 시간과 상태를 1초마다 Streamlit으로 전송
setInterval(() => {
    if (video.readyState > 0) { // 비디오가 로드된 상태인지 확인
        window.parent.postMessage(
            {
                type: 'video_update',
                currentTime: video.currentTime,
                duration: video.duration,
                ended: video.ended
            },
            "*"
        );
    }
}, 1000); // 1초마다

// 비디오가 완전히 끝났을 때만 명시적으로 ended 메시지 전송
video.addEventListener('ended', () => {
    window.parent.postMessage({type: 'video_ended'}, "*");
});
</script>
"""

# HTML 컴포넌트를 Streamlit에 렌더링
# height를 넉넉하게 주어 비디오가 잘 보이도록 합니다.
st.components.v1.html(video_html, height=400)

# 2. Streamlit 내 JS 메시지 수신용 숨겨진 input + 리스너
# 이 스크립트는 HTML 컴포넌트 내에서 Streamlit으로 데이터를 전달하는 역할을 합니다.
# Streamlit의 html 컴포넌트는 postMessage를 직접 받지 못하므로,
# 메시지를 받아서 숨겨진 input의 value를 변경하고 이벤트를 발생시켜야 Streamlit이 이를 감지합니다.
st.components.v1.html("""
<script>
window.addEventListener("message", (event) => {
    // Streamlit 앱이 localhost가 아닌 경우, origin 검사를 강화하는 것이 좋습니다.
    // if (event.origin !== "http://localhost:8501") return; // 실제 배포 시 도메인 변경

    if (event.data.type === 'video_update' || event.data.type === 'video_ended') {
        const input = window.parent.document.querySelector('input[data-testid="video_message_input"]');
        if (input) {
            // JSON 문자열로 데이터를 직렬화하여 input value에 저장
            input.value = JSON.stringify(event.data);
            // input 이벤트 발생시켜 Streamlit이 값 변경을 감지하도록 함
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
});
</script>
<input type="text" data-testid="video_message_input" style="display:none;" />
""", height=0) # 이 컴포넌트 자체는 화면에 보이지 않으므로 height=0

# 3. 숨겨진 input 값 읽기
# Streamlit 앱이 재실행될 때마다 이 input의 값이 변경되었는지 확인합니다.
received_json_str = st.text_input(
    "Received Video Data",
    key="video_message_input",
    label_visibility="collapsed" # 레이블 숨김
)

# 4. 세션 상태 업데이트 및 포인트 지급 로직
if received_json_str and received_json_str != st.session_state.last_received_message:
    try:
        data = json.loads(received_json_str)
        st.session_state.last_received_message = received_json_str # 마지막으로 받은 메시지 업데이트

        if data.get('type') == 'video_update':
            # 비디오 현재 시간 업데이트
            st.session_state.video_current_time = data.get('currentTime', 0.0)
            st.session_state.video_duration = data.get('duration', 0.0) # 총 길이도 업데이트

            # 비디오가 끝났지만 아직 포인트 지급이 안 된 경우 (안전 장치)
            if data.get('ended') and not st.session_state.watched:
                st.session_state.points += 25
                st.session_state.watched = True
                st.success(f"🎉 영상 시청 완료! 포인트 25점 지급. 총 포인트: {st.session_state.points}")
                st.rerun() # 포인트 지급 후 바로 UI 업데이트를 위해 재실행
                
        elif data.get('type') == 'video_ended':
            # 비디오 종료 메시지가 명시적으로 오면 포인트 지급 (주요 트리거)
            if not st.session_state.watched:
                st.session_state.points += 25
                st.session_state.watched = True
                st.success(f"🎉 영상 시청 완료! 포인트 25점 지급. 총 포인트: {st.session_state.points}")
                st.rerun() # 포인트 지급 후 바로 UI 업데이트를 위해 재실행

    except json.JSONDecodeError:
        st.warning("JSON 디코딩 오류가 발생했습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

# 5. 프로그래스바 및 정보 표시
# 비디오의 총 길이가 0이면 (아직 로드 안됨) 300초(5분)를 기본값으로 사용
total_duration = st.session_state.video_duration if st.session_state.video_duration > 0 else (5 * 60)
progress = min(st.session_state.video_current_time / total_duration, 1.0)

st.progress(progress, text=f"시청 시간: {st.session_state.video_current_time:.1f}초 / {total_duration:.1f}초")
st.write(f"현재 포인트: **{st.session_state.points}** 점")

# Streamlit이 자동으로 재실행되도록 강제하는 부분 (선택 사항)
# 실시간 업데이트가 중요하면 사용하지만, 서버 부하를 고려해야 함
# import time
# time.sleep(1) # 1초마다 재실행 유도
# st.rerun()
