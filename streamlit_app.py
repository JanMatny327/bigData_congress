import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random

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

# --- 페이지 설정 ---
st.set_page_config(layout="wide")

# --- 웹 로고 (사이드바로 이동) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/TDSlogo.png", width=150) # 로고를 사이드바 상단에 배치
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

     # ✅ 사용자 세션 초기화
    if "username" not in st.session_state:
        st.session_state.username = "guest"

    # ✅ 미션 완료 여부 체크 함수
    def mission_page(mission, mission_num):
        key = f"mission_done_{mission_num}_{st.session_state.username}"  # 사용자별 완료 여부 저장

        if key not in st.session_state:
            st.session_state[key] = False

        st.header("미션 제목 : " + mission["name"])
        st.write("미션 내용 : " + mission["detail"])

        if st.session_state[key]:
            st.success("이미 완료한 미션입니다!")
            return

        if mission["id"] == "photo":
            uploaded = st.file_uploader("사진 업로드", type=["jpg", "png"], key=f"uploader_{mission_num}")
            if uploaded:
                st.balloons()
                time.sleep(0.5)
                st.session_state[key] = True
                st.success("관리자가 검토 중입니다. 검토 후 포인트가 지급될 예정입니다.")

        elif mission["id"] == "quiz":
            answer = st.radio(mission["detail"], mission["options"], key=f"radio_{mission_num}")
            if st.button(f"제출", key=f"submit_quiz_{mission_num}"):
                if answer == mission["answer"]:
                    st.balloons()
                    time.sleep(0.5)
                    st.session_state[key] = True
                    st.success("관리자가 검토 중입니다. 검토 후 포인트가 지급될 예정입니다.")
                else:
                    st.error("오답! 다시 시도해보세요.")
    
        elif mission["id"] == "action":
            if st.button(f"네 해봤어요!", key=f"action_done_{mission_num}"):
                st.balloons()
                time.sleep(0.5)
                st.session_state[key] = True
                st.success("관리자가 검토 중입니다. 검토 후 포인트가 지급될 예정입니다.")
    
    
    
    with tab3:
        # 미션 리스트
        missions = [
            {"id":"photo","name":"소화기 사진 업로드!","detail":"가정 내 소화기를 찾아 사진을 업로드 해주세요."},
            {"id":"photo","name":"소방 안전 빅데이터 사이트 접속!","detail":"소방 안전 빅데이터 사이트에 접속 후 스크린샷을 찍어 올려주세요."},
            {"id":"photo","name":"TDS 사이트 접속!","detail":"TDS 사이트에 접속한 사진을 스크린샷을 찍어 올려주세요."},
            {"id":"photo","name":"완강기 찾아보기!","detail":"건물에 설치된 완강기 사진을 찾아 업로드 해주세요."},
            {"id":"photo","name":"화재사고 뉴스 캡처!","detail":"최근 뉴스에서 화재 관련 기사를 찾아 캡처하고 올려주세요."},
            {"id":"photo","name":"우리집 가스차단기 확인!","detail":"우리집에 설치된 가스차단기나 가스밸브를 사진으로 찍어 올려보세요."},
            {"id":"quiz", "name":"소방서 퀴즈!", "detail":"위급한 상황이 일어났을 때 어디로 신고해야 될까요?", "answer":"119","options":["119", "112", "1190"]},
            {"id":"quiz", "name":"소화기 사용 퀴즈!", "detail":"소화기를 사용할 때 가장 먼저 빼야하는 부분은?", "answer":"안전핀",
             "options":["안구핀", "안전핀", "안경핀"]},
            {"id":"quiz","name":"소화기 퀴즈2!","detail":"소화기의 유효기간은 보통 몇 년일까요?", "answer":"10년",
             "options":["5년", "10년", "15년"]},
            {"id":"quiz", "name":"화재 퀴즈!", "detail":"화재가 난 건물에서 다른 사람에게 위험을 알리는데 사용하는 소리 장치는?", "answer":"화재경보기",
             "options":["대피소", "스프링쿨러", "화재경보기"]},
            {"id":"quiz","name":"화재 예방 퀴즈!","detail":"전기 콘센트에서 불이 나지 않도록 하려면 어떻게 해야 할까요?", "answer":"문어발 금지",
             "options":["문어발 금지", "자주 만지기", "멀티탭 물청소"]},
            {"id":"quiz","name":"계절별 화재 위험 퀴즈!","detail":"겨울철에 가장 많은 화재 원인은?", "answer":"난방기기",
             "options":["에어컨", "난방기기", "선풍기"]},
            {"id":"quiz","name":"대피 요령 퀴즈!","detail":"불이 났을 때 엘리베이터 대신 이용해야 하는 것은?", "answer":"계단",
             "options":["계단", "엘리베이터", "에스컬레이터"]},
            {"id":"action", "name":"멀티탭 확인하기", "detail":"사용하지 않는 멀티탭이 있는지 확인해보세요!"},
            {"id":"action","name":"콘센트 먼지 제거하기","detail":"화재 예방을 위해 사용하지 않는 콘센트나 멀티탭의 먼지를 닦아보세요."},
            {"id":"action","name":"가전제품 플러그 뽑기","detail":"사용하지 않는 가전제품의 플러그를 뽑아두는 습관을 실천해보세요."},
            {"id":"action", "name":"소방서 확인하기", "detail":"우리 주변에 있는 소방서의 위치를 확인해보세요!"},
            {"id":"action", "name":"가스 밸브 확인하기", "detail":"가스 밸브가 잠겨져 있는지 확인하세요!"}
        ]
    
        # 오늘의 미션 5개 무작위 선택
        seed = int(dt.date.today().strftime("%Y%m%d"))
        random.seed(seed)
        daily_missions = random.sample(missions, 5)
    
        st.header('🔥 오늘의 미션 리스트')
    
        mission_names = [ms["name"] for ms in daily_missions]
        selected_mission = st.selectbox("수행할 미션을 선택하세요", mission_names)
    
        st.write("💡 모든 미션을 완료하면 각각 10포인트가 지급됩니다!")
        st.write("\n")
    
        if selected_mission != "-- 미션을 선택하세요 --":
            selected_index = mission_names.index(selected_mission)
            mission_page(daily_missions[selected_index], selected_index + 1)
            
    with tab4:
        st.write('제작 예정')
        

# 로그인되지 않은 경우 메시지 표시
else:
    st.info("로그인 또는 회원가입을 해주세요. 🔑")
