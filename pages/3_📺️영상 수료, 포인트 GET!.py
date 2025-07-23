import streamlit as st
import datetime
import time # sleep 함수를 위해 필요

st.set_page_config(layout="wide", page_title="영상 수강 포인트 시스템")

st.title("🎥 영상 수강 포인트 시스템 (버튼 기반)")
st.write("비디오를 시청하고 '시청 완료' 버튼을 눌러 포인트를 획득하세요.")

# --- 세션 변수 초기화 ---
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'video_started_at' not in st.session_state:
    st.session_state.video_started_at = None # 비디오 시청 시작 시간 기록
if 'video_completed_for_points' not in st.session_state:
    st.session_state.video_completed_for_points = False # 현재 세션에서 포인트 지급 여부

# 비디오 정보 (운영자가 관리)
VIDEO_URL = "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4"
VIDEO_DURATION_SECONDS = 758.0  # 비디오의 실제 길이 (약 12분 38초)를 직접 입력 (운영자 설정)
MIN_WATCH_PERCENTAGE = 0.95  # 최소 시청 비율 (95%)

# --- 1. 비디오 플레이어 ---
st.video(VIDEO_URL)

st.markdown("---")

# --- 2. 시청 시작 및 완료 버튼 ---
col1, col2 = st.columns(2)

# 시청 시작 버튼
with col1:
    if st.button("▶️ 시청 시작", key="start_watch", disabled=st.session_state.video_started_at is not None):
        st.session_state.video_started_at = datetime.datetime.now()
        st.session_state.video_completed_for_points = False # 다시 시작했으니 포인트 지급 플래그 초기화
        st.success("✅ 비디오 시청이 시작되었습니다! 끝까지 시청해주세요.")
        # UI 업데이트를 위해 다시 실행
        st.rerun()

# 시청 완료 버튼
with col2:
    # 시청 시작 기록이 없거나 이미 포인트가 지급되었다면 버튼 비활성화
    if st.button("✅ 시청 완료 및 포인트 받기", key="complete_watch",
                 disabled=st.session_state.video_started_at is None or st.session_state.video_completed_for_points):
        if st.session_state.video_started_at:
            time_watched_seconds = (datetime.datetime.now() - st.session_state.video_started_at).total_seconds()
            
            # 최소 시청 시간 (95% 기준)
            required_watch_time = VIDEO_DURATION_SECONDS * MIN_WATCH_PERCENTAGE

            st.markdown(f"**총 시청 시간:** {time_watched_seconds:.1f}초")
            st.markdown(f"**필요 시청 시간 (95%):** {required_watch_time:.1f}초")

            if time_watched_seconds >= required_watch_time:
                if not st.session_state.video_completed_for_points:
                    st.session_state.points += 25
                    st.session_state.video_completed_for_points = True
                    st.success(f"🎉 축하합니다! 비디오를 {time_watched_seconds:.1f}초 시청하여 25포인트를 받았습니다! 현재 총 포인트: {st.session_state.points}점")
                    st.balloons() # 축하 효과
                else:
                    st.info("이미 이 비디오로 포인트를 받으셨습니다.")
            else:
                st.warning(f"⚠️ 시청 시간이 부족합니다. 최소 {required_watch_time:.1f}초 이상 시청해야 합니다. (현재: {time_watched_seconds:.1f}초)")
        else:
            st.warning("먼저 '시청 시작' 버튼을 눌러주세요.")
        st.rerun() # UI 업데이트를 위해 다시 실행

# --- 3. 현재 시청 상태 및 포인트 표시 ---
st.markdown("---")

st.metric("현재 획득 포인트", value=f"{st.session_state.points} 점")

if st.session_state.video_started_at:
    elapsed_time = (datetime.datetime.now() - st.session_state.video_started_at).total_seconds()
    st.info(f"⏳ 비디오 시청 중... 경과 시간: {elapsed_time:.1f}초")
else:
    st.info("비디오 시청을 시작하려면 '시청 시작' 버튼을 눌러주세요.")

if st.session_state.video_completed_for_points:
    st.success("이 비디오는 성공적으로 시청 완료하여 포인트를 받았습니다.")

st.markdown("---")
st.caption("🚨 **주의**: 이 시스템은 사용자가 '시청 시작' 버튼을 누른 시점부터 '시청 완료' 버튼을 누른 시점까지의 시간을 기반으로 포인트를 지급합니다. 사용자가 실제로 비디오를 재생했는지 여부는 감지하지 않습니다. 운영자가 비디오의 실제 길이를 정확히 설정해야 합니다.")
st.caption("비디오 URL: " + VIDEO_URL)
