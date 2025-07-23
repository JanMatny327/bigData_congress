import streamlit as st
from streamlit.components.v1 import html

st.title("자동 영상 수강 시간 감지 & 포인트 지급")

# 세션 변수 초기화
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'watched' not in st.session_state:
    st.session_state.watched = False
if 'video_time' not in st.session_state:
    st.session_state.video_time = 0.0

# 1. 영상 + JS : 영상 재생시간 주기적 전달, 종료 시점 전달
video_html = """
<video id="video" width="640" height="360" controls>
  <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
</video>
<script>
const video = document.getElementById('video');

// 1초마다 재생시간 보내기
setInterval(() => {
    window.parent.postMessage({currentTime: video.currentTime}, "*");
}, 1000);

// 영상 끝나면 알림 보내기
video.addEventListener('ended', () => {
    window.parent.postMessage({event: 'ended'}, "*");
});
</script>
"""

html(video_html, height=400)

# 2. Streamlit 내 JS 메시지 수신용 숨겨진 input + 리스너
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
        const inputEnded = window.parent.document.querySelector('input[data-testid="videoEndedInput"]');
        if(inputEnded){
            inputEnded.value = 'ended';
            inputEnded.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
});
</script>

<input type="text" data-testid="videoTimeInput" style="display:none" />
<input type="text" data-testid="videoEndedInput" style="display:none" />
""", height=0)

# 3. 숨겨진 input 값 읽기
video_time_str = st.text_input("", key="videoTimeInput", label_visibility="collapsed")
video_ended_str = st.text_input("", key="videoEndedInput", label_visibility="collapsed")

# 4. 세션 상태 업데이트
try:
    if video_time_str:
        st.session_state.video_time = float(video_time_str)
except:
    pass

if video_ended_str == 'ended' and not st.session_state.watched:
    st.session_state.points += 25
    st.session_state.watched = True
    st.success(f"영상 시청 완료! 포인트 25점 지급. 총 포인트: {st.session_state.points}")

# 5. 프로그래스바 (예: 영상 5분 가정)
total_duration = 5*60  # 5분 = 300초
progress = min(st.session_state.video_time / total_duration, 1.0)
st.progress(progress, text=f"시청 시간: {st.session_state.video_time:.1f}초 / {total_duration}초")
st.write(f"현재 포인트: {st.session_state.points}")
