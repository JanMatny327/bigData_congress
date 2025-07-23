import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random

# --- 세션 state 설정 ---
st.session_state.videoTime = 0
st.session_state.FullTime = 0

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
    with st.expander('화제안전 영상교육'):
        st.video('https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4') 
        st.progress(st.session_state.videoTime, text=f"현재 시청 시간 : {st.session_state.videoTime}분 / {st.session_state.FullTime}분")

with col2:
    st.subheader('영상 강의자료2')
