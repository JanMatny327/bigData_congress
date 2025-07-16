import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random

# --- 페이지 설정 ---
st.set_page_config(layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ 로그인 후 이용 가능합니다.")
    st.stop()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/TDSlogo.png", width=150) # 로고를 사이드바 상단에 배치
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



