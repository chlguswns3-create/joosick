import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(layout="wide")
st.title("📈 초간단 국내/해외 주식 모의투자 시뮬레이터")

# 가상의 환율 설정 (1달러 = 1,400원)
EXCHANGE_RATE = 1400

# 주식 선택 리스트 설정 (화면 표시 이름: [yfinance 티커, 국가])
STOCK_DICT = {
    "삼성전자 🇰🇷": ["005930.KS", "KR"],
    "SK하이닉스 🇰🇷": ["000660.KS", "KR"],
    "애플 (Apple) 🇺🇸": ["AAPL", "US"],
    "테슬라 (Tesla) 🇺🇸": ["TSLA", "US"],
    "엔비디아 (NVIDIA) 🇺🇸": ["NVDA", "US"],
    "구글 (Google) 🇺🇸": ["GOOGL", "US"]
}

# 2. 유저 데이터 초기화 (세션 상태 활용 - 모든 자산은 '원화' 기준)
if 'cash' not in st.session_state:
    st.session_state.cash = 10000000  # 초기 자본: 1,000만 원
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # 보유 주식 현황 {주식이름: 수량}

# 3. 사이드바 - 내 자산 현황 표시
st.sidebar.header("💰 내 투자 지갑")
st.sidebar.subheader(f"보유 현금: {st.session_state.cash:,.0f} 원")

st.sidebar.write("---")
st.sidebar.subheader("💼 내 포트폴리오")
if st.session_state.portfolio:
    for stock_name, q in st.session_state.portfolio.items():
        st.sidebar.write(f"- **{stock_name}**: {q}주 보유")
else:
    st.sidebar.write("보유 중인 주식이 없습니다.")

# 4. 메인 화면 - [변경 포인트] 검색창 대신 선택 박스(Selectbox) 사용!
selected_stock = st.selectbox("투자할 주식을 선택하세요 👇", list(STOCK_DICT.keys()))

# 선택된 주식의 정보 가져오기
ticker = STOCK_DICT[selected_stock][0]
country = STOCK_DICT[selected_stock][1]

try:
    # 주가 데이터 가져오기 (최근 1개월)
    stock = yf.Ticker(ticker)
    df = stock.history(period="1mo")
    
    if not df.empty:
        # 원래 가격 (미국 주식은 달러, 한국 주식은 원화로 가져옴)
        raw_price = df['Close'].iloc[-1]
        
        # 화면에 표시할 가격 및 실제 계산할 원화 가격 설정
        if country == "US":
            price_display = f"${raw_price:,.2f} (약 {raw_price * EXCHANGE_RATE:,.0f} 원)"
            current_price_krw = raw_price * EXCHANGE_RATE
        else:
            price_display = f"{raw_price:,.0f} 원"
            current_price_krw = raw_price
            
        # 주가 정보 및 차트 출력
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"### {selected_stock}")
            st.metric(label="현재 주가", value=price_display)
            
            # 매수/매도 수량 입력
            quantity = st.number_input("거래 수량 선택", min_value=1, value=1, step=1)
            total_cost_krw = current_price_krw * quantity
            st.write(f"총 거래 금액: **{total_cost_krw:,.0f} 원**")
            
            # 매수 / 매도 버튼
            btn_buy, btn_sell = st.columns(2)
            
            with btn_buy:
                if st.button("🔴 매수하기", use_container_width=True):
                    if st.session_state.cash >= total_cost_krw:
                        st.session_state.cash -= total_cost_krw
                        st.session_state.portfolio[selected_stock] = st.session_state.portfolio.get(selected_stock, 0) + quantity
                        st.success(f"{selected_stock} {quantity}주 매수 완료!")
                        st.rerun()
                    else:
                        st.error("잔액이 부족합니다!")
                        
            with btn_sell:
                if st.button("🔵 매도하기", use_container_width=True):
                    if st.session_state.portfolio.get(selected_stock, 0) >= quantity:
                        st.session_state.cash += total_cost_krw
                        st.session_state.portfolio[selected_stock] -= quantity
                        
                        if st.session_state.portfolio[selected_stock] == 0:
                            del st.session_state.portfolio[selected_stock]
                            
                        st.success(f"{selected_stock} {quantity}주 매도 완료!")
                        st.rerun()
                    else:
                        st.error("보유 수량이 부족합니다!")

        with col2:
            st.subheader("📊 최근 1개월 주가 흐름")
            st.line_chart(df['Close'])
            
    else:
        st.warning("데이터를 불러올 수 없습니다.")
        
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
