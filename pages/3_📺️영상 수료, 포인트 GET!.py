import streamlit as st
from streamlit.components.v1 import html

# 세션 상태 초기화
if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0.0
if 'FullTime' not in st.session_state:
    st.session_state.FullTime = 5.0  # 영상 전체 길이 (분)

st.title("영상 보고 포인트 얻자!")

# HTML + JS로 video 태그 삽입, 재생 시간 1초마다 부모에 전송
video_html = f"""
<video id="videoPlayer" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

<script>
const video = document.getElementById('videoPlayer');
setInterval(() => {{
    const currentTime = video.currentTime;
    const minutes = (currentTime / 60).toFixed(2);
    window.parent.postMessage({{videoTime: minutes}}, "*");
}}, 1000);
</script>
"""

html(video_html, height=400)

# 메시지 수신하는 스크립트와 숨겨진 input
html("""
<script>
window.addEventListener("message", (event) => {
    const data = event.data;
    if (data.videoTime) {
        const input = window.parent.document.querySelector('input[data-testid="videoTimeInput"]');
        if(input){
            input.value = data.videoTime;
            input.dispatchEvent(new Event("input", { bubbles: true }));
        }
    }
});
</script>
<input type="text" data-testid="videoTimeInput" style="display:none" />
""", height=0)

# input에서 받은 재생시간을 세션 상태에 저장
time_str = st.text_input("video_time", key="videoTimeInput")
if time_str:
    st.session_state.videoTime = float(time_str)

# 프로그래스 바 표시
progress_val = min(st.session_state.videoTime / st.session_state.FullTime, 1.0)
st.progress(progress_val, text=f"현재 시청 시간: {st.session_state.videoTime:.2f}분 / {st.session_state.FullTime}분")
