import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time

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

with tab3:
    st.header('To Do Safe Your Mission!')
    st.write("제작 예정")
    
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

