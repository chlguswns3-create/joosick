import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(layout="wide")
st.title("📈 초간단 국내/해외 주식 모의투자 시뮬레이터")

# 가상의 환율 설정 (1달러 = 1,400원)
EXCHANGE_RATE = 1400

# 주식 선택 리스트 설정
STOCK_DICT = {
    "삼성전자 🇰🇷": ["005930.KS", "KR"],
    "SK하이닉스 🇰🇷": ["000660.KS", "KR"],
    "애플 (Apple) 🇺🇸": ["AAPL", "US"],
    "테슬라 (Tesla) 🇺🇸": ["TSLA", "US"],
    "엔비디아 (NVIDIA) 🇺🇸": ["NVDA", "US"],
    "구글 (Google) 🇺🇸": ["GOOGL", "US"],
    "직접 검색해서 입력하기 🔍": ["CUSTOM", "CUSTOM"]
}

# 2. 유저 데이터 초기화
if 'cash' not in st.session_state:
    st.session_state.cash = 10000000  # 초기 자본: 1,000만 원
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # {주식이름: {"수량": q, "매수총액_원화": total_cost}}

# --- [사이드바 실시간 자산 및 수익률 계산] ---
total_stock_value = 0  # 보유 주식의 현재 총 가치

for stock_name, info in list(st.session_state.portfolio.items()):
    # 티커와 국가 판별
    if stock_name in STOCK_DICT and STOCK_DICT[stock_name][0] != "CUSTOM":
        t_code = STOCK_DICT[stock_name][0]
        c_type = STOCK_DICT[stock_name][1]
    else:
        try:
            t_code = stock_name.split("(")[1].replace(")", "")
            c_type = "KR" if (".KS" in t_code or ".KQ" in t_code) else "US"
        except:
            continue
            
    # 실시간 현재가 긁어오기
    try:
        s_data = yf.Ticker(t_code).history(period="1d")
        if not s_data.empty:
            c_price = s_data['Close'].iloc[-1]
            c_price_krw = c_price * EXCHANGE_RATE if c_type == "US" else c_price
            
            # 주식 평가액 누적
            total_stock_value += (c_price_krw * info["수량"])
    except:
        # 에러 시 계산에서 제외하거나 이전 데이터 유지
        pass

# 1번 기능: 총 평가 자산 (현금 + 주식 현재 가치)
total_assets = st.session_state.cash + total_stock_value

# 2번 기능: 총 평가 손익 및 수익률 계산
total_invested = sum(info["매수총액_원화"] for info in st.session_state.portfolio.values())
total_profit = total_stock_value - total_invested
profit_rate = (total_profit / total_invested * 100) if total_invested > 0 else 0.0

# 3. 사이드바 화면 그려주기
st.sidebar.header("💰 내 투자 지갑")

# 총 평가 자산 표시 (대형 글씨)
st.sidebar.metric(label="총 평가 자산", value=f"{total_assets:,.0f} 원")
st.sidebar.write(f"💵 보유 현금: {st.session_state.cash:,.0f} 원")
st.sidebar.write(f"📊 주식 평가액: {total_stock_value:,.0f} 원")

# 주식을 보유하고 있을 때만 수익률 메트릭 표시 (플러스/마이너스 색상 자동 적용)
if total_invested > 0:
    st.sidebar.write("---")
    st.sidebar.metric(
        label="📉 총 평가 손익 (수익률)", 
        value=f"{total_profit:+, .0f} 원", 
        delta=f"{profit_rate:+.2f}%"
    )

st.sidebar.write("---")
st.sidebar.subheader("💼 내 포트폴리오")
if st.session_state.portfolio:
    for stock_name, info in st.session_state.portfolio.items():
        avg_price = info["매수총액_원화"] / info["수량"]
        st
