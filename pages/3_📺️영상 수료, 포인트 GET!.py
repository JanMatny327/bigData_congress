import streamlit as st
import datetime
import time # sleep 함수를 위해 필요

st.set_page_config(layout="wide", page_title="비디오 시청 포인트")

st.title("🎥 비디오 시청 학습 시스템")
st.markdown("비디오를 시청하고, 시작과 종료 시간을 기준으로 포인트를 획득하세요.")

# --- 세션 변수 초기화 ---
if 'total_points' not in st.session_state:
    st.session_state.total_points = 0

# 각 비디오의 상태를 딕셔너리로 관리
# key: video_id, value: {'start_time': datetime obj, 'end_time': datetime obj, 'watched_duration': float, 'points_awarded': bool}
if 'video_tracking' not in st.session_state:
    st.session_state.video_tracking = {}

# --- 비디오 목록 정의 (운영자 설정) ---
VIDEO_LIST = [
    {"id": "video_a", "title": "소방 안전 수칙 (화재 예방편)",
     "url": "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4",
     "expected_duration": 758.0, "points": 25}, # 약 12분 38초
    {"id": "video_b", "title": "지진 발생 시 대처 요령",
     "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
     "expected_duration": 596.0, "points": 20}, # 약 9분 56초 (샘플 영상)
    {"id": "video_c", "title": "응급처치 기본 교육",
     "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
     "expected_duration": 15.0, "points": 10}, # 약 15초 (짧은 샘플 영상)
]

MIN_WATCH_PERCENTAGE = 0.90 # 최소 시청 비율 (예: 90%)

# 각 비디오의 초기 추적 상태 설정
for video_info in VIDEO_LIST:
    if video_info['id'] not in st.session_state.video_tracking:
        st.session_state.video_tracking[video_info['id']] = {
            'start_time': None,
            'end_time': None,
            'watched_duration': 0.0,
            'points_awarded': False,
            'is_playing': False # 현재 비디오가 재생 중인지 (streamlit 1.33.0 이상에서만 가능)
        }

# --- 비디오 이벤트 콜백 함수 (Streamlit 1.33.0 이상에서 play/pause 이벤트 감지) ---
# 이 부분은 Streamlit 버전 1.33.0 이상에서 st.video의 on_play/on_pause 콜백 함수를 지원할 때 동작합니다.
# 만약 이전 버전이라면 이 콜백 함수들은 호출되지 않습니다.
def handle_play_event(video_id):
    if not st.session_state.video_tracking[video_id]['is_playing']:
        st.session_state.video_tracking[video_id]['start_time'] = datetime.datetime.now()
        st.session_state.video_tracking[video_id]['is_playing'] = True
        st.toast(f"▶️ '{video_id}' 재생 시작!", icon="▶️")
        # st.rerun() # 불필요한 reruns 방지

def handle_pause_event(video_id):
    if st.session_state.video_tracking[video_id]['is_playing']:
        current_pause_time = datetime.datetime.now()
        start_time = st.session_state.video_tracking[video_id]['start_time']
        
        # 일시정지 또는 종료 시 시청 시간 누적
        if start_time:
            session_duration = (current_pause_time - start_time).total_seconds()
            st.session_state.video_tracking[video_id]['watched_duration'] += session_duration
            st.session_state.video_tracking[video_id]['start_time'] = None # 다음 재생을 위해 시작 시간 초기화
        
        st.session_state.video_tracking[video_id]['is_playing'] = False
        st.toast(f"⏸️ '{video_id}' 재생 일시정지.", icon="⏸️")
        check_and_award_points(video_id) # 일시정지/종료 시점마다 포인트 검사
        # st.rerun() # 불필요한 reruns 방지

def check_and_award_points(video_id):
    video_info = next(v for v in VIDEO_LIST if v['id'] == video_id)
    tracking_info = st.session_state.video_tracking[video_id]

    if tracking_info['points_awarded']:
        return # 이미 포인트 지급됨

    # 예상 길이 대비 시청 비율 계산
    watch_percentage = tracking_info['watched_duration'] / video_info['expected_duration']
    
    # 90% 이상 시청했으면 포인트 지급 (또는 다른 조건: 비디오 끝까지 시청)
    if watch_percentage >= MIN_WATCH_PERCENTAGE:
        st.session_state.total_points += video_info['points']
        tracking_info['points_awarded'] = True
        st.success(f"🎉 '{video_info['title']}' 시청 완료! {video_info['points']} 포인트를 획득했습니다!")
        st.balloons() # 축하 효과
        st.rerun() # UI 업데이트를 위해 앱 재실행


# --- UI 렌더링 ---
for video_info in VIDEO_LIST:
    video_id = video_info['id']
    tracking_info = st.session_state.video_tracking[video_id]

    st.subheader(f"🎬 {video_info['title']}")
    
    # st.video 컴포넌트 사용 (key와 on_play/on_pause 콜백 연결)
    st.video(
        video_info['url'],
        start_time=0,
        key=f"st_video_{video_id}",
        on_play=lambda vid=video_id: handle_play_event(vid),
        on_pause=lambda vid=video_id: handle_pause_event(vid)
        # on_ended 콜백은 현재 st.video에 없음, on_pause에서 처리하거나 수동 확인 필요
    )

    # 현재 시청 시간 표시 (누적)
    st.progress(
        min(tracking_info['watched_duration'] / video_info['expected_duration'], 1.0),
        text=f"누적 시청 시간: {tracking_info['watched_duration']:.1f}초 / 총 {video_info['expected_duration']:.1f}초 "
             f"({(tracking_info['watched_duration'] / video_info['expected_duration']) * 100:.1f}%)"
    )

    if tracking_info['points_awarded']:
        st.success(f"✅ 이 영상으로 {video_info['points']} 포인트를 이미 획득했습니다.")
    else:
        st.info("시청 완료 시 포인트가 지급됩니다.")
    st.markdown("---")

# --- 총 포인트 표시 ---
st.markdown("---")
st.metric("현재 총 획득 포인트", value=f"{st.session_state.total_points} 점")
st.markdown("---")
st.info("💡 각 영상의 누적 시청 시간이 설정된 비율(예: 90%)을 넘으면 포인트가 지급됩니다.")
st.caption("🚨 **주의**: 이 시스템은 Streamlit 1.33.0 이상 버전의 `st.video` `on_play`/`on_pause` 콜백 기능을 사용합니다. 이전 버전에서는 재생/일시정지 감지가 작동하지 않을 수 있습니다.")
st.caption("비디오가 **완전히 종료**될 경우에도 `on_pause` 이벤트가 발생하며, 이때 최종적으로 시청 시간이 누적되고 포인트 지급 여부를 확인합니다.")
