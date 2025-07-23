import streamlit as st
from streamlit.components.v1 import html

st.title("간단 영상 재생시간 자동 체크")

# 세션 초기화
if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0

# HTML+JS: 영상 + 1초마다 currentTime을 hidden input에 직접 넣기
video_js = """
<video id="video" width="640" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
</video>

<input type="hidden" id="timeInput" />

<script>
const video = document.getElementById('video');
const input = document.getElementById('timeInput');

setInterval(() => {
  input.value = video.currentTime.toFixed(2);
  input.dispatchEvent(new Event('input'));
}, 1000);
</script>
"""

html(video_js, height=400)

# Streamlit 텍스트 입력에 hidden input 연결(key값 맞춤)
time = st.text_input("현재 재생 시간 (초)", key="timeInput")

if time:
    st.session_state.videoTime = float(time)

progress = st.session_state.videoTime / (5*60)  # 5분 기준
st.progress(min(progress, 1.0))
st.write(f"현재 시청 시간: {st.session_state.videoTime:.2f}초 / 300초")
