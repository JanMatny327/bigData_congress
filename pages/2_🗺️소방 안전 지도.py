import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.features import CustomIcon
import requests

# --- 페이지 설정 ---
st.set_page_config(layout="wide", page_title="소방 안전 지도", page_icon="🗺️")

# --- 로그인 확인 ---
if not st.session_state.get("logged_in"):
    st.warning("⚠️ 로그인 후 이용 가능합니다.")
    st.stop()

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
            st.experimental_rerun()

# --- 탭 구성 ---
tab1, tab2 = st.tabs(['🧯 소방 안전 지도', '🔥 사건사고 지도'])

# --- 🔸 소방 안전 지도 탭 ---
with tab1:
    st.header('🧯 소방 안전 지도')

    try:
        # 데이터 불러오기
        data = pd.read_csv("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/pages/seoul_119_data.csv")
        data2 = pd.read_csv("https://raw.githubusercontent.com/JanMatny327/bigData_congress/5383d52756a325ed369f401fb521aac43b3e3865/fire_station_status_v5.csv")

        # 출처 구분 컬럼 추가
        data["source"] = "data"
        data2["source"] = "data2"

        # 합치기
        result = pd.concat([data, data2], ignore_index=True)

        # 지역 리스트
        districts = sorted(result['본부명'].dropna().unique())

        # 드롭다운 박스
        selected_cause = st.selectbox('사고 원인을 선택하세요:', districts)

        # 선택한 지역 필터링
        filtered = result[result['본부명'] == selected_cause]
        filtered_data = filtered[filtered["source"] == "data"]
        filtered_data2 = filtered[filtered["source"] == "data2"]

        # 내 위치 임시 설정 (필요 시 변경)
        def get_geolocation():
            try:
                res = requests.get("https://ipapi.co/json/").json()
                return {'coords': {'latitude': res['latitude'], 'longitude': res['longitude']}}
            except:
                return None

        location = get_geolocation()
        if location:
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
        else:
            lat, lon = 37.5665, 126.9780  # 서울시청 기본 좌표

        # 지도 기본 생성
        default_center = st.session_state.get("center_map", [lat, lon])
        m = folium.Map(location=default_center, zoom_start=12)

        # 내 위치 마커
        folium.Marker(
            location=[lat, lon],
            tooltip="📍 내 위치",
            popup="내 위치입니다.",
            icon=folium.Icon(color="blue", icon="user")
        ).add_to(m)

        # filtered_data2 마커 추가
        for i in filtered_data2.index:
            try:
                name = filtered_data2.loc[i, '소방서']
                lat2 = float(filtered_data2.loc[i, '위도'])
                lon2 = float(filtered_data2.loc[i, '경도'])
                address = filtered_data2.loc[i, '주소']
                number = filtered_data2.loc[i, '전화번호']
                image = "https://cdn-icons-png.flaticon.com/512/2801/2801574.png"

                popup_html = f"""
                <div style="width:200px">
                    <b>소방서 명:</b> {name}<br>
                    <b>주소:</b> {address}<br>
                    <b>전화번호:</b> {number}<br>
                    <img src="{image}" width="200px">
                </div>
                """
                popup = folium.Popup(folium.IFrame(popup_html, width=220, height=250), max_width=250)
                icon = CustomIcon("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/소방서.png", icon_size=(40, 40))
                folium.Marker(location=[lat2, lon2], tooltip=name, popup=popup, icon=icon).add_to(m)
            except Exception as e:
                st.warning(f"data2 마커 오류: {e}")

        # filtered_data 마커 추가
        for i in filtered_data.index:
            try:
                name = filtered_data.loc[i, '본부명']
                lat1 = float(filtered_data.loc[i, '위도'])
                lon1 = float(filtered_data.loc[i, '경도'])
                address = filtered_data.loc[i, '소방서주소']
                number = filtered_data.loc[i, '전화번호']
                url = filtered_data.loc[i, '소방서_이미지_주소']

                popup_html = f"""
                <div style="width:200px">
                    <b>소방서 명:</b> {name}<br>
                    <b>주소:</b> {address}<br>
                    <b>전화번호:</b> {number}<br>
                    <img src="{url}" width="200px">
                </div>
                """
                popup = folium.Popup(folium.IFrame(popup_html, width=220, height=250), max_width=250)
                icon = CustomIcon("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/소방서.png", icon_size=(40, 40))
                folium.Marker(location=[lat1, lon1], tooltip=name, popup=popup, icon=icon).add_to(m)
            except Exception as e:
                st.warning(f"data 마커 오류: {e}")

        # 중심 좌표 재조정 (새로 생성 X, 위치만 이동)
        if not filtered.empty and '위도' in filtered.columns and '경도' in filtered.columns:
            center = [filtered['위도'].mean(), filtered['경도'].mean()]
            m.location = center
            m.zoom_start = 14.5

        # 지도 출력
        st_folium(m, width=1920, height=600)

    except Exception as e:
        st.error(f"🚨 지도 로딩 중 오류가 발생했습니다: {e}")

# --- 🔸 사건사고 지도 탭 ---
with tab2:
    st.header('🔥 사건사고 지도')

    try:
        data = pd.read_csv("https://raw.githubusercontent.com/JanMatny327/bigData_congress/main/Seoul_Rescue_Final.csv")

        accident_causes = sorted(data['사고원인명'].unique())
        districts = sorted(data['현장시군구명'].unique())

        col1, col2 = st.columns(2)
        with col1:
            selected_cause = st.selectbox('사고 원인을 선택하세요:', accident_causes)
        with col2:
            selected_district = st.selectbox('시군구를 선택하세요:', districts)

        filtered = data[(data['사고원인명'] == selected_cause) & (data['현장시군구명'] == selected_district)]

        if not filtered.empty:
            center = [filtered['손상지역위도'].mean(), filtered['손상지역경도'].mean()]
        else:
            center = [37.5665, 126.9780]

        m = folium.Map(location=center, zoom_start=14.5)

        from folium.plugins import HeatMap
        HeatMap(data=filtered[['손상지역위도', '손상지역경도']], radius=20).add_to(m)

        response = requests.get('https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json')
        seoul_geo = response.json()
        filtered_geojson = {
            "type": "FeatureCollection",
            "features": [f for f in seoul_geo['features'] if f['properties']['name'] == selected_district]
        }

        folium.GeoJson(
            filtered_geojson,
            name=selected_district,
            style_function=lambda x: {
                'fillColor': 'none',
                'color': 'red',
                'weight': 4
            }
        ).add_to(m)

        st_folium(m, width=1920, height=600)

    except Exception as e:
        st.error(f"🚨 사건사고 지도 로딩 중 오류가 발생했습니다: {e}")
