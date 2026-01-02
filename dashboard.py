import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="푸드타파 성과 진단 시스템", layout="wide")

# 2. 고정 주소 설정
SHEET_ID = "1cYYSlXxnOwl7POi7tBrcdKLLGvlN2dDrWJ8XC5MU7-U"
GID = "1174906177" 
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=10)
def load_and_process():
    try:
        # 데이터 긁어오기
        df = pd.read_csv(URL)
        
        # 열 이름 강제 매칭 (날짜, 방문자, 가입자, 게시글, 댓글, 탈퇴자 순서)
        df.columns = ['날짜', '방문자', '가입자', '게시글', '댓글', '탈퇴자'][:len(df.columns)]
        
        # 날짜 형식 정리
        df['날짜'] = pd.to_datetime(df['날짜'].astype(str).str.strip(), errors='coerce')
        
        # 숫자 형식 정리 (콤마 제거 등)
        for col in ['방문자', '가입자', '게시글', '댓글', '탈퇴자']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)
        
        return df.dropna(subset=['날짜']).sort_values('날짜')
    except Exception as e:
        st.error(f"데이터 처리 중 오류: {e}")
        return pd.DataFrame()

# --- 대시보드 메인 ---
st.title("🚀 푸드타파 마케팅 실시간 대시보드")

df = load_and_process()

if not df.empty:
    # 3. 상단 요약 지표 (가장 최근 데이터 기준)
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("오늘 방문자", f"{int(latest['방문자'])}명", f"{int(latest['방문자'] - prev['방문자'])}")
    col2.metric("오늘 가입자", f"{int(latest['가입자'])}명", f"{int(latest['가입자'] - prev['가입자'])}")
    col3.metric("오늘 게시글", f"{int(latest['게시글'])}개")
    col4.metric("오늘 탈퇴자", f"{int(latest['탈퇴자'])}명", delta_color="inverse")

    st.divider()

    # 4. 사이드바 분석 설정
    with st.sidebar:
        st.header("📊 분석 기간 설정")
        view_type = st.radio("집계 기준 선택", ["일별", "주별", "월별"])
        metrics = ['방문자', '가입자', '게시글', '댓글', '탈퇴자']
        selected = st.multiselect("확인할 지표", metrics, default=['방문자', '가입자'])

    # 5. 집계 로직 (일/주/월)
    # 주차와 월별 날짜 생성
    df['주차'] = df['날짜'].dt.to_period('W').apply(lambda r: r.start_time)
    df['월별'] = df['날짜'].dt.to_period('M').apply(lambda r: r.start_time)
    
    if view_type == "주별":
        display_df = df.groupby('주차').sum(numeric_only=True).reset_index().rename(columns={'주차': '날짜'})
    elif view_type == "월별":
        display_df = df.groupby('월별').sum(numeric_only=True).reset_index().rename(columns={'월별': '날짜'})
    else:
        display_df = df.copy()

    # 차트 출력
    if selected:
        st.line_chart(display_df.set_index('날짜')[selected])
    
    # 데이터 테이블
    st.subheader(f"📋 {view_type} 성과 리스트")
    st.dataframe(display_df.sort_values('날짜', ascending=False), use_container_width=True)

else:
    st.info("데이터 로딩 중입니다... 시트에 데이터를 입력해 주세요.")