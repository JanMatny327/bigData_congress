import streamlit as st
import pandas as pd
import folium
import streamlit_folium as sf
import time
import datetime as dt
import random




# ✅ 세션 상태 초기화
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
            st.rerun()

# --- 세션 상태 초기화 ---
if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = {}

# --- 페이지 설정 ---
st.set_page_config(layout="wide")
st.title("영상 수강 및 퀴즈")

# --- 영상 데이터 ---
video_data = {
    "올바른 전기 사용 5가지 안전수칙": {
        "url": "https://www.gnfire.go.kr/upload/gnfire/527/_dc702786-14af-48c3-a210-6b78b76b92f21751619510804.mp4",
        "출처": "경상남도소방본부",
        "퀴즈제목": "다음 중 올바른 안전수칙을 고르시오",
        "문제": [
            "1. 플러그를 뽑을 때 선을 잡고 뽑는다.",
            "2. 젖은 손으로 콘센트를 만진다.",
            "3. 멀티탭을 문어발식으로 사용한다.",
            "4. 차단기가 있는 장소를 혼잡하게 만든다.",
            "5. TV, 냉장고 등 가전제품은 단일 콘센트를 사용한다."
        ],
        "답": "5. TV, 냉장고 등 가전제품은 단일 콘센트를 사용한다."
    },

    "화재는 부주의에서 시작된다": {
        "url": "https://119fbn.fire.go.kr/site/fbn119/file/download/uu/f874f2550bac48ab97e893d108ad9c10",
        "출처": "한국소방방송",
        "퀴즈제목": "영상에서 나온 인물이 한 잘못을 모두 고르시오",
        "문제": [
            "1. 음식을 조리하면서 자리를 비웠다.",
            "2. 놀이터에서 불장난을 하였다.",
            "3. 담배꽁초를 아무런 곳에 버렸다.",
            "4. 캠핑장에서 불을 피운후 자리를 비웠다.",
            "5. 문어발식 콘센트사용을 했다."
        ],
        "답": ["3. 담배꽁초를 아무런 곳에 버렸다.", "5. 문어발식 콘센트사용을 했다."]
    },

    "소방안전 교육 화제예방": {
        "url": "https://119metaverse.nfa.go.kr/upload/safety/EBIyFQu4Qh%EC%B2%AD%EC%86%8C%EB%85%84%20%EC%86%8C%EB%B0%A9%EC%95%88%EC%A0%84%EA%B5%90%EC%9C%A1_%EB%8B%A8%ED%8E%B8%20%EC%98%81%EC%83%81_%ED%99%94%EC%9E%AC%EC%95%88%EC%A0%84.mp4",
        "출처": "소방청",
        "퀴즈제목": "옳지 않은 소화기 사용법을 고르시오",
        "문제": [
            "1. 안전핀을 제거한다.",
            "2. 호스를 옆으로 당겨서 빼낸다.",
            "3. 노즐을 잡고 불이난 곳을 향해서 조준한다.",
            "4. 손잡이를 움켜쥐고 불을 향해 발사한다.",
            "5. 소화기를 사용할 때 바람을 마주보고 분사한다."
        ],
        "답": "5. 소화기를 사용할 때 바람을 마주보고 분사한다."
    },

    "소방안전교육 영상교재 (화재예방편)": {
        "url": "https://119metaverse.nfa.go.kr/upload/safety/Vt45mNgvB42.%20%EC%86%8C%EB%B0%A9%EC%B2%AD_%ED%99%94%EC%9E%AC%20%EC%98%88%EB%B0%A9%ED%8E%B8_1.mp4",
        "출처": "소방청",
        "퀴즈제목": "야외 활동 시 주의하지 않아도 되는 점을 고르시오.",
        "문제": [
            "1. 물놀이를 할때는 구명조끼를 꼭 입는다.",
            "2. 불을 피울때 화로 사용후 잔불 정리하기.",
            "3. 휴대용 가스레인지 사용시 받침보다 작은 냄비 사용하기.",
            "4. 한개의 콘센트에 여러게의 제품을 연결하지 않기.",
            "5. 플러그, 콘센트의 물기 노출에 주의하기."
        ],
        "답": "1. 물놀이를 할때는 구명조끼를 꼭 입는다."
    }
}

# --- 비디오 선택 ---
video_title = st.selectbox("수강하실 비디오를 선택하세요:", list(video_data.keys()))
video_info = video_data[video_title]

# --- 비디오 출력 ---
if video_info.get("url"):
    st.video(video_info["url"], start_time=0)
    st.caption(f"📌 출처: {video_info['출처']}")
else:
    st.warning("⚠️ 해당 영상은 준비 중입니다.")
    st.caption(f"📌 출처: {video_info['출처']}")
    st.stop()

# --- 퀴즈 출력 ---
if "퀴즈제목" in video_info:
    st.subheader("📋 영상 보고 난 후 퀴즈")

    quiz_key = f"{video_title}_quiz_passed"
    if quiz_key not in st.session_state:
        st.session_state[quiz_key] = False

    if st.session_state[quiz_key]:
        st.success("✅ 이미 퀴즈를 통과하셨습니다!")
    else:
        correct = video_info["답"]
        options = video_info["문제"]

        if isinstance(correct, list):
            user_answer = st.multiselect(video_info["퀴즈제목"], options)
        else:
            user_answer = st.radio(video_info["퀴즈제목"], options)

        if st.button("제출"):
            if isinstance(correct, list):
                if set(user_answer) == set(correct):
                    st.success("🎉 정답입니다!")
                    st.session_state.point += 30
                    st.session_state[quiz_key] = True
                    st.balloons()
                    time.sleep(0.5)
                    st.info("💰 포인트 +30 적립되었습니다.")
                else:
                    st.error("❌ 오답입니다. 다시 시도해보세요.")
            else:
                if user_answer == correct:
                    st.success("🎉 정답입니다!")
                    st.session_state.point += 30
                    st.session_state[quiz_key] = True
                    st.balloons()
                    time.sleep(0.5)
                    st.info("💰 포인트 +30 적립되었습니다.")
                else:
                    st.error("❌ 오답입니다. 다시 시도해보세요.")
