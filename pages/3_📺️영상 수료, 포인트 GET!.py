import streamlit as st
from streamlit.components.v1 import html
import json

st.set_page_config(layout="wide", page_title="비디오 수강 및 포인트 지급")

st.title("🎥 비디오 수강 & 포인트 지급 시스템")

# --- 세션 변수 초기화 ---
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'video_completed_for_points' not in st.session_state:
    st.session_state.video_completed_for_points = False # 포인트가 지급되었는지 추적
if 'current_video_time' not in st.session_state:
    st.session_state.current_video_time = 0.0
if 'total_video_duration' not in st.session_state:
    st.session_state.total_video_duration = 0.0
if 'js_message_payload' not in st.session_state:
    st.session_state.js_message_payload = {} # JavaScript에서 받은 최신 데이터 저장

# --- 비디오 URL ---
VIDEO_URL = "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4"

# --- 1. 비디오 플레이어 및 JavaScript 통신 로직 ---
# 모든 JavaScript 로직을 하나의 HTML 컴포넌트에 포함하여 비디오와 통신합니다.
# 이 컴포넌트는 Streamlit 앱의 숨겨진 텍스트 입력 필드에 값을 업데이트하여 Python으로 데이터를 보냅니다.
video_player_and_sender_html = f"""
<video id="myVideoPlayer" width="100%" height="auto" controls src="{VIDEO_URL}">
    <source src="{VIDEO_URL}" type="video/mp4">
    Your browser does not support the video tag.
</video>
<script>
    const video = document.getElementById('myVideoPlayer');
    const hiddenInput = window.parent.document.querySelector('input[data-testid="video_status_receiver"]');

    // 디버깅을 위한 초기 메시지
    console.log("JS: Video player script loaded.");
    if (!video) console.error("JS Error: Video element not found!");
    if (!hiddenInput) console.error("JS Error: Hidden input for Streamlit not found!");

    // Streamlit으로 메시지를 보내는 함수
    function sendVideoStatusToStreamlit(type, payload) {{
        if (hiddenInput) {{
            const message = {{ type: type, payload: payload }};
            hiddenInput.value = JSON.stringify(message);
            hiddenInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            // console.log("JS: Sent message to Streamlit:", message.type, JSON.stringify(payload)); // 디버깅
        }} else {{
            console.error("JS Error: Cannot send message, hidden input is null.");
        }}
    }}

    // 1초마다 비디오 상태 업데이트 전송
    setInterval(() => {{
        if (video && video.readyState >= 1) {{ // video가 존재하고 최소한 메타데이터가 로드된 상태
            sendVideoStatusToStreamlit('video_status_update', {{
                currentTime: video.currentTime,
                duration: video.duration,
                ended: video.ended
            }});
        }}
    }}, 1000); // 1초마다 전송

    // 비디오가 끝나면 명시적으로 메시지 전송
    if (video) {{
        video.addEventListener('ended', () => {{
            sendVideoStatusToStreamlit('video_ended', {{ ended: true }});
        }});

        // 메타데이터 로드 시 (총 길이 확보)
        video.addEventListener('loadedmetadata', () => {{
            sendVideoStatusToStreamlit('video_metadata', {{ duration: video.duration }});
        }});
    }}
</script>
<input type="text" data-testid="video_status_receiver" style="display:none;" />
"""

# Streamlit HTML 컴포넌트를 사용하여 비디오 플레이어와 JS 코드 삽입
# height=0 인 input은 Streamlit이 값을 읽을 수 있도록 하지만 UI에 보이지 않게 합니다.
st.components.v1.html(video_player_and_sender_html, height=400)


# --- 2. Streamlit Python 코드에서 메시지 수신 및 처리 ---
# JavaScript에서 업데이트한 숨겨진 input의 값을 읽어옵니다.
received_message_str = st.text_input(
    "Hidden Video Status Receiver",
    key="video_status_receiver", # data-testid와 일치하도록 설정
    label_visibility="collapsed" # UI에서 숨김
)

# JavaScript에서 새로운 메시지를 받았을 때만 처리
if received_message_str and received_message_str != st.session_state.js_message_payload.get('raw_string'):
    try:
        # JSON 문자열을 파이썬 딕셔너리로 변환
        data = json.loads(received_message_str)
        st.session_state.js_message_payload = {
            'raw_string': received_message_str, # 중복 처리를 막기 위해 원본 문자열 저장
            'parsed_data': data
        }

        # st.write(f"Python received: {data.get('type')}, Payload: {data.get('payload')}") # 디버깅용

        message_type = data.get('type')
        payload = data.get('payload', {})

        if message_type == 'video_status_update':
            st.session_state.current_video_time = payload.get('currentTime', 0.0)
            if payload.get('duration', 0.0) > 0:
                st.session_state.total_video_duration = payload.get('duration', 0.0)

        elif message_type == 'video_ended':
            # 비디오 종료 이벤트가 발생하면 바로 총 시간 업데이트
            st.session_state.current_video_time = st.session_state.total_video_duration
            payload['ended'] = True # ended 플래그 강제 설정 (안전성)

        elif message_type == 'video_metadata':
            if payload.get('duration', 0.0) > 0:
                st.session_state.total_video_duration = payload.get('duration', 0.0)

        # --- 3. 포인트 지급 로직 ---
        # 비디오 총 길이가 유효하고 아직 포인트가 지급되지 않았을 때
        if st.session_state.total_video_duration > 0 and not st.session_state.video_completed_for_points:
            watch_percentage = (st.session_state.current_video_time / st.session_state.total_video_duration) * 100

            # 비디오가 JS에서 ended 상태이거나, 시청률이 95% 이상일 때 포인트 지급
            if payload.get('ended', False) or watch_percentage >= 95.0:
                st.session_state.points += 25
                st.session_state.video_completed_for_points = True
                st.success(f"✅ 영상 시청 완료! 포인트 25점 지급! 총 포인트: {st.session_state.points}점")
                st.balloons() # 축하 풍선 효과
                st.rerun() # 포인트 지급 후 UI 업데이트를 위해 앱 재실행

    except json.JSONDecodeError:
        st.warning("경고: JavaScript 메시지 디코딩 오류 발생. 메시지 형식 확인 필요.")
    except Exception as e:
        st.error(f"오류: Streamlit에서 데이터 처리 중 문제 발생: {e}")

# --- 4. 사용자 인터페이스 (진행률 바 & 포인트 표시) ---
st.markdown("---")
# 비디오 총 길이가 유효하면 그 값을 사용, 아니면 기본값 (예: 300초 = 5분)
display_duration = st.session_state.total_video_duration if st.session_state.total_video_duration > 0 else 300.0

progress_value = min(st.session_state.current_video_time / display_duration, 1.0)
st.progress(progress_value, text=f"시청 진행률: {progress_value * 100:.1f}% "
                                   f"({st.session_state.current_video_time:.1f}초 / {display_duration:.1f}초)")

st.metric("현재 획득 포인트", value=f"{st.session_state.points} 점")

st.markdown("---")
st.info("💡 비디오를 끝까지 시청하면 (95% 이상 시청 또는 종료 이벤트 발생) 포인트가 지급됩니다.")
st.caption("문제가 발생하면 브라우저 개발자 도구 (F12)의 'Console' 탭을 확인해주세요.")
