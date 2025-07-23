import streamlit as st
from streamlit.components.v1 import html

if 'points' not in st.session_state:
    st.session_state.points = 0
if 'watched' not in st.session_state:
    st.session_state.watched = False

st.title("영상 시청 완료 시 포인트 지급")

video_html = """
<video id="video" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
</video>

<script>
const video = document.getElementById('video');

video.addEventListener('ended', () => {
    window.parent.postMessage({event: 'videoEnded'}, '*');
});
</script>
"""

html(video_html, height=400)

# Streamlit에서 메시지 받기용 스크립트 & 숨겨진 input
html("""
<script>
window.addEventListener('message', (event) => {
    if(event.data.event === 'videoEnded'){
        const input = window.parent.document.querySelector('input[data-testid="videoEndedInput"]');
        if(input){
            input.value = 'ended';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
});
</script>
<input type="text" data-testid="videoEndedInput" style="display:none" />
""", height=0)

video_status = st.text_input("", key="videoEndedInput", label_visibility="collapsed")

if video_status == "ended" and not st.session_state.watched:
    st.session_state.points += 25
    st.session_state.watched = True
    st.success(f"영상 시청 완료! 포인트 25점 지급되었습니다. 총 포인트: {st.session_state.points}")

st.write(f"현재 포인트: {st.session_state.points}")
