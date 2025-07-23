import streamlit as st
from streamlit.components.v1 import html

# --- 세션 state 설정 ---
if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0
if 'FullTime' not in st.session_state:
    st.session_state.FullTime = 5  # 예시 : 전체 5분

st.set_page_config(layout="wide")

st.header("영상 보고 포인트 얻자!")

col1, col2 = st.columns(2)
with col1:
    st.subheader('영상 강의자료')

    with st.expander('화재안전 영상교육'):
        # HTML + JS 코드 삽입
        video_component = """
        <video id="myVideo" width="480" height="270" controls>
          <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
        </video>
        <script>
        const video = document.getElementById('myVideo');
        setInterval(() => {
          const minutes = (video.currentTime / 60).toFixed(2);
          window.parent.postMessage({"videoTime": minutes}, "*");
        }, 1000);
        </script>
        """
        html(video_component, height=300)

        # 메시지 수신 listener
        html("""
        <script>
        window.addEventListener("message", (event) => {
            const data = event.data;
            if (data.videoTime) {
                const streamlitDoc = window.parent.document;
                const input = streamlitDoc.querySelector('input[data-testid="stVideoTimeInput"]');
                input.value = data.videoTime;
                input.dispatchEvent(new Event("input", { bubbles: true }));
            }
        }, false);
        </script>
        <input type="text" data-testid="stVideoTimeInput" style="display:none" />
        """, height=0)

        # input 수신
        time = st.text_input("video_time", key="stVideoTimeInput")
        if time:
            st.session_state.videoTime = float(time)

        # 진행도 표시
        progress = min(st.session_state.videoTime / st.session_state.FullTime, 1.0)
        st.progress(progress, text=f"현재 시청 시간 : {st.session_state.videoTime:.2f}분 / {st.session_state.FullTime}분")

with col2:
    st.subheader('영상 강의자료2')
