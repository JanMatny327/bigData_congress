import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide", page_title="영상 수강 & 포인트 지급")

st.title("🎥 자동 영상 수강 시간 감지 & 포인트 지급 (새로운 로직)")

# --- 세션 변수 초기화 ---
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'video_watched_for_points' not in st.session_state:
    st.session_state.video_watched_for_points = False # 포인트 지급 여부 추적
if 'current_play_time' not in st.session_state:
    st.session_state.current_play_time = 0.0
if 'video_total_duration' not in st.session_state:
    st.session_state.video_total_duration = 0.0

# --- 비디오 URL ---
VIDEO_URL = "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4"

# --- 1. 비디오 플레이어 임베드 ---
# Streamlit의 내장 st.video를 사용합니다.
# 이 컴포넌트 자체로는 재생 시간을 Streamlit으로 직접 전달하지 못하므로,
# 아래에서 streamlit_js_eval을 사용하여 DOM을 통해 시간을 가져옵니다.
st.video(VIDEO_URL)

# --- 2. JavaScript를 통해 비디오 상태 가져오기 ---
# streamlit_js_eval을 사용하여 웹 페이지의 DOM에 접근, 비디오의 현재 시간과 총 시간을 가져옵니다.
# 1초마다 이 함수를 실행하여 Streamlit 상태를 업데이트합니다.
try:
    video_state = streamlit_js_eval(
        js_expressions=f"""
        (function() {{
            const video = document.querySelector('video[src="{VIDEO_URL}"]');
            if (video) {{
                return {{
                    currentTime: video.currentTime,
                    duration: video.duration,
                    ended: video.ended
                }};
            }}
            return null;
        }})();
        """,
        key="video_watcher",
        interval=1000 # 1초마다 JS 코드 실행
    )

    if video_state:
        st.session_state.current_play_time = video_state.get("currentTime", 0.0)
        st.session_state.video_total_duration = video_state.get("duration", 0.0)
        video_ended_js = video_state.get("ended", False)

        # --- 3. 포인트 지급 로직 ---
        # 비디오 총 길이가 유효하고, 아직 포인트가 지급되지 않았을 때
        if st.session_state.video_total_duration > 0 and not st.session_state.video_watched_for_points:
            # 시청률 계산 (예: 95% 이상 시청 시 완료로 간주)
            watch_percentage = (st.session_state.current_play_time / st.session_state.video_total_duration) * 100

            # 비디오가 JS에서 ended 상태이거나, 시청률이 95% 이상일 때
            # (두 가지 조건을 함께 사용하여 스킵 등으로 인한 우회 방지 및 정확도 향상)
            if video_ended_js or watch_percentage >= 95.0:
                st.session_state.points += 25
                st.session_state.video_watched_for_points = True
                st.success(f"✅ 영상 시청 완료! 포인트 25점 지급! 총 포인트: {st.session_state.points}점")
                st.balloons() # 축하 풍선 효과

except Exception as e:
    st.error(f"비디오 상태를 가져오는 중 오류가 발생했습니다: {e}")
    st.info("비디오가 로드되지 않았거나, 브라우저 환경에 따라 작동하지 않을 수 있습니다.")


# --- 4. 사용자 인터페이스 (진행률 바 & 포인트 표시) ---
st.markdown("---")
# 비디오 총 길이가 유효하면 그 값을 사용, 아니면 기본값 (예: 300초 = 5분)
display_total_duration = st.session_state.video_total_duration if st.session_state.video_total_duration > 0 else 300

progress_value = min(st.session_state.current_play_time / display_total_duration, 1.0)
st.progress(progress_value, text=f"시청 진행률: {progress_value * 100:.1f}% "
                                   f"({st.session_state.current_play_time:.1f}초 / {display_total_duration:.1f}초)")

st.metric("현재 획득 포인트", value=f"{st.session_state.points} 점")

st.markdown("---")
st.info("💡 비디오를 끝까지 시청하면 포인트가 지급됩니다.")
