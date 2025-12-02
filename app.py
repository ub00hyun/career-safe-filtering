import streamlit as st
import pandas as pd

# ---------------------------
# 데이터 로드
# ---------------------------
@st.cache_data
def load_data():
    return pd.read_csv("프로젝트 최종본.csv", encoding="cp949")

df = load_data()

# HR 토픽 매핑 (코드 → 사용자 라벨)
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


# 라벨 → 코드 매핑 (역방향)
label_to_code = {v: k for k, v in topic_map.items()}

# rep_topic에서 코드만 추출 (T1, T2...)
df["topic_code"] = df["rep_topic"].str.extract(r"(T\d+)")
df["대표문제요약"] = df["topic_code"].map(topic_map)


# --------------------------------
# 세션 상태 초기화
# --------------------------------
if "excluded_codes" not in st.session_state:
    st.session_state.excluded_codes = []

if "phase" not in st.session_state:
    st.session_state.phase = "select_first"


# ---------------------------
# UI 제목
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

    available_labels = [
        t for t in topic_map.values()
        if label_to_code[t] not in st.session_state.excluded_codes
    ]

    choice = st.multiselect(
        "제외할 요인 선택",
        options=available_labels,
        key="first_select"
    )

    if st.button("요인 추가 / 다음"):
        for label in choice:
            st.session_state.excluded_codes.append(label_to_code[label])

        st.session_state.phase = "ask_more"
        st.rerun()


# =====================================================
#  PHASE 2 — 추가 제외 여부 / 결과
# =====================================================
if st.session_state.phase in ["ask_more", "result"]:

    if st.session_state.excluded_codes:
        excluded_labels = [topic_map[c] for c in st.session_state.excluded_codes]
        st.write("제외된 요인: " + ", ".join(excluded_labels))
    else:
        st.write("아직 제외된 요인이 없습니다.")

    more = st.radio(
        "추가로 제외하고 싶은 요인이 있습니까?",
        ["예", "아니요"],
        key="more_radio"
    )

    # 추가 선택
    if more == "예":

        available_more = [
            t for t in topic_map.values()
            if label_to_code[t] not in st.session_state.excluded_codes
        ]

        extra = st.multiselect(
            "추가로 제외할 요인 선택",
            options=available_more,
            key="extra_select"
        )

        if st.button("추가 제외 적용"):
            for label in extra:
                st.session_state.excluded_codes.append(label_to_code[label])

            st.rerun()

    # 결과 출력
    if more == "아니요":
        st.session_state.phase = "result"

        # 제외된 topic_code 제거
        result = df[~df["topic_code"].isin(st.session_state.excluded_codes)].copy()

        # 정렬
        sort_cols = ["별점", "rep_prob"]
        sort_cols = [c for c in sort_cols if c in result.columns]

        if sort_cols:
            result = result.sort_values(
                by=sort_cols,
                ascending=[False, True][:len(sort_cols)]
            )

        total_count = len(result)
        display_df = result.head(40)

        st.subheader(f"📊 추천 기업 Top {len(display_df)} (총 {total_count}개 기업 중)")

        # 표시 컬럼
        show_cols = ["company", "대표문제요약", "산업", "기업형태", "사원수"]
        for col in ["별점", "별점종합"]:
            if col in result.columns:
                show_cols.append(col)
                break

        st.dataframe(display_df[show_cols])
