import streamlit as st
from streamlit.components.v1 import html

if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0.0
if 'FullTime' not in st.session_state:
    st.session_state.FullTime = 5.0

st.title("영상 재생시간 자동 감지 및 프로그래스바")

# 로컬 환경 localhost:8501 기준으로 postMessage 대상 명시
video_html = """
<video id="videoPlayer" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

<script>
const video = document.getElementById('videoPlayer');
// 실제 실행하는 도메인에 맞게 바꾸세요 (예: http://localhost:8501)
const targetOrigin = "http://localhost:8501";

setInterval(() => {
  window.parent.postMessage({videoTime: video.currentTime / 60}, targetOrigin);
}, 1000);
</script>
"""

html(video_html, height=400)

# 메시지 수신용 JS + 숨겨진 input
html("""
<script>
window.addEventListener("message", (event) => {
  // event.origin이 targetOrigin과 일치하는지 확인해 보안 강화 가능
  if(event.data.videoTime !== undefined){
    const input = window.parent.document.querySelector('input[data-testid="videoTimeInput"]');
    if(input){
      input.value = event.data.videoTime.toFixed(2);
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
});
</script>
<input type="text" data-testid="videoTimeInput" style="display:none" />
""", height=0)

time_str = st.text_input("", key="videoTimeInput", label_visibility="collapsed")

if time_str:
    try:
        st.session_state.videoTime = float(time_str)
    except:
        pass

progress = min(st.session_state.videoTime / st.session_state.FullTime, 1.0)
st.progress(progress, text=f"현재 시청 시간: {st.session_state.videoTime:.2f}분 / {st.session_state.FullTime}분")
