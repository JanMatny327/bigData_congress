import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random
from folium.features import CustomIcon

# --- 페이지 설정 ---
st.set_page_config(layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ 로그인 후 이용 가능합니다.")
    st.stop()

st.set_page_config(page_title="소방 안전 지도", page_icon="🗺️")

with st.sidebar:
    st.image("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/TDS_일개미들.png", width=150) # 로고를 사이드바 상단에 배치
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

tab1, tab2 = st.tabs(['소방 안전 지도', '소방 사건사고 지도'])

with tab1:
    st.header('소방 안전 지도')
    try:
        data = pd.read_csv("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/pages/seoul_119_data.csv")

        m = folium.Map(location=[37.5665, 126.9780],zoom_start=12)
    
        for i in data.index:
            name = data.loc[i, '소방서이름 ']
            lat = data.loc[i, '위도']
            lon = data.loc[i, '경도']
            address = data.loc[i, '소방서주소']
            number = data.loc[i,'전화번호']
            url = data.loc[i, '소방서_이미지_주소']
            image_url = f"{url}"

            popup_html = f"""
                <div style=width:"200px">
                    <b>소방서 명:</b> {name}<br>
                    <b>소방서 주소:</b> {address}<br>
                    <b>소방서 전화번호:</b> {number}<br>
                    <img src="{image_url}" width="300px">
                </div>
                """
            
            tooltip = name
            popup_text = f"소방서 명: {name}<br>소방서 주소: {address}<br>소방서 전화번호:</b> {number}<br>"
            popup = folium.Popup(folium.IFrame(popup_html, width=355, height=310), max_width=355)
            
            icon = CustomIcon("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/소방서.png", icon_size=(40, 40))
            
            folium.Marker(
                location=[lat, lon],
                tooltip=tooltip,
                popup=popup,
                icon=icon
            ).add_to(m)
            
            
            
        # st_folium으로 지도 출력
        st_data = sf.st_folium(m, width=1920, height=600)
        except FileNotFoundError:
        st.error("⚠️ '서울시 소방서 위치정보.csv' 파일을 찾을 수 없습니다. 파일이 스크립트와 같은 경로에 있는지 확인해주세요.")
        except Exception as e:
        st.error(f"지도 로딩 중 오류가 발생했습니다: {e}")
            
with tab2:
    st.header('소방 사건사고 지도')
