import streamlit as st
from streamlit.components.v1 import html
import json

st.set_page_config(layout="wide", page_title="비디오 수강 및 포인트 지급")

st.title("🎥 비디오 수강 & 포인트 지급 시스템")

# --- 세션 변수 초기화 ---
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'video_completed_for_points' not in st.session_state:
    st.session_state.video_completed_for_points = False
if 'current_video_time' not in st.session_state:
    st.session_state.current_video_time = 0.0
if 'total_video_duration' not in st.session_state:
    st.session_state.total_video_duration = 0.0
if 'js_message_payload' not in st.session_state: # JavaScript에서 받은 최신 데이터를 원본 문자열과 함께 저장
    st.session_state.js_message_payload = {'raw_string': '', 'parsed_data': {}}


# --- 1. 비디오 플레이어 및 JavaScript 통신 로직을 포함하는 HTML 컴포넌트 ---
# 주의: 이 긴 HTML/JS 문자열을 Python 코드 안에 직접 f-string으로 넣습니다.
# HTML 코드 부분은 위에 별도로 제공된 블록을 그대로 복사하여 여기에 붙여넣으세요.
video_component_html = """
<style>
    /* 기본적인 비디오 플레이어 스타일 (선택 사항) */
    #myVideoPlayer {
        display: block;
        margin: 0 auto;
        border: 1px solid #ddd;
        border-radius: 8px;
    }
</style>

<video id="myVideoPlayer" width="100%" height="auto" controls playsinline>
    <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

<input type="text" id="streamlitHiddenInput" data-testid="video_status_receiver" style="display:none;" />

<script>
    const video = document.getElementById('myVideoPlayer');
    // hiddenInput은 iframe 내에서 직접 찾음
    const hiddenInput = document.getElementById('streamlitHiddenInput');

    // 디버깅 메시지 설정: Console 탭에 출력됨
    console.log("JS: Video player script loaded.");
    if (!video) {
        console.error("JS Error: Video element (myVideoPlayer) not found!");
    }
    if (!hiddenInput) {
        console.error("JS Error: Hidden input (streamlitHiddenInput) for Streamlit not found!");
    }

    // Streamlit으로 메시지를 보내는 함수
    function sendVideoStatusToStreamlit(type, payload) {
        if (hiddenInput) {
            const message = { type: type, payload: payload };
            hiddenInput.value = JSON.stringify(message);
            // Streamlit에 값이 변경되었음을 알리기 위해 'input' 이벤트 강제 발생
            hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
            // console.log("JS: Sent message to Streamlit:", message.type, JSON.stringify(payload)); // 디버깅: 너무 많이 출력될 수 있음
        } else {
            console.error("JS Error: Cannot send message, hidden input is not accessible.");
        }
    }

    // 비디오 이벤트 리스너 설정
    if (video) {
        // 비디오 메타데이터 로드 시 (총 길이 확보)
        video.addEventListener('loadedmetadata', () => {
            console.log("JS: Video loadedmetadata event fired.");
            sendVideoStatusToStreamlit('video_metadata', { duration: video.duration });
        });

        // 비디오 재생/일시정지 상태 변경 시
        video.addEventListener('play', () => { console.log("JS: Video started playing."); });
        video.addEventListener('pause', () => { console.log("JS: Video paused."); });

        // 1초마다 비디오 상태 업데이트 전송
        // 'timeupdate' 이벤트는 너무 자주 발생하므로, setInterval을 사용하여 1초 간격으로 제한
        let lastSentTime = 0;
        const sendInterval = 1000; // 1초마다 전송 (밀리초)
        video.addEventListener('timeupdate', () => {
            const currentTime = video.currentTime;
            if (currentTime * 1000 - lastSentTime >= sendInterval) { // 시간 차이 계산
                sendVideoStatusToStreamlit('video_status_update', {
                    currentTime: currentTime,
                    duration: video.duration,
                    ended: video.ended
                });
                lastSentTime = currentTime * 1000;
            }
        });

        // 비디오가 완전히 끝나면 명시적으로 메시지 전송
        video.addEventListener('ended', () => {
            console.log("JS: Video ended event fired.");
            sendVideoStatusToStreamlit('video_ended', { ended: true });
        });

    } else {
        console.error("JS: Video element 'myVideoPlayer' was not found when setting up event listeners.");
    }

    // 추가 디버깅: 5초마다 비디오 상태 강제 확인
    setInterval(() => {
        if (video) {
            console.log(`JS Debug: Current time: ${video.currentTime.toFixed(1)}, Duration: ${video.duration.toFixed(1)}, Ended: ${video.ended}`);
        }
    }, 5000); // 5초마다 콘솔에 디버깅 정보 출력

</script>
"""

# Streamlit HTML 컴포넌트를 사용하여 비디오 플레이어와 JS 코드 삽입
# height를 넉넉하게 주어 비디오가 잘 보이도록 합니다.
st.components.v1.html(video_component_html, height=400)

# --- 2. Streamlit Python 코드에서 메시지 수신 및 처리 ---
# JavaScript에서 업데이트한 숨겨진 input의 값을 읽어옵니다.
# data-testid와 일치하는 key를 사용해야 합니다.
received_message_str = st.text_input(
    "Hidden Video Status Receiver",
    key="video_status_receiver",
    label_visibility="collapsed" # UI에서 숨김
)

# JavaScript에서 새로운 메시지를 받았을 때만 처리 (중복 실행 방지)
if received_message_str and received_message_str != st.session_state.js_message_payload.get('raw_string'):
    try:
        data = json.loads(received_message_str)
        st.session_state.js_message_payload = {
            'raw_string': received_message_str,
            'parsed_data': data
        }

        # Python 디버깅: 어떤 메시지를 받았는지 콘솔이나 Streamlit 앱에 출력 (필요시 주석 해제)
        # st.write(f"Python Received: Type={data.get('type')}, Payload={data.get('payload')}")

        message_type = data.get('type')
        payload = data.get('payload', {})

        if message_type == 'video_status_update':
            st.session_state.current_video_time = payload.get('currentTime', 0.0)
            if payload.get('duration', 0.0) > 0:
                st.session_state.total_video_duration = payload.get('duration', 0.0)

        elif message_type == 'video_ended':
            st.session_state.current_video_time = st.session_state.total_video_duration # 비디오 끝까지 재생된 것으로 간주
            payload['ended'] = True # ended 플래그 강제 설정

        elif message_type == 'video_metadata':
