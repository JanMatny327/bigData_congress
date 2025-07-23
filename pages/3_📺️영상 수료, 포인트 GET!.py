import streamlit as st
from streamlit.components.v1 import html
import time

if 'points' not in st.session_state:
    st.session_state.points = 0
if 'watched' not in st.session_state:
    st.session_state.watched = False
if 'video_time' not in st.session_state:
    st.session_state.video_time = 0.0

st.title("영상 수강 & 포인트 지급 테스트")

# 비디오 + JS : 
# 1초마다 currentTime postMessage로 보내고,
# ended 이벤트 발생 시 postMessage로 'ended' 보냄
video_html = """
<video id="video" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
</video>

<script>
const video = document.getElementById('video');
setInterval(() => {
    window.parent.postMessage({currentTime: video.currentTime}, "*");
}, 1000);

video.addEventListener('ended', () => {
    window.parent.postMessage({event: 'ended'}, "*");
});
</script>
"""

html(video_html, height=400)

# Streamlit에서 postMessage 수신 및 처리하는 hidden input + listener
html("""
<script>
window.addEventListener("message", (event) => {
    if(event.data.currentTime !== undefined){
        const input = window.parent.document.querySelector('input[data-testid="videoTimeInput"]');
        if(input){
            input.value = event.data.currentTime.toFixed(2);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    if(event.data.event === 'ended'){
        const input = window.parent.document.querySelector('input[data-testid="videoEndedInput"]');
        if(input){
            input.value = 'ended';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
});
</script>

<input type="text" data-testid="videoTimeInput" style="display:none" />
<input type="text" data-testid="videoEndedInput" style="display:none" />
""", height=0)

# Streamlit input 위젯으로 input값 받기
video_time_str = st.text_input("", key="videoTimeInput", label_visibility="collapsed")
video_ended_str = st.text_input("", key="videoEndedInput", label_visibility="collapsed")

try:
    if video_time_str:
        st.session_state.video_time = float(video_time_str)
except:
    pass

if video_ended_str == 'ended' and not st.session_state.watched:
    st.session_state.points += 25
    st.session_state.watched = True
    st.success(f"영상 시청 완료! 포인트 25점 지급. 총 포인트: {st.session_state.points}")

# 프로그래스바
total_seconds = 5 * 60  # 영상 길이 5분 (필요 시 조절)
progress = min(st.session_state.video_time / total_seconds, 1.0)
st.progress(progress, text=f"시청 시간: {st.session_state.video_time:.1f}초 / {total_seconds}초")
st.write(f"현재 포인트: {st.session_state.points}")
