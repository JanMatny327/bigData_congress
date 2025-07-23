import streamlit as st
from streamlit.components.v1 import html
import json

st.set_page_config(layout="wide", page_title="다중 영상 시청 & 포인트")

st.title("🎥 다중 영상 학습 및 포인트 획득")
st.markdown("각 영상을 시청하고 시청 완료 조건을 충족하면 포인트를 획득합니다.")

# --- 1. 세션 변수 초기화 ---
if 'total_points' not in st.session_state:
    st.session_state.total_points = 0

# 각 비디오의 상태를 딕셔너리로 관리
# key: video_id, value: {'watched_for_points': bool, 'current_time': float, 'duration': float}
if 'video_statuses' not in st.session_state:
    st.session_state.video_statuses = {}

# JavaScript로부터 받은 최신 메시지를 저장 (중복 처리 방지용)
if 'last_js_message' not in st.session_state:
    st.session_state.last_js_message = ""

# --- 2. 비디오 목록 정의 (운영자 설정) ---
# 비디오 ID를 고유하게 부여하고, URL과 예상 길이를 지정합니다.
VIDEO_LIST = [
    {"id": "video1", "title": "소방 안전 수칙 (화재 예방편)",
     "url": "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4",
     "expected_duration": 758.0, "points": 25}, # 약 12분 38초
    {"id": "video2", "title": "지진 발생 시 대처 요령",
     "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
     "expected_duration": 596.0, "points": 20}, # 약 9분 56초 (샘플 영상)
    {"id": "video3", "title": "응급처치 기본 교육",
     "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
     "expected_duration": 15.0, "points": 10}, # 약 15초 (짧은 샘플 영상)
]

MIN_WATCH_PERCENTAGE_FOR_POINTS = 0.95 # 95% 이상 시청 시 포인트 지급

# 각 비디오의 초기 상태 설정 또는 업데이트
for video_info in VIDEO_LIST:
    if video_info['id'] not in st.session_state.video_statuses:
        st.session_state.video_statuses[video_info['id']] = {
            'watched_for_points': False,
            'current_time': 0.0,
            'duration': video_info['expected_duration'] # 초기에는 예상 길이로 설정
        }

# --- 3. 비디오 플레이어 및 JavaScript 통신 로직 ---
# 이 함수는 각 비디오마다 HTML 컴포넌트를 생성하여 페이지에 표시합니다.
def render_video_player(video_id, video_url):
    html_content = f"""
    <div id="video_container_{video_id}" style="margin-bottom: 20px;">
        <video id="player_{video_id}" width="100%" height="auto" controls playsinline src="{video_url}">
            <source src="{video_url}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div id="debug_info_{video_id}" style="font-size: 0.8em; color: #666;"></div>
    </div>
    <script>
        // 현재 스크립트가 실행되는 iframe 내의 비디오 및 숨겨진 input을 찾습니다.
        const video = document.getElementById('player_{video_id}');
        // Streamlit 메인 앱의 input을 찾기 위해 window.parent를 사용합니다.
        const hiddenInput = window.parent.document.querySelector('input[data-testid="video_status_receiver"]');
        const debugDiv = document.getElementById('debug_info_{video_id}');

        console.log(`JS {video_id}: Script loaded.`);
        if (!video) console.error(`JS Error {video_id}: Video element not found!`);
        if (!hiddenInput) console.error(`JS Error {video_id}: Hidden input for Streamlit not found!`);

        function sendToStreamlit(type, payload) {{
            if (hiddenInput) {{
                const message = {{
                    type: type,
                    video_id: '{video_id}', // 어떤 비디오에서 온 메시지인지 명확히 표시
                    payload: payload
                }};
                hiddenInput.value = JSON.stringify(message);
                hiddenInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                // console.log(`JS {video_id}: Sent ${{type}}`, JSON.stringify(payload)); // 디버깅: 너무 많이 출력될 수 있음
            }}
        }}

        // 'timeupdate' 이벤트는 너무 자주 발생하므로, 1초 간격으로 제한합니다.
        let lastTimeUpdate = 0;
        const TIME_UPDATE_INTERVAL = 1000; // 1초 (밀리초)

        if (video) {{
            video.addEventListener('loadedmetadata', () => {{
                console.log(`JS {video_id}: loadedmetadata, duration: ${{video.duration}}`);
                sendToStreamlit('metadata', {{ duration: video.duration }});
            }});

            video.addEventListener('timeupdate', () => {{
                const currentTime = video.currentTime;
                // 이전 업데이트로부터 1초 이상 경과했을 때만 Streamlit으로 전송
                if ((currentTime * 1000) - lastTimeUpdate >= TIME_UPDATE_INTERVAL) {{
                    sendToStreamlit('update', {{
                        currentTime: currentTime,
                        duration: video.duration, // 현재 감지된 비디오 총 길이도 함께 보냄
                        ended: video.ended
                    }});
                    lastTimeUpdate = currentTime * 1000;
                }
                if (debugDiv) {{
                    debugDiv.textContent = `현재 시간: ${{currentTime.toFixed(1)}}초 / 총 길이: ${{video.duration.toFixed(1)}}초`;
                }}
            }});

            video.addEventListener('ended', () => {{
                console.log(`JS {video_id}: Video ended.`);
                sendToStreamlit('ended', {{ ended: true, currentTime: video.duration, duration: video.duration }});
            }});
        }}
    </script>
    """
    # 각 비디오마다 고유한 HTML 컴포넌트를 렌더링
    st.components.v1.html(html_content, height=st.session_state.video_statuses[video_id]['duration'] / 758 * 400 + 50) # 비디오 길이에 따라 높이 조절 + 디버그 div 높이
    # 위 height 계산식은 예시이며, 실제 비디오 비율에 따라 조정해야 합니다.
    # 일반적으로 고정 높이 400~500px 정도가 적당합니다.
    # st.components.v1.html(html_content, height=450) # 고정 높이 사용 예시

