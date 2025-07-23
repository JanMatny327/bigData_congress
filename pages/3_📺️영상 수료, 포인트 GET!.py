import streamlit as st
from streamlit.components.v1 import html

# === 초기 세션 상태 설정 ===
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0.0
if 'FullTime' not in st.session_state:
    st.session_state.FullTime = 5.0  # 영상 길이 (분)
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'point_given' not in st.session_state:
    st.session_state.point_given = False

# === 로그인 UI ===
def login():
    st.title("로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        # 여기서는 임시로 아이디=admin, 비번=1234 고정
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("로그인 실패. 아이디 또는 비밀번호가 틀렸습니다.")

def logout():
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.videoTime = 0.0
        st.session_state.point_given = False
        st.experimental_rerun()

# === 로그인 상태 체크 ===
if not st.session_state.logged_in:
    login()
    st.stop()

# === 로그인 후 화면 ===
st.sidebar.success(f"{st.session_state.username}님, 환영합니다!")
logout()

st.title("영상 보고 포인트 얻자!")

# === 영상 컴포넌트 ===
video_url = "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4"

video_component = f"""
<video id="myVideo" width="640" height="360" controls>
  <source src="{video_url}" type="video/mp4">
  Your browser does not support the video tag.
</video>

<script>
const video = document.getElementById('myVideo');
setInterval(() => {{
  const currentSeconds = video.currentTime;
  const minutes = (currentSeconds / 60).toFixed(2);
  window.parent.postMessage({{videoTime: minutes}}, "*");
}}, 1000);
</script>
"""

html(video_component, height=400)

# 메시지 수신 + 숨겨진 input
html("""
<script>
window.addEventListener("message", (event) => {{
    const data = event.data;
    if (data.videoTime) {{
        const input = window.parent.document.querySelector('input[data-testid="stVideoTimeInput"]');
        if(input){{
            input.value = data.videoTime;
            input.dispatchEvent(new Event("input", {{ bubbles: true }}));
        }}
    }}
}}, false);
</script>
<input type="text" data-testid="stVideoTimeInput" style="display:none" />
""", height=0)

# 재생시간 받기
time_str = st.text_input("video_time", key="stVideoTimeInput")

try:
    if time_str:
        st.session_state.videoTime = float(time_str)
except:
    pass

# 진행도 표시
progress = min(st.session_state.videoTime / st.session_state.FullTime, 1.0)
st.progress(progress, text=f"현재 시청 시간 : {st.session_state.videoTime:.2f}분 / {st.session_state.FullTime}분")

# 포인트 지급 조건 및 지급
if st.session_state.videoTime >= st.session_state.FullTime and not st.session_state.point_given:
    st.session_state.points += 25  # 지급 포인트
    st.session_state.point_given = True
    st.success(f"🎉 영상 시청 완료! {st.session_state.points} 포인트가 지급되었습니다.")

# 현재 포인트 표시
st.info(f"현재 포인트: {st.session_state.points}점")
