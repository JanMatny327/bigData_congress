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

if "avatar_uploaded_once" not in st.session_state:
    st.session_state.avatar_uploaded_once = False

# ✅ 레벨업 로직
if st.session_state.current_exp >= st.session_state.base_exp:
    st.session_state.level += 1
    st.session_state.point += 50
    st.session_state.current_exp = 0
    st.session_state.base_exp = int(100 * (st.session_state.level ** 0.65))

# --- 사이드바 ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/TDS_일개미들.png", width=150)
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
avata, information = st.columns([1, 3])

with avata:
    st.header("🧑 내 정보")

    # ✅ 업로드된 이미지가 있으면 그걸로 표시
    if "uploaded_avatar" in st.session_state:
        st.image(st.session_state.uploaded_avatar, caption="내 아바타", width=200)
    else:
        st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/avata.png", caption="내 아바타", width=200)

    # ✅ 이미지 업로더: 업로드하면 바로 적용됨
    on = st.toggle(label="아이콘 사진 업로드")
    if on:
        uploaded = st.file_uploader(label="사진을 업로드", type=["jpg", "png"])
        if uploaded:
            st.session_state.uploaded_avatar = uploaded
            st.success("✅ 아바타가 변경되었습니다! 페이지를 이동해 확인하세요!")
    


with information:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.write(f"**아이디:** {st.session_state.username}")
    st.write(f"**레벨:** {st.session_state.level}")

    # ✅ 경험치 바
    exp_bar = st.session_state.current_exp / st.session_state.base_exp if st.session_state.base_exp > 0 else 0.0
    st.progress(exp_bar, text=f"{st.session_state.current_exp} / {int(st.session_state.base_exp)} EXP")

    st.write(f"**누적 포인트:** {st.session_state.point}점")
