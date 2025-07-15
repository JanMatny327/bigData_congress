import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random
import PIL from image

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
        loading = st.image("LogoVideo.gif", width=600)
        time.sleep(2.5)
        loading.empty()
        st.session_state.loading_done = True

# --- 페이지 설정 ---
st.set_page_config(layout="wide")
st.title('To Do Safe')

# --- 웹 로고 (사이드바로 이동) ---
with st.sidebar:
    st.image("TDSlogo.png", width=150) # 로고를 사이드바 상단에 배치
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


# --- 메인 콘텐츠 (로그인된 경우에만 표시) ---
if st.session_state.logged_in:
    tab1, tab2, tab3, tab4 = st.tabs(['TDS 사이트란?', '소방 안전 지도', '안전 미션', '내 정보'])

    with tab1:
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

    with tab2:
        st.header('소방 안전 지도')
        try:
            data = pd.read_csv("서울특별시_소방서자료.csv")

            m = folium.Map(location=[37.5665, 126.9780],zoom_start=12)

            for i in data.index:
                name = data.loc[i, '소방서이름 ']
                lat = data.loc[i, '위도']
                lon = data.loc[i, '경도']
                address = data.loc[i, '소방서주소']
                number = data.loc[i,'전화번호']
                url = data.loc[i, '소방서 이미지 주소']
                image_url = f"{url}" 

                # HTML 팝업 구성
                popup_html = f"""
                    <div style=width:"200px">
                    <b>소방서 명:</b> {name}<br>
                    <b>소방서 주소:</b> {address}<br>
                    <b>소방서 전화번호:</b> {number}<br>
                    <img src="{image_url}" width="250px">
                </div>
                """
                tooltip = name
                popup_text = f"소방서 명: {name}<br>소방서 주소: {address}<br>소방서 전화번호:</b> {number}<br>"
                popup = folium.Popup(folium.IFrame(popup_html, width=270, height=300), max_width=300)
    
                folium.Marker(
                    location=[lat, lon],
                    tooltip=tooltip,
                    popup=popup,
                    icon=folium.Icon(color='blue', icon='markers')
                ).add_to(m)

            # st_folium으로 지도 출력
            st_data = sf.st_folium(m, width=1920, height=600)
        except FileNotFoundError:
            st.error("⚠️ '서울시 소방서 위치정보.csv' 파일을 찾을 수 없습니다. 파일이 스크립트와 같은 경로에 있는지 확인해주세요.")
        except Exception as e:
            st.error(f"지도 로딩 중 오류가 발생했습니다: {e}")

    # 페이지 이동 함수
    def go_to(page):
        st.session_state.current_page = page

    # 페이지 미션 확인, 미션 지정 등 다양한 역할 수행
    def mission_page(mission, mission_num):
        key = f"mission_done_{mission_num}_{st.session_state.username}" # 사용자별 미션 완료 상태 저장
        if key not in st.session_state:
            st.session_state[key] = False

        st.header("미션 제목 : " + mission["name"])
        st.write("미션 내용 : " + mission["detail"])

        # 현재 미션의 고유 키를 기반으로 "홈으로 돌아가기" 버튼 생성
        if st.button("홈으로 돌아가기", key=f"back_home_btn_{mission_num}"):
            go_to("home")

        if st.session_state[key]:
            st.success("이미 완료한 미션입니다! 포인트가 지급되었어요.")
            return

        if mission["id"] == "photo":
            uploaded = st.file_uploader("사진 업로드", type=["jpg", "png"], key=f"uploader_{mission_num}")
            if uploaded:
                st.session_state[key] = True
                st.success("사진 업로드 완료! 포인트 지급!!")

        elif mission["id"] == "quiz":
            answer = st.radio(mission["detail"], mission["options"], key=f"radio_{mission_num}")
            if st.button(f"제출_{mission_num}", key=f"submit_quiz_{mission_num}"):
                if answer == mission["answer"]:
                    st.session_state[key] = True
                    st.success("정답! 포인트 지급!!")
                else:
                    st.error("오답! 다시 시도해보세요.")

        elif mission["id"] == "action":
            if st.button(f"네 해봤어요!_{mission_num}", key=f"action_done_{mission_num}"):
                st.session_state[key] = True
                st.success("포인트 지급!!")

    with tab3:
        missions = [
            {"id":"photo","name":"소화기 사진 업로드!","detail":"가정 내 소화기를 찾아 사진을 업로드 해주세요."},
            {"id":"photo","name":"소방 안전 빅데이터 사이트 접속!","detail":"소방 안전 빅데이터 사이트에 접속 후 스크린샷을 찍어 올려주세요."},
            {"id":"photo","name":"TDS 사이트 접속!","detail":"TDS 사이트에 접속한 사진을 스크린샷을 찍어 올려주세요."},
            {"id":"quiz", "name":"소방서 퀴즈!", "detail":"위급한 상황이 일어났을 때 어디로 신고해야 될까요?", "answer":"119","options":["119", "112", "1190"]},
            {"id":"quiz", "name":"소화기 사용 퀴즈!", "detail":"소화기를 사용할 때 가장 먼저 빼야하는 부분은?", "answer":"안전핀",
             "options":["안구핀", "안전핀", "안경핀"]},
            {"id":"quiz", "name":"화재 퀴즈!", "detail":"화재가 난 건물에서 다른 사람에게 위험을 알리는데 사용하는 소리 장치는?", "answer":"화재경보기",
             "options":["대피소", "스프링쿨러", "화재경보기"]},
            {"id":"action", "name":"멀티탭 확인하기", "detail":"사용하지 않는 멀티탭이 있는지 확인해보세요!"},
            {"id":"action", "name":"소방서 확인하기", "detail":"우리 주변에 있는 소방서의 위치를 확인해보세요!"},
            {"id":"action", "name":"가스 밸브 확인하기", "detail":"가스 밸브가 잠겨져 있는지 확인하세요!"}
        ]

        seed = int(dt.date.today().strftime("%Y%m%d"))
        random.seed(seed)
        daily_missions = random.sample(missions, 3)

        if "current_page" not in st.session_state:
            st.session_state.current_page = "home"

        if st.session_state.current_page == "home":
            st.header('미션 리스트')
            for i, ms in enumerate(daily_missions, 1):
                # 미션 버튼에 고유한 key 추가
                if st.button(ms["name"], key=f"mission_btn_{i}"):
                    go_to(f"missionPage{i}")
            st.write("모든 미션은 10포인트가 주어집니다!")

        elif st.session_state.current_page.startswith("missionPage"):
            idx = int(st.session_state.current_page[-1]) - 1
            mission_page(daily_missions[idx], idx + 1)

    with tab4:
        st.write('제작 예정')
        

# 로그인되지 않은 경우 메시지 표시
else:
    st.info("로그인 또는 회원가입을 해주세요. 🔑")
