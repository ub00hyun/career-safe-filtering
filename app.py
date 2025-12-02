import streamlit as st
import pandas as pd

# ---------------------------
# 데이터 로드
# ---------------------------
@st.cache_data
def load_data():
    return pd.read_csv("프로젝트 최종본.csv", encoding="cp949")
    return df

df = load_data()

# HR 토픽 매핑 (표시용 라벨)
topic_map = {
    "T1": "워라밸 / 복지",
    "T2": "계약직·전환 문제",
    "T3": "업무 강도 / 편차",
    "T4": "조직문화 / 리더십",
    "T5": "근무환경 열악",
    "T6": "비효율적 문서 작업",
    "T7": "성장성 부족",
    "T8": "사내 정치 / 불공정",
    "T9": "경영진 문제",
    "T10": "팀·부서 배정 문제",
    "T11": "보상 / 임금 문제",
}

# --------------------------------
# 세션 상태 초기화
# --------------------------------
if "excluded_topics" not in st.session_state:
    st.session_state.excluded_topics = []    # 사람이 보는 레이블로 저장

if "phase" not in st.session_state:
    st.session_state.phase = "select_first"  # select_first → ask_more → result

# ---------------------------
# 제목
# ---------------------------
st.markdown("""
# 🛡️ 커리어 세이프 필터링
현직자 리뷰 기반 HR 리스크 제거형 기업 추천 서비스입니다.
""")

st.subheader("❌ 피하고 싶은 HR 리스크를 선택하세요.")

# =====================================================
#  PHASE 1 — 첫 요인 선택
# =====================================================
if st.session_state.phase == "select_first":

    available = [
        t for t in topic_map.values()
        if t not in st.session_state.excluded_topics
    ]

    choice = st.multiselect(
        "제외할 요인 선택",
        options=available,
        key="first_select"
    )

    if st.button("요인 추가 / 다음"):
        st.session_state.excluded_topics.extend(choice)
        st.session_state.phase = "ask_more"
        st.rerun()


# =====================================================
#  PHASE 2 — 추가 제외 여부
# =====================================================
if st.session_state.phase in ["ask_more", "result"]:

    if st.session_state.excluded_topics:
        st.write("제외된 요인: " + ", ".join(st.session_state.excluded_topics))
    else:
        st.write("현재까지 제외된 요인이 없습니다.")

    more = st.radio(
        "추가로 제외하고 싶은 요인이 있습니까?",
        ["예", "아니요"],
        key="more_radio"
    )

    # -----------------------
    # 추가 제외
    # -----------------------
    if more == "예":

        available_more = [
            t for t in topic_map.values()
            if t not in st.session_state.excluded_topics
        ]

        extra = st.multiselect(
            "추가로 제외할 요인 선택",
            options=available_more,
            key="extra_select"
        )

        if st.button("추가 제외 적용"):
            st.session_state.excluded_topics.extend(extra)
            st.rerun()

    # -----------------------
    # 추천 결과 생성
    # -----------------------
    if more == "아니요":
        st.session_state.phase = "result"

        # 제외 주제 기반 필터링
        result = df[~df["rep_topic"].isin(st.session_state.excluded_topics)].copy()

        # 정렬 기준: 별점 높은 순, rep_prob 낮은 순
        sort_cols = ["별점", "rep_prob"]
        sort_cols = [c for c in sort_cols if c in result.columns]

        if sort_cols:
            result = result.sort_values(
                by=sort_cols,
                ascending=[False, True][:len(sort_cols)]
            )

                # 전체 필터링된 기업 수
        total_count = len(result)

        # 상위 40개만 표시
        display_df = result.head(40)
        display_count = len(display_df)

        st.subheader(f"📊 추천 기업 Top {display_count} (총 {total_count}개 기업 중)")


        # 표시할 컬럼 자동 인식
        show_cols = ["company", "rep_topic", "산업", "기업형태", "사원수"]
        for col in ["별점", "별점종합"]:
            if col in result.columns:
                show_cols.append(col)
                break

        st.dataframe(result[show_cols])
