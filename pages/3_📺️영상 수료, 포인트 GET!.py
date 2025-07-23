import streamlit as st
from streamlit.components.v1 import html

if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0.0
if 'FullTime' not in st.session_state:
    st.session_state.FullTime = 5.0  # 영상 전체 길이 (분)

st.title("영상 재생시간 자동 감지 프로그래스바")

video_html = """
<video id="videoPlayer" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
<script>
const video = document.getElementById('videoPlayer');
setInterval(() => {
  const currentTime = video.currentTime;
  window.parent.postMessage({videoTime: currentTime / 60}, "*");
}, 1000);
</script>
"""

html(video_html, height=400)

# 메시지 받기 및 input에 자동 반영 (사용자가 입력하는 게 절대 아님)
html("""
<script>
window.addEventListener("message", (event) => {
    if(event.data.videoTime !== undefined){
        const input = window.parent.document.querySelector('input[data-testid="videoTimeInput"]');
        if(input){
            input.value = event.data.videoTime.toFixed(2);
            input.dispatchEvent(new Event('input', {bubbles:true}));
        }
    }
});
</script>
<input type="text" data-testid="videoTimeInput" style="display:none" />
""", height=0)

# Streamlit이 input변화 감지해 세션 상태 업데이트
time_str = st.text_input("", key="videoTimeInput", label_visibility="collapsed")
if time_str:
    try:
        st.session_state.videoTime = float(time_str)
    except:
        pass

progress = min(st.session_state.videoTime / st.session_state.FullTime, 1.0)
st.progress(progress, text=f"자동 감지 시청 시간: {st.session_state.videoTime:.2f}분 / {st.session_state.FullTime}분")
