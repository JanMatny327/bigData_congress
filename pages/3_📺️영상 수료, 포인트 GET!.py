import streamlit as st
import datetime

# 페이지 설정: 넓은 레이아웃으로 설정하여 비디오를 더 잘 볼 수 있게 합니다.
st.set_page_config(layout="wide", page_title="영상 수강 & 포인트 GET!")

st.title("🎥 자동 영상 수강 시간 감지 & 포인트 지급")
st.write("각 비디오를 시청하고 **'시청 완료 확인' 버튼**을 눌러 포인트를 획득하세요. 획득한 포인트는 안전 관련 물품 구매에 사용될 수 있습니다.") [cite: 9]

# --- 1. 세션 변수 초기화 ---
# Streamlit의 session_state를 사용하여 앱 재실행 시에도 데이터가 유지되도록 합니다.
if 'total_points' not in st.session_state:
    st.session_state.total_points = 0

# 각 비디오의 시청 완료 상태를 추적하는 딕셔너리입니다.
# key: video_id, value: {'points_awarded': bool}
if 'video_completion_status' not in st.session_state:
    st.session_state.video_completion_status = {}

# --- 2. 비디오 목록 정의 (운영자 설정) ---
# 기획서의 '안전교육 콘텐츠(영상)'  에 해당하며, 실제 영상 URL과 획득 포인트를 정의합니다.
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

# 각 비디오의 초기 완료 상태를 세션 상태에 설정합니다.
for video_info in VIDEO_LIST:
    if video_info['id'] not in st.session_state.video_completion_status:
        st.session_state.video_completion_status[video_info['id']] = {
            'points_awarded': False
        }

# --- 3. 비디오 플레이어 및 '시청 완료' 버튼 렌더링 ---
# 각 비디오에 대해 플레이어와 완료 버튼을 생성합니다.
for video_info in VIDEO_LIST:
    video_id = video_info['id']
    completion_status = st.session_state.video_completion_status[video_id]

    st.subheader(f"🎬 {video_info['title']}")
    
    # 비디오 URL의 유효성을 검증하여 오류를 방지합니다.
    video_url = video_info.get('url')
    if not isinstance(video_url, str) or not video_url:
        st.error(f"⚠️ 오류: '{video_info.get('title', '알 수 없는 영상')}' 영상의 URL이 없거나 유효하지 않습니다. URL: `{video_url}`")
        st.markdown("---") 
        continue 

    try:
        # Streamlit의 비디오 컴포넌트를 사용하여 영상을 임베드합니다.
        st.video(
            video_url,
            start_time=0, # 비디오가 0초부터 시작하도록 설정
            key=f"st_video_{video_id}" # 각 비디오 컴포넌트에 고유한 키를 부여하여 Streamlit이 상태를 관리할 수 있도록 합니다.
        )
    except Exception as e:
        # 비디오 로딩 중 발생할 수 있는 오류를 처리하고 사용자에게 알립니다.
        st.error(f"❌ '{video_info.get('title', '알 수 없는 영상')}' 영상 로딩 중 심각한 오류 발생: `{e}`")
        st.info("💡 위 오류는 주로 Streamlit 버전이 낮거나, 비디오 URL 접근에 문제가 있을 때 발생합니다.")
        st.markdown("---")
        continue

    # '시청 완료 확인' 버튼을 생성합니다.
    if st.button(
        f"✅ {video_info['title']} 시청 완료 확인",
        key=f"complete_btn_{video_id}", # 각 버튼에 고유한 키를 부여합니다.
        disabled=completion_status['points_awarded'] # 해당 비디오의 포인트가 이미 지급되었다면 버튼을 비활성화합니다.
    ):
        if not completion_status['points_awarded']: # 중복 포인트 지급을 방지합니다.
            st.session_state.total_points += video_info['points'] # 총 포인트를 증가시킵니다.
            completion_status['points_awarded'] = True # 해당 비디오의 완료 상태를 '포인트 지급됨'으로 변경합니다.
            st.success(f"🎉 '{video_info['title']}' 시청 완료! {video_info['points']} 포인트를 획득했습니다!")
            st.balloons() # 축하 풍선 효과를 표시합니다.
            st.rerun() # 앱 UI를 업데이트하여 변경된 상태를 즉시 반영합니다.

    # 현재 비디오의 포인트 지급 상태를 사용자에게 표시합니다.
    if completion_status['points_awarded']:
        st.success(f"✅ 이 영상으로 {video_info['points']} 포인트를 이미 획득했습니다.")
    else:
        st.info("비디오를 시청한 후 '시청 완료 확인' 버튼을 눌러주세요.")
    st.markdown("---")

# --- 4. 총 포인트 표시 ---
# 사용자가 획득한 총 포인트를 표시합니다.
st.markdown("---")
st.metric("현재 총 획득 포인트", value=f"{st.session_state.total_points} 점")
st.markdown("---")
st.info("💡 각 비디오를 시청하고 '시청 완료 확인' 버튼을 누르면 포인트가 지급됩니다.")
st.caption("🚨 **참고**: 이 버전은 사용자가 직접 '시청 완료 확인' 버튼을 눌러야 포인트가 지급됩니다. 비디오 재생 시간을 자동 감지하지 않습니다.")
