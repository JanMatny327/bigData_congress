import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt

if "loading_done" not in st.session_state:
    st.session_state.loading_done = False

if not st.session_state.loading_done:
    with st.spinner('일개미들의 작업을 로딩 중입니다...'):
        loading = st.image("LogoVideo.gif", width=600)
        time.sleep(2.5)
        loading.empty()
        st.session_state.loading_done = True

st.title('To Do Safe')
st.set_page_config(layout="wide")

# 웹 사이트 탭
tab1, tab2, tab3 = st.tabs(['TDS 사이트란?', '소방 안전 지도', 'To Do Safe Your Mission!'])

with tab1:
    st.header('To do Safe : 미션을 깨면서 안전을 점검하세요')
    # 클릭시 내용 보여주는 
    with st.expander('TDS(To Do Safe) 사이트란?'):
        st.write('To Do Safe 사이트' +
        '\n시민들의 소방안전에 대한 경각심을 깨워주고 점검하는 습관을 들일 수 있게 도와주는 사이트입니다.' +
        '\n집안에서 발생할 수 있는 사건들을 점검하며 미션을 클리어하고 포인트를 흭득하세요!')

    st.header('소방 안전 지도 : 주변 소방서 위치 및 과거 사고 이력을 확인해 당신의 안전을 지키세요.')
    # 클릭시 내용 보여주는 
    with st.expander('소방 안전 지도란?'):
        st.write('소방 안전 지도란?' +
        '\n시민들이 주변의 있는 소방서를 빠르게 확인하여 사고를 줄일 수 있는 지도입니다.' +
        '\n또한 과거의 사고 정보을 확인하여 안전사고를 미리 예방할 수 있습니다.')

with tab2:
    st.header('소방 안전 지도')
    data = pd.read_csv("서울시 소방서 위치정보.csv", encoding='utf-8')
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

    # 소방서 위치 마커 추가
    for i in data.index:
        name = data.loc[i, '서ㆍ센터명']
        lat = data.loc[i, '위도']
        lon = data.loc[i, '경도']
        folium.Marker(
            location=[lat, lon],
            popup=name,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    # st_folium으로 지도 출력
    st_data = sf.st_folium(m, width=1000, height=500)

# 페이지 이동 함수
def go_to(page):
    st.session_state.current_page = page

# 페이지 미션 확인, 미션 지정 등 다양한 역할 수행
def mission_page(mission, mission_num):
    key = f"mission_done_{mission_num}" # 매개변수로 받은 mission_num 값을 활용해, 미션을 했는지 확인
    if key not in st.session_state: # 만약 현재 상태로 가지고 있지 않다면 key값에 들어있는 변수의 이름으로 false 초기화
        st.session_state[key] = False 

    st.header("미션 제목 : " + mission["name"]) # 제목 적어주기
    st.write("미션 내용 : " + mission["detail"]) # 자세한 내용 적어주기

    if st.button("홈으로 돌아가기"): # 홈으로 돌아가는 버튼
        go_to("home")

    if st.session_state[key]: # 만약 미션 완료가 True라면
        st.success("이미 완료한 미션입니다! 포인트가 지급되었어요.") # 메세지 띄우기 
        return # return 하여 밑의 코드 실행X

    if mission["id"] == "photo": # 만약 미션의 종류가 사진 찍는 거라면 
        uploaded = st.file_uploader("사진 업로드", type=["jpg", "png"]) # 사진 업로드 하기
        if uploaded: # 사진 업로드 했으면
            st.session_state[key] = True # 미션완료 체크
            st.success("사진 업로드 완료! 포인트 지급!!") # 포인트 지급

    elif mission["id"] == "quiz": # 만약 미션 종류가 퀴즈라면
        answer = st.radio(mission["detail"], mission["options"], key=f"radio_{mission_num}") # 답을 고르게함
        if st.button(f"제출_{mission_num}"): # 버튼 제출
            if answer == mission["answer"]: # 버튼 제출이 답과 맞으면
                st.session_state[key] = True # 미션 완료 체크
                st.success("정답! 포인트 지급!!") # 포인트 지급
            else: # 아니면
                st.error("오답! 다시 시도해보세요.") # 오답 체크

    elif mission["id"] == "action": # 만약 미션의 종류가 간단한 행동이라면
        if st.button(f"네 해봤어요!_{mission_num}"): # 해봤어요 버튼 체크 
            st.session_state[key] = True # 미션 완료 체크
            st.success("포인트 지급!!") # 포인트 지급
 
    
with tab3:
    missions = [ # 미션 종류 딕셔너리리
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

    seed = int(dt.date.today().strftime("%Y%m%d")) # seed 변수의 오늘 날짜만 저장
    random.seed(seed) # seed 함수 : 같은 값이 들어오면 같은 값을 내보냄
    daily_missions = random.sample(missions, 3) # 샘플로 중복없이 3개의 misssion 리스트에서 미션을 뽑음

    if "current_page" not in st.session_state: # 만약 페이지 변수가 비어있다면
        st.session_state.current_page = "home" # 기본값을 홈으로 초기화

    if st.session_state.current_page == "home": # 만약 홈 페이지라면
        st.header('미션 리스트') # 미션 리스트 제목 추가
        for i, ms in enumerate(daily_missions, 1): # 딕셔너리 + 인덱스 값까지 같이 반복 돌림
            if st.button(ms["name"]): # 각자의 이름으로 버튼 생성
                go_to(f"missionPage{i}") # 미션 1,2 3 페이지로 이동
        st.write("모든 미션은 10포인트가 주어집니다!") # 모든 미션은 몇포인트가 주어지는지 공지

    elif st.session_state.current_page.startswith("missionPage"): # 홈페이지가 아니고 미션 1, 2, 3 페이지 중 하나라면
        idx = int(st.session_state.current_page[-1]) - 1 # 미션 마지막 숫자를 인덱스로 삼고
        mission_page(daily_missions[idx], idx + 1) # 그 숫자의 페이지의 미션을 불러옴
    
# 웹 로고
logoUrl = "TDSlogo.png"
logo = st.logo(logoUrl)
st.html("""
  <style>
    [alt=Logo] {
      height: 4rem!important;
    }
  </style>
        """)

