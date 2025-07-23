import streamlit as st
from streamlit.components.v1 import html
import json # JavaScript에서 JSON 문자열을 받아 파싱하기 위해 필요

st.set_page_config(layout="wide", page_title="영상 수강 & 포인트 지급")

st.title("🎥 자동 영상 수강 시간 감지 & 포인트 지급 (PostMessage 방식)")

# --- 세션 변수 초기화 ---
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'video_watched_for_points' not in st.session_state:
    st.session_state.video_watched_for_points = False # 포인트 지급 여부 추적
if 'current_play_time' not in st.session_state:
    st.session_state.current_play_time = 0.0
if 'video_total_duration' not in st.session_state:
    st.session_state.video_total_duration = 0.0
if 'last_video_state_json' not in st.session_state:
    st.session_state.last_video_state_json = "" # JS에서 받은 마지막 JSON 문자열 저장

# --- 비디오 URL ---
VIDEO_URL = "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4"

# --- 1. 비디오 플레이어 및 JavaScript 송신 로직 ---
# JavaScript에서 비디오의 현재 상태를 주기적으로 Streamlit으로 전달
video_player_html = f"""
<video id="myVideoPlayer" width="100%" height="auto" controls src="{VIDEO_URL}">
    <source src="{VIDEO_URL}" type="video/mp4">
    Your browser does not support the video tag.
</video>
<script>
    const video = document.getElementById('myVideoPlayer');

    // 1초마다 현재 시간, 총 길이, 종료 여부 등 상태를 JSON 형태로 부모에게 전송
    setInterval(() => {{
        // video 요소가 존재하고, 최소한 메타데이터가 로드되어 재생 가능할 때만 메시지 전송
        if (video && video.readyState > 0) {{
            const videoState = {{
                currentTime: video.currentTime,
                duration: video.duration,
                ended: video.ended
            }};
            // 부모 Streamlit 앱으로 메시지 전송
            window.parent.postMessage({{
                type: 'video_status_update',
                payload: videoState
            }}, '*');
            // console.log('JS sent video_status_update:', videoState.currentTime.toFixed(1)); // 디버깅용
        }}
    }}, 1000); // 1초마다 전송

    // 비디오가 완전히 끝났을 때 명시적으로 알림 (안전 장치)
    video.addEventListener('ended', () => {{
        window.parent.postMessage({{
            type: 'video_ended_event',
            payload: {{ ended: true }}
        }}, '*');
        // console.log('JS sent video_ended_event'); // 디버깅용
    }});

    // 비디오 메타데이터가 로드되었을 때 총 길이를 즉시 전송
    video.addEventListener('loadedmetadata', () => {{
        window.parent.postMessage({{
            type: 'video_metadata_loaded',
            payload: {{ duration: video.duration }}
        }}, '*');
        // console.log('JS sent video_metadata_loaded:', video.duration.toFixed(1)); // 디버깅용
    }});

</script>
"""
st.components.v1.html(video_player_html, height=400)

# --- 2. JavaScript 메시지 수신 및 Streamlit으로 전달 (숨겨진 input 활용) ---
# 이 HTML 컴포넌트는 Streamlit 앱의 DOM에 숨겨진 input을 생성하고,
# 비디오 플레이어로부터 받은 메시지를 이 input의 값으로 업데이트한 후
# input 이벤트를 발생시켜 Streamlit이 재실행되도록 합니다.
message_receiver_html = """
<script>
window.addEventListener("message", (event) => {
    // 보안 강화를 위해 특정 origin만 허용하려면 event.origin을 확인하세요 (예: "http://localhost:8501")
    // if (event.origin !== "http://localhost:8501") return;

    // 비디오 플레이어에서 온 메시지인지 확인
    if (event.data && (event.data.type === 'video_status_update' ||
                       event.data.type === 'video_ended_event' ||
                       event.data.type === 'video_metadata_loaded')) {
        const inputElement = window.parent.document.querySelector('input[data-testid="video_message_receiver"]');
        if (inputElement) {
            // 메시지 페이로드를 JSON 문자열로 변환하여 input 값에 할당
            inputElement.value = JSON.stringify(event.data);
            // input 이벤트를 강제로 발생시켜 Streamlit 앱의 재실행을 유도
            inputElement.dispatchEvent(new Event('input', { bubbles: true }));
            // console.log('JS received message and dispatched input:', event.data.type); // 디버깅용
        }
    }
});
</script>
<input type="text" data-testid="video_message_receiver" style="display:none;" />
"""
st.components.v1.html(message_receiver_html, height=0) # 화면에 보이지 않도록 height=0

