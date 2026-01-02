import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="푸드타파 성과 진단 시스템", layout="wide")

# 2. 데이터 로드 (마케터님 시트 주소 유지)
SHEET_ID = "1cYYSlXxnOwl7POi7tBrcdKLLGvlN2dDrWJ8XC5MU7-U"
GID = "1174906177" 
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = ['날짜', '방문자', '가입자', '게시글', '댓글', '탈퇴자'][:len(df.columns)]
        df['날짜'] = pd.to_datetime(df['날짜'].astype(str).str.strip(), errors='coerce')
        for col in ['방문자', '가입자', '게시글', '댓글', '탈퇴자']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)
        return df.dropna(subset=['날짜']).sort_values('날짜')
    except:
        return pd.DataFrame()

# --- 메인 화면 ---
st.title("🚀 푸드타파 마케팅 성과 진단 보고서")
df = load_data()

if not df.empty:
    # 지표 요약
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("오늘 방문자", f"{int(latest['방문자'])}명", f"{int(latest['방문자']-prev['방문자'])}")
    m2.metric("오늘 가입자", f"{int(latest['가입자'])}명", f"{int(latest['가입자']-prev['가입자'])}")
    m3.metric("누적 게시글", f"{int(df['게시글'].sum())}개")
    m4.metric("오늘 탈퇴자", f"{int(latest['탈퇴자'])}명", delta_color="inverse")

    st.divider()

    # 차트 분석
    view_type = st.sidebar.radio("분석 기준", ["일별", "주별", "월별"])
    st.line_chart(df.set_index('날짜')[['방문자', '가입자']])

    # --- 🕵️ 10년 차 마케터의 진단 섹션 ---
    st.header("📋 데이터 기반 마케팅 진단 & 제언")
    
    # 분석 변수 설정
    conv_rate = (latest['가입자'] / latest['방문자'] * 100) if latest['방문자'] > 0 else 0
    post_per_user = (latest['게시글'] / latest['가입자']) if latest['가입자'] > 0 else 0
    churn_rate = (latest['탈퇴자'] / latest['가입자'] * 100) if latest['가입자'] > 0 else 0

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🚩 주요 문제점")
        if conv_rate < 5:
            st.error(f"**방문자 대비 가입 전환율 저조** (현재 {conv_rate:.1f}%)\n\n방문자는 많으나 가입으로 이어지지 않고 있습니다. 카페 대문이나 소개글의 매력도를 점검해야 합니다.")
        if churn_rate > 10:
            st.error(f"**탈퇴자 비율 급증 주의** (현재 {churn_rate:.1f}%)\n\n탈퇴자가 늘고 있습니다. 광고성 콘텐츠가 과하거나 조개 뼈 처리 등 유저가 기대한 정보가 부족할 수 있습니다.")
        if post_per_user < 0.5:
            st.warning(f"**커뮤니티 활동성 저하**\n\n신규 가입자 대비 게시글 수가 적습니다. 유저 참여 유도형 이벤트가 시급합니다.")
        else:
            st.success("데이터가 전반적으로 안정적인 흐름을 보이고 있습니다.")

    with col_b:
        st.subheader("💡 개선 방법 제언")
        st.info("1. **콘텐츠 강화:** 푸드타파 유저들이 헷갈려 하는 '음식물 vs 일반 쓰레기' 구분법 콘텐츠를 시리즈로 기획해 보세요.")
        st.info("2. **이탈 방지:** 탈퇴자가 발생하는 시점에 유저 피드백을 수집하여 푸드타파 서비스의 개선점으로 연결해야 합니다.")
        st.info("3. **댓글 소통:** 현재 게시글당 댓글 수치를 모니터링하여, 마케터가 직접 '댓글1, 댓글2'와 같이 선제적으로 소통을 시작하는 것이 중요합니다.")

    st.divider()
    st.subheader("📊 전체 성과 리스트")
    st.dataframe(df.sort_values('날짜', ascending=False), use_container_width=True)

else:
    st.info("데이터 로드 중...")
