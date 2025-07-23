import streamlit as st
from streamlit.components.v1 import html

if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0.0

st.title("자동 재생 시간 감지 테스트")

video_html = """
<video id="video" width="640" height="360" controls>
  <source src="https://sample-videos.com/video123/mp4/480/asdasdas.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
<script>
const video = document.getElementById('video');
setInterval(() => {
  window.parent.postMessage({videoTime: video.currentTime}, "*");
}, 1000);
</script>
"""

html(video_html, height=400)

html("""
<script>
window.addEventListener("message", e => {
  if(e.data.videoTime !== undefined){
    const input = window.parent.document.querySelector('input[data-testid="videoTimeInput"]');
    if(input){
      input.value = e.data.videoTime.toFixed(2);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }
});
</script>
<input type="text" data-testid="videoTimeInput" style="display:none" />
""", height=0)

time_str = st.text_input("", key="videoTimeInput", label_visibility="collapsed")
if time_str:
    st.session_state.videoTime = float(time_str)

st.write(f"감지된 재생 시간: {st.session_state.videoTime} 초")
