import streamlit as st
from streamlit.components.v1 import html

if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0.0
if 'FullTime' not in st.session_state:
    st.session_state.FullTime = 5.0

st.title("영상 재생시간 자동 감지 테스트")

video_html = """
<video id="videoPlayer" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

<script>
const video = document.getElementById('videoPlayer');
setInterval(() => {
  console.log("Sending currentTime:", video.currentTime);
  window.parent.postMessage({videoTime: video.currentTime / 60}, "*");
}, 1000);
</script>
"""

html(video_html, height=400)

html("""
<script>
window.addEventListener("message", (event) => {
  console.log("Received message in Streamlit:", event.data);
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
