import streamlit as st
import pandas as pd

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

with tab2:
    st.header('소방 안전 지도')
    # 위도와 경도를 활용하여 지도 이미지를 사이트 안에 송출
    data = pd.DataFrame({
        'latitude': [37.7749, 34.0522, 40.7128],
        'longitude': [-122.4194, -118.2437, -74.0060]
    })
    # 맵 이미지 송출
    st.map(data)

with tab3:
    st.header('To Do Safe Your Mission!')
    st.write("제작 예정")

# 웹 사이트 사이드 바
search = st.sidebar.text_input('검색할 내용을 입력하세요.')


