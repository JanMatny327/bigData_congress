import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random
from streamlit.components.v1 import html as html_component

# --- 세션 state 설정 ---
if 'videoTime' not in st.session_state:
    st.session_state.videoTime = 0
if 'FullTime' not in st.session_state:
    st.session_state.FullTime = 5  # 예시 : 영상 길이 5분
if 'givePoint' not in st.session_state:
    st.session_state.givePoint = 25

# --- 페이지 설정 ---
st.set_page_config(layout="wide")

# 로그인 상태가 아닐 경우 사이트 이용 불가 처리
if not st.session_state.get("logged_in"):
    st.warning("⚠️ 로그인 후 이용 가능합니다.")
    st.stop()

# 로그아웃 버튼 사이드바
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


# --- 영상 강의 페이지 ---
st.header("영상 보고 포인트 얻자!")

col1, col2 = st.columns(2)
with col1:
    st.subheader('영상 강의자료')
    with st.expander('화재안전 영상교육'):

        # HTML video 태그 + JS로 현재 시간 전송
        video_code = """
        <video id="myVideo" width="480" height="270" controls>
          <source src="https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4" type="video/mp4">
        </video>
        <script>
          const video = document.getElementById('myVideo');
          setInterval(() => {
            window.parent.postMessage(video.currentTime, "*");
          }, 1000);
        </script>
        """
        html_component(video_code, height=300)

        # 메시지 수신 및 session_state 업데이트
        html_component("""
        <script>
        window.addEventListener("message", (event) => {
            const seconds = event.data;
            const minutes = (seconds / 60).toFixed(2);
            const streamlitDoc = window.parent.document;
            const input = streamlitDoc.querySelector('input[data-testid="stTextInput"]');
            input.value = minutes;
            input.dispatchEvent(new Event("input", { bubbles: true }));
        }, false);
        </script>
        <input type="text" data-testid="stTextInput" style="display:none" />
        """, height=0)

        # input 값 수신
        time = st.text_input("video_time")
        if time:
            st.session_state.videoTime = float(time)

        # 진행도 표시
        progress_value = min(st.session_state.videoTime / st.session_state.FullTime, 1.0)
        st.progress(progress_value, text=f"현재 시청 시간 : {st.session_state.videoTime:.2f}분 / {st.session_state.FullTime}분")

with col2:
    st.subheader('영상 강의자료2')
    # 다른 영상 강의자료 추가 가능

