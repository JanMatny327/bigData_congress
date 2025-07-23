import streamlit as st
import datetime
import time # 지연 시간 시뮬레이션을 위해 필요

st.set_page_config(layout="wide", page_title="영상 수강 포인트 시스템 (안정화)")

st.title("🎥 영상 수강 포인트 시스템 (안정화 버전)")
st.write("각 비디오를 시청하고 '시청 완료' 버튼을 눌러 포인트를 획득하세요. 실제 시청 시간이 누적됩니다.")

# --- 세션 변수 초기화 ---
if 'total_points' not in st.session_state:
    st.session_state.total_points = 0

# 각 비디오의 상태를 딕셔너리로 관리
# key: video_id, value: {'accumulated_watch_time': float, 'last_play_start_time': datetime obj, 'points_awarded': bool}
if 'video_tracking' not in st.session_state:
    st.session_state.video_tracking = {}

# --- 비디오 목록 정의 (운영자 설정) ---
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

MIN_WATCH_PERCENTAGE = 0.90 # 최소 시청 비율 (예: 90%)

# 각 비디오의 초기 추적 상태 설정
for video_info in VIDEO_LIST:
    if video_info['id'] not in st.session_state.video_tracking:
        st.session_state.video_tracking[video_info['id']] = {
            'accumulated_watch_time': 0.0,  # 누적 시청 시간 (초)
            'last_play_start_time': None,   # 마지막으로 재생 시작한 시점 (datetime 객체)
            'points_awarded': False,        # 포인트 지급 여부
            'is_playing_flag': False        # 현재 재생 중인지 여부 (UI 피드백용)
        }

# --- 콜백 함수: 비디오 재생/정지 시 호출 (Streamlit 1.33.0 이상 권장) ---
def on_play_callback(video_id):
    if not st.session_state.video_tracking[video_id]['is_playing_flag']:
        st.session_state.video_tracking[video_id]['last_play_start_time'] = datetime.datetime.now()
        st.session_state.video_tracking[video_id]['is_playing_flag'] = True
        st.toast(f"▶️ '{video_id}' 재생 시작!", icon="▶️")
        # st.rerun() # 불필요한 reruns 방지

def on_pause_callback(video_id):
    tracking_info = st.session_state.video_tracking[video_id]
    if tracking_info['is_playing_flag'] and tracking_info['last_play_start_time']:
        # 현재 재생 세션 시간 계산 및 누적
        session_duration = (datetime.datetime.now() - tracking_info['last_play_start_time']).total_seconds()
        tracking_info['accumulated_watch_time'] += session_duration
        
        # 시작 시간 초기화 및 재생 플래그 변경
        tracking_info['last_play_start_time'] = None
        tracking_info['is_playing_flag'] = False
        st.toast(f"⏸️ '{video_id}' 재생 일시정지. 누적 시청 시간: {tracking_info['accumulated_watch_time']:.1f}초", icon="⏸️")
        check_and_award_points(video_id) # 일시정지/종료 시점마다 포인트 검사
        # st.rerun() # 불필요한 reruns 방지 (check_and_award_points에서 필요시 rerun)

def check_and_award_points(video_id):
    video_info = next(v for v in VIDEO_LIST if v['id'] == video_id)
    tracking_info = st.session_state.video_tracking[video_id]

    if tracking_info['points_awarded']:
        return # 이미 포인트 지급됨

    # 예상 길이 대비 누적 시청 비율 계산
    watch_percentage = tracking_info['accumulated_watch_time'] / video_info['expected_duration']
    
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
    # Streamlit 1.33.0 이상에서만 on_play/on_pause 콜백이 지원됩니다.
    st.video(
        video_info['url'],
        start_time=0,
        key=f"st_video_{video_id}",
        on_play=lambda vid=video_id: on_play_callback(vid),
        on_pause=lambda vid=video_id: on_pause_callback(vid)
        # on_ended 콜백은 현재 st.video에 없음, on_pause에서 비디오 종료 처리
    )

    # 현재 누적 시청 시간과 진행률 표시
    st.progress(
        min(tracking_info['accumulated_watch_time'] / video_info['expected_duration'], 1.0),
        text=f"누적 시청 시간: {tracking_info['accumulated_watch_time']:.1f}초 / 총 {video_info['expected_duration']:.1f}초 "
             f"({(tracking_info['accumulated_watch_time'] / video_info['expected_duration']) * 100:.1f}%)"
    )

    # 시청 완료 버튼 (수동 트리거)
    # 이미 포인트가 지급되었거나, 현재 재생 중일 때는 버튼 비활성화
    if st.button(
        f"✅ {video_info['title']} 시청 완료 확인",
        key=f"complete_btn_{video_id}",
        disabled=tracking_info['points_awarded'] or tracking_info['is_playing_flag']
    ):
        # 버튼을 누르면 강제로 시청 시간 누적 및 포인트 확인
        # 현재 재생 중이지 않다면, 마지막 재생 세션이 on_pause에서 처리되지 않았을 때를 대비
        if tracking_info['last_play_start_time']:
            session_duration = (datetime.datetime.now() - tracking_info['last_play_start_time']).total_seconds()
            tracking_info['accumulated_watch_time'] += session_duration
            tracking_info['last_play_start_time'] = None
            tracking_info['is_playing_flag'] = False
        
        check_and_award_points(video_id)
        st.rerun() # 버튼 클릭 후 UI 업데이트

    if tracking_info['points_awarded']:
        st.success(f"✅ 이 영상으로 {video_info['points']} 포인트를 이미 획득했습니다.")
    else:
        st.info("비디오를 충분히 시청하고 '시청 완료 확인' 버튼을 눌러주세요.")
    st.markdown("---")

# --- 총 포인트 표시 ---
st.markdown("---")
st.metric("현재 총 획득 포인트", value=f"{st.session_state.total_points} 점")
st.markdown("---")
st.info("💡 각 영상의 누적 시청 시간이 설정된 비율(예: 90%)을 넘거나 '시청 완료 확인' 버튼을 누르면 포인트가 지급됩니다.")
st.caption("🚨 **주의**: 이 시스템은 Streamlit의 `st.video` `on_play`/`on_pause` 콜백을 사용합니다. 이전 버전에서는 재생/일시정지 감지가 작동하지 않을 수 있습니다. 수동 '시청 완료 확인' 버튼이 주요 검증 수단입니다.")