# 모든 비디오 플레이어를 렌더링
for video_info in VIDEO_LIST:
    st.subheader(f"🎬 {video_info['title']}")
    render_video_player(video_info['id'], video_info['url'])
    # 각 비디오 아래에 포인트 지급 상태 및 진행률 표시
    status = st.session_state.video_statuses[video_info['id']]
    display_duration = status['duration'] if status['duration'] > 0 else video_info['expected_duration']
    
    progress_val = min(status['current_time'] / display_duration, 1.0) if display_duration > 0 else 0.0
    st.progress(progress_val, text=f"시청 진행률: {progress_val * 100:.1f}% "
                                     f"({status['current_time']:.1f}초 / {display_duration:.1f}초)")
    
    if status['watched_for_points']:
        st.success(f"✅ 이 영상으로 {video_info['points']} 포인트를 획득했습니다.")
    else:
        st.info("시청 완료 시 포인트가 지급됩니다.")
    st.markdown("---")


# --- 4. Streamlit Python 코드에서 메시지 수신 및 처리 ---
# JavaScript에서 각 비디오의 상태 업데이트 메시지를 받을 숨겨진 input
# 이 input은 페이지 전체에서 단 하나만 존재합니다.
received_message_str = st.text_input(
    "Hidden Video Status Receiver",
    key="video_status_receiver",
    label_visibility="collapsed"
)

# JavaScript에서 새로운 메시지를 받았을 때만 처리 (중복 실행 방지)
if received_message_str and received_message_str != st.session_state.last_js_message:
    try:
        data = json.loads(received_message_str)
        st.session_state.last_js_message = received_message_str # 마지막 처리된 메시지 저장

        video_id = data.get('video_id')
        message_type = data.get('type')
        payload = data.get('payload', {})

        if video_id and video_id in st.session_state.video_statuses:
            current_video_status = st.session_state.video_statuses[video_id]

            # st.write(f"Py Received: ID={video_id}, Type={message_type}, Payload={payload}") # 디버깅용

            if message_type == 'metadata':
                if payload.get('duration', 0.0) > 0:
                    current_video_status['duration'] = payload['duration']
            
            elif message_type == 'update':
                current_video_status['current_time'] = payload.get('currentTime', 0.0)
                if payload.get('duration', 0.0) > 0:
                    current_video_status['duration'] = payload['duration']

            elif message_type == 'ended':
                # 영상이 끝났다는 메시지를 받으면, 총 길이를 현재 시간으로 설정하여 100% 시청으로 간주
                current_video_status['current_time'] = payload.get('duration', 0.0) # 총 길이로 설정
                if payload.get('duration', 0.0) > 0:
                    current_video_status['duration'] = payload['duration'] # 최종 길이 업데이트

            # --- 포인트 지급 로직 (모든 메시지 타입 후 공통 검증) ---
            # 아직 포인트가 지급되지 않았고, 비디오 총 길이가 유효한 경우에만 검증
            if not current_video_status['watched_for_points'] and current_video_status['duration'] > 0:
                watch_percentage = (current_video_status['current_time'] / current_video_status['duration'])
                
                # 시청 완료 기준 충족 시 포인트 지급
                if watch_percentage >= MIN_WATCH_PERCENTAGE_FOR_POINTS:
                    st.session_state.total_points += next(v['points'] for v in VIDEO_LIST if v['id'] == video_id)
                    current_video_status['watched_for_points'] = True # 해당 비디오 포인트 지급 완료 플래그
                    st.toast(f"🎉 {video_id} 영상 시청 완료! 포인트 획득!", icon="🎈")
                    st.rerun() # UI 업데이트 및 재실행

    except json.JSONDecodeError:
        st.warning("경고: JavaScript 메시지 디코딩 오류 발생. 메시지 형식 확인 필요.")
    except Exception as e:
        st.error(f"오류: Streamlit에서 데이터 처리 중 문제 발생: {e}")

# --- 5. 총 포인트 표시 ---
st.markdown("---")
st.metric("현재 총 획득 포인트", value=f"{st.session_state.total_points} 점")
st.markdown("---")
st.info("💡 각 영상의 시청률이 95%를 넘거나 영상이 끝까지 재생되면 해당 영상에 대한 포인트가 지급됩니다.")
st.caption("🚨 **주의**: 이 시스템은 클라이언트 측 JavaScript 감지에 의존하므로, 브라우저 환경이나 네트워크 상태에 따라 오차가 발생할 수 있습니다. 운영자는 `VIDEO_LIST`의 'expected_duration'을 정확히 설정하는 것이 중요합니다.")