# --- 3. Streamlit Python 코드에서 메시지 수신 및 처리 ---
# 숨겨진 input의 변경된 값을 읽어옵니다.
received_message_json = st.text_input(
    "Hidden Video Message Receiver",
    key="video_message_receiver", # data-testid와 동일한 key
    label_visibility="collapsed" # UI에서 숨김
)

# 이전에 받은 메시지와 다를 경우에만 처리하여 불필요한 재실행 및 로직 중복 실행 방지
if received_message_json and received_message_json != st.session_state.last_video_state_json:
    try:
        data = json.loads(received_message_json)
        st.session_state.last_video_state_json = received_message_json # 마지막으로 처리한 메시지 업데이트

        # st.write(f"Python received data: {data}") # Python에서 데이터 수신 확인용

        if data.get('type') == 'video_status_update':
            payload = data.get('payload', {})
            st.session_state.current_play_time = payload.get('currentTime', 0.0)
            if payload.get('duration', 0.0) > 0: # 총 길이가 유효하면 업데이트
                st.session_state.video_total_duration = payload.get('duration', 0.0)

            # 포인트 지급 로직 (현재 시간 기반)
            if st.session_state.video_total_duration > 0 and not st.session_state.video_watched_for_points:
                watch_percentage = (st.session_state.current_play_time / st.session_state.video_total_duration) * 100

                # 95% 이상 시청했거나, JS에서 'ended'라고 명시적으로 알린 경우
                if watch_percentage >= 95.0 or payload.get('ended', False):
                    st.session_state.points += 25
                    st.session_state.video_watched_for_points = True
                    st.success(f"✅ 영상 시청 완료! 포인트 25점 지급! 총 포인트: {st.session_state.points}점")
                    st.balloons() # 축하 효과
                    # 포인트 지급 후 상태 업데이트를 위해 Streamlit 재실행 유도
                    st.rerun()

        elif data.get('type') == 'video_ended_event':
            # 'ended' 이벤트가 명시적으로 발생했을 때 (중복 방지를 위한 2차 확인)
            if not st.session_state.video_watched_for_points:
                st.session_state.points += 25
                st.session_state.video_watched_for_points = True
                st.success(f"✅ 영상 시청 완료! 포인트 25점 지급! 총 포인트: {st.session_state.points}점 (이벤트 완료)")
                st.balloons()
                st.rerun()

        elif data.get('type') == 'video_metadata_loaded':
            # 비디오 메타데이터 로드 시 총 길이 업데이트 (초기 로딩 시 정확한 총 길이 파악)
            payload = data.get('payload', {})
            if payload.get('duration', 0.0) > 0:
                st.session_state.video_total_duration = payload.get('duration', 0.0)

    except json.JSONDecodeError:
        st.warning("JSON 메시지 디코딩 오류가 발생했습니다. 예상치 못한 데이터: " + received_message_json)
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")

# --- 4. 사용자 인터페이스 (진행률 바 & 포인트 표시) ---
st.markdown("---")
# 비디오 총 길이가 유효하면 그 값을 사용, 아니면 기본값 (예: 300초 = 5분)
display_total_duration = st.session_state.video_total_duration if st.session_state.video_total_duration > 0 else 300

progress_value = min(st.session_state.current_play_time / display_total_duration, 1.0)
st.progress(progress_value, text=f"시청 진행률: {progress_value * 100:.1f}% "
                                   f"({st.session_state.current_play_time:.1f}초 / {display_total_duration:.1f}초)")

st.metric("현재 획득 포인트", value=f"{st.session_state.points} 점")

st.markdown("---")
st.info("💡 비디오를 끝까지 시청하면 (95% 이상 시청 또는 종료 이벤트 발생) 포인트가 지급됩니다.")
st.caption("참고: 브라우저 환경 및 네트워크 상태에 따라 반응 속도가 달라질 수 있습니다.")
