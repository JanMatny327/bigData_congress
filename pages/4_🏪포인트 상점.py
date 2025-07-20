import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random

# --- 페이지 설정 ---
st.set_page_config(layout="wide", page_title="내 정보", page_icon="ℹ️")

# ✅ 세션 상태 초기화
if not st.session_state.get("logged_in"):
    st.warning("⚠️ 로그인 후 이용 가능합니다.")
    st.stop()

# --- 사이드바 ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/TDSlogo.png", width=150)
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
            st.session_state.login_username_input = ""
            st.session_state.login_password_input = ""
            st.session_state.new_username_input = ""
            st.session_state.new_password_input = ""
            st.rerun()

# --- 메인 페이지 ---
# 탭 구성
# 탭 구성
편의점, 상품권, 카페 = st.tabs(["🏪편의점", "💳상품권", "☕카페"])

# --- 편의점 탭 ---
with 편의점:
    st.markdown("### 🏪 편의점 상품")
    편의점_상품 = [
        {"이름": "우동컵라면", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/컵라면%20그림.png", "포인트": 500},
        {"이름": "매운컵라면", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/컵라면%20그림.png", "포인트": 600},
        {"이름": "비빔컵라면", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/컵라면%20그림.png", "포인트": 550},
    ]
    for idx, item in enumerate(편의점_상품):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(item["이미지"], width=200, caption=item["이름"])
            st.markdown(f"**포인트: {item['포인트']}P**")
        with col2:
            st.write("")
            st.write("")
            if st.button("구매하기", key=f"buy_convenience_{idx}"):
                if item['포인트'] < st.session_state.point:
                    st.success(f"{item['이름']}을(를) 구매했습니다!")
                    st.session_state.point -= item['포인트']
                else:
                    st.error("포인트가 부족합니다.")
        st.markdown("---")

# --- 상품권 탭 ---
with 상품권:
    st.markdown("### 💳 상품권")
    상품권_상품 = [
        {"이름": "게임상품권", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/상품권%20그림.png", "포인트": 2000},
        {"이름": "온라인상품권", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/상품권%20그림.png", "포인트": 3000},
        {"이름": "음식점상품권", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/상품권%20그림.png", "포인트": 2500},
    ]
    for idx, item in enumerate(상품권_상품):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(item["이미지"], width=200, caption=item["이름"])
            st.markdown(f"**포인트: {item['포인트']}P**")
        with col2:
            st.write("")
            st.write("")
            if st.button("구매하기", key=f"buy_gift_{idx}"):
                if st.button("구매하기", key=f"buy_convenience_{idx}"):
                    if item['포인트'] < st.session_state.point:
                        st.success(f"{item['이름']}을(를) 구매했습니다!")
                        st.session_state.point -= item['포인트']
                    else:
                        st.error("포인트가 부족합니다.")
        st.markdown("---")

# --- 카페 탭 ---
with 카페:
    st.markdown("### ☕ 카페")
    카페_상품 = [
        {"이름": "아메리카노", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/커피%20그림.png", "포인트": 1500},
        {"이름": "카페라떼", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/커피%20그림.png", "포인트": 1700},
        {"이름": "아이스티", "이미지": "https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/커피%20그림.png", "포인트": 1300},
    ]
    for idx, item in enumerate(카페_상품):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(item["이미지"], width=200, caption=item["이름"])
            st.markdown(f"**포인트: {item['포인트']}P**")
        with col2:
            st.write("")
            st.write("")
            if st.button("구매하기", key=f"buy_cafe_{idx}"):
                if item['포인트'] < st.session_state.point:
                    st.success(f"{item['이름']}을(를) 구매했습니다!")
                    st.session_state.point -= item['포인트']
                else:
                    st.error("포인트가 부족합니다.")
        st.markdown("---")
