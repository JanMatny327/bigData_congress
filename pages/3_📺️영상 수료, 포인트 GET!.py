import streamlit as st
from streamlit.components.v1 import html

if 'points' not in st.session_state:
    st.session_state.points = 0
if 'watched' not in st.session_state:
    st.session_state.watched = False

# --- 페이지 설정 ---
st.set_page_config(layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ 로그인 후 이용 가능합니다.")
    st.stop()

st.set_page_config(page_title="소방 안전 지도", page_icon="🗺️")

with st.sidebar:
    st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/TDS_일개미들.png", width=150) # 로고를 사이드바 상단에 배치
    st.markdown("""
        <style>
            [alt=Logo] {
                height: 4rem!important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        st.success(f"환영합니다, {st.session_state.username}님!")
        
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            # 로그아웃 시 입력 필드 초기화 (필요하다면)
            st.session_state.login_username_input = ""
            st.session_state.login_password_input = ""
            st.session_state.new_username_input = ""
            st.session_state.new_password_input = ""
            st.rerun() # 로그아웃 후 페이지 새로고침

st.title("영상 수강")

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

ended = st.text_input("", key="videoEndedInput", label_visibility="collapsed")

if ended == "ended" and not st.session_state.watched:
    st.session_state.points += 25
    st.session_state.watched = True
    st.success(f"영상 시청 완료! 포인트 25점 지급. 총 포인트: {st.session_state.points}")

st.write(f"현재 포인트: {st.session_state.points}")
