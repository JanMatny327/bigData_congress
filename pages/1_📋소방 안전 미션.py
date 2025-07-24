import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random

# --- 페이지 설정 ---
st.set_page_config(layout="wide", page_title="소방 안전 미션")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ 로그인 후 이용 가능합니다.")
    st.stop()

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
            st.experimental_rerun()

# 사용자 세션 기본값 설정
if "username" not in st.session_state:
    st.session_state.username = "guest"

# 미션 완료 체크 함수
def mission_page(mission, mission_num):
    key = f"mission_done_{mission_num}_{st.session_state.username}"
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

# 현재 년월일시분 기준 seed 생성
now = dt.datetime.now()
seed = int(now.strftime("%Y%m%d%H%M"))
random.seed(seed)
daily_missions = random.sample(missions, 5)

st.header('🔥 오늘의 미션 리스트')
# 남은 시간 표시
st.info("미션은 1분마다 갱신됩니다.")

mission_names = [ms["name"] for ms in daily_missions]
selected_mission = st.selectbox("수행할 미션을 선택하세요", mission_names)

st.write("💡 모든 미션을 완료하면 각각 10포인트가 지급됩니다!")
st.write("\n")

if selected_mission:
    selected_index = mission_names.index(selected_mission)
    mission_page(daily_missions[selected_index], selected_index + 1)
