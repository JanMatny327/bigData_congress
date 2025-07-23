import streamlit as st
from streamlit.components.v1 import html
import time

st.title("영상 재생시간 자동 감지 (최대한 간단)")

if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0.0

video_html = """
<video id="video" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
</video>
<script>
  const video = document.getElementById('video');
  setInterval(() => {
    localStorage.setItem('videoTime', video.currentTime);
  }, 1000);
</script>
"""

html(video_html, height=400)

# 버튼 누르면 localStorage에서 재생시간을 JS->파이썬으로 가져오기
if st.button("현재 영상 재생시간 불러오기"):
    st.session_state.videoTime = st.experimental_get_query_params().get('videoTime', [0])[0]

progress = st.session_state.videoTime / (5*60)
st.progress(min(progress, 1.0))
st.write(f"현재 시청 시간: {st.session_state.videoTime:.2f}초 / 300초")
