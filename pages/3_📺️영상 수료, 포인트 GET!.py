import streamlit as st
import datetime

st.set_page_config(layout="wide", page_title="영상 수료 포인트 (최종)")

st.title("🎥 영상 수료 포인트 시스템 (최종 안정화 버전)")
st.write("각 비디오를 시청하고 **'시청 완료 확인' 버튼**을 눌러 포인트를 획득하세요.")

# --- 1. 세션 변수 초기화 ---
if 'total_points' not in st.session_state:
    st.session_state.total_points = 0

# 각 비디오의 상태를 딕셔너리로 관리
# key: video_id, value: {'points_awarded': bool}
if 'video_completion_status' not in st.session_state:
    st.session_state.video_completion_status = {}

# --- 2. 비디오 목록 정의 (운영자 설정) ---
# 제공된 URL들이 웹에서 직접 접근 가능한지 다시 한번 확인해주세요.
VIDEO_LIST = [
    {"id": "video1", "title": "소방 안전 수칙 (화재 예방편)",
     "url": "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4",
     "points": 25},
    {"id": "video2", "title": "지진 발생 시 대처 요령",
     "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
     "points": 20},
    {"id": "video3", "title": "응급처치 기본 교육",
     "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
     "points": 10},
]

# 각 비디오의 초기 완료 상태 설정
for video_info in VIDEO_LIST:
    if video_info['id'] not in st.session_state.video_completion_status:
        st.session_state.video_completion_status[video_info['id']] = {
            'points_awarded': False
        }

# --- 3. 비디오 플레이어 및 '시청 완료' 버튼 렌더링 ---
for video_info in VIDEO_LIST:
    video_id = video_info['id']
    completion_status = st.session_state.video_completion_status[video_id]

    st.subheader(f"🎬 {video_info['title']}")
    
    # URL 값에 대한 강력한 검증 및 에러 처리
    video_url = video_info.get('url')
    
    # URL이 존재하고, 문자열이며, 비어있지 않은지 확인
    if not isinstance(video_url, str) or not video_url:
        st.error(f"⚠️ 오류: '{video_info.get('title', '알 수 없는 영상')}' 영상의 URL이 없거나 유효하지 않습니다. URL: `{video_url}`")
        st.markdown("---") 
        continue 

    try:
        # st.video 컴포넌트 사용 (key 인자는 최신 Streamlit에서 지원)
        st.video(
            video_url,
            start_time=0, 
            key=f"st_video_{video_id}" # 이 'key' 인자가 이전 Streamlit 버전에서 문제 발생
        )
    except Exception as e:
        # st.video 자체에서 발생하는 예외를 잡아서 구체적인 에러 메시지를 출력
        st.error(f"❌ '{video_info.get('title', '알 수 없는 영상')}' 영상 로딩 중 심각한 오류 발생: `{e}`")
        st.info("💡 위 오류는 주로 Streamlit 버전이 낮거나, 비디오 URL 접근에 문제가 있을 때 발생합니다.")
        st.markdown("---")
        continue

    # '시청 완료 확인' 버튼
    if st.button(
        f"✅ {video_info['title']} 시청 완료 확인",
        key=f"complete_btn_{video_id}",
        disabled=completion_status['points_awarded']
    ):
        if not completion_status['points_awarded']:
            st.session_state.total_points += video_info['points']
            completion_status['points_awarded'] = True
            st.success(f"🎉 '{video_info['title']}' 시청 완료! {video_info['points']} 포인트를 획득했습니다!")
            st.balloons()
            st.rerun()

    if completion_status['points_awarded']:
        st.success(f"✅ 이 영상으로 {video_info['points']} 포인트를 이미 획득했습니다.")
    else:
        st.info("비디오를 시청한 후 '시청 완료 확인' 버튼을 눌러주세요.")
    st.markdown("---")

# --- 4. 총 포인트 표시 ---
st.markdown("---")
st.metric("현재 총 획득 포인트", value=f"{st.session_state.total_points} 점")
st.markdown("---")
st.info("💡 각 비디오를 시청하고 '시청 완료 확인' 버튼을 누르면 포인트가 지급됩니다.")
st.caption("🚨 **참고**: 이 버전은 사용자가 직접 '시청 완료 확인' 버튼을 눌러야 포인트가 지급됩니다. 비디오 재생 시간을 자동 감지하지 않습니다.")
