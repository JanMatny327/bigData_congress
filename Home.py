import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random
import plotly.express as px

st.set_page_config(layout='wide')

if "level" not in st.session_state:
    st.session_state.level = 1

if "point" not in st.session_state:
    st.session_state.point = 0

if "current_exp" not in st.session_state:
    st.session_state.current_exp = 0

if "base_exp" not in st.session_state:
    st.session_state.base_exp = 100

# --- 세션 상태 초기화 ---
if "loading_done" not in st.session_state:
    st.session_state.loading_done = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "users" not in st.session_state:
    st.session_state.users = {"testuser": "password123"} # 예시 사용자 (저장되지 않음)

# --- 새로운 세션 상태 변수 추가: 로그인 폼 입력값 관리 ---
if "login_username_input" not in st.session_state:
    st.session_state.login_username_input = ""
if "login_password_input" not in st.session_state:
    st.session_state.login_password_input = ""
if "new_username_input" not in st.session_state:
    st.session_state.new_username_input = ""
if "new_password_input" not in st.session_state:
    st.session_state.new_password_input = ""


# --- 로딩 스크린 ---
if not st.session_state.loading_done:
    with st.spinner('일개미들의 작업을 로딩 중입니다...'):
        loading = st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/LogoVideo.gif", width=600)
        time.sleep(2.5)
        loading.empty()
        st.session_state.loading_done = True

# --- 메인 Home Page ---
st.image('https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/to-do-safe.png', width=1500)

st.header('To do Safe : 미션을 깨면서 안전을 점검하세요')
with st.expander('TDS(To Do Safe) 사이트란?'):
    st.write('To Do Safe 사이트' +
    '\n시민들의 소방안전에 대한 경각심을 깨워주고 점검하는 습관을 들일 수 있게 도와주는 사이트입니다.' +
    '\n집안에서 발생할 수 있는 사건들을 점검하며 미션을 클리어하고 포인트를 흭득하세요!')

st.header('소방 안전 지도 : 주변 소방서 위치 및 과거 사고 이력을 확인해 당신의 안전을 지키세요.')
with st.expander('소방 안전 지도란?'):
    st.write('소방 안전 지도란?' +
    '\n시민들이 주변의 있는 소방서를 빠르게 확인하여 사고를 줄일 수 있는 지도입니다.' +
    '\n또한 과거의 사고 정보을 확인하여 안전사고를 미리 예방할 수 있습니다.')
df = pd.read_csv("부주의에_의한_화재발생.csv")

fig = px.bar(df, x='사고원인', y='발생횟수', title="2022년도 서울시 부주의로 인한 화재사고 원인")

st.chart(fig)

# --- 웹 로고 (사이드바로 이동) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/TDS_일개미들.png", width=150) # 로고를 사이드바 상단에 배치
    st.markdown("""
        <style>
            [alt=Logo] {
                height: 4rem!important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- 로그인/회원가입 로직 (사이드바) ---
with st.sidebar:
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
    else:
        st.subheader("로그인")
        # value 파라미터에 세션 상태 변수 연결
        # on_change 콜백 함수를 사용하여 입력 필드 변경 시 세션 상태 업데이트
        def update_login_username():
            st.session_state.login_username_input = st.session_state.login_username_key
        def update_login_password():
            st.session_state.login_password_input = st.session_state.login_password_key

        login_username = st.text_input("사용자 이름", value=st.session_state.login_username_input, key="login_username_key", on_change=update_login_username)
        login_password = st.text_input("비밀번호", type="password", value=st.session_state.login_password_input, key="login_password_key", on_change=update_login_password)

        if st.button("로그인"):
            if login_username in st.session_state.users and st.session_state.users[login_username] == login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("로그인 성공!")
                time.sleep(0.5) # 잠시 대기하여 메시지 확인
                st.rerun() # 로그인 후 페이지 새로고침하여 메인 콘텐츠 표시
            else:
                st.error("잘못된 사용자 이름 또는 비밀번호입니다.")

        st.subheader("회원가입")
        # 회원가입 입력 필드도 동일하게 value와 on_change 사용
        def update_new_username():
            st.session_state.new_username_input = st.session_state.new_username_key
        def update_new_password():
            st.session_state.new_password_input = st.session_state.new_password_key

        new_username = st.text_input("새 사용자 이름", value=st.session_state.new_username_input, key="new_username_key", on_change=update_new_username)
        new_password = st.text_input("새 비밀번호", type="password", value=st.session_state.new_password_input, key="new_password_key", on_change=update_new_password)

        if st.button("회원가입"):
            if new_username in st.session_state.users:
                st.warning("이미 존재하는 사용자 이름입니다.")
            elif not new_username or not new_password:
                st.warning("사용자 이름과 비밀번호를 모두 입력해주세요.")
            else:
                st.session_state.users[new_username] = new_password
                st.success(f"'{new_username}'님 회원가입이 완료되었습니다! 이제 로그인할 수 있습니다.")
                # 회원가입 후 로그인 폼을 자동으로 채우기 위해 세션 상태를 수정
                st.session_state.login_username_input = new_username
                st.session_state.login_password_input = "" # 비밀번호는 초기화
                # st.rerun() # 필요하다면 회원가입 후 바로 새로고침
                # 회원가입 성공 후 입력 필드 초기화
                st.session_state.new_username_input = ""
                st.session_state.new_password_input = ""

