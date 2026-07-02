import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(layout="wide")
st.title("📈 나만의 주식 모의투자 시뮬레이터")

# 2. 유저 데이터 초기화 (세션 상태 활용)
# 새로고침을 해도 이 자산 데이터는 유지됩니다.
if 'cash' not in st.session_state:
    st.session_state.cash = 10000000  # 초기 자본: 1,000만 원
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # 보유 주식 현황 {티커: 수량}

# 3. 사이드바 - 내 자산 현황 표시
st.sidebar.header("💰 내 투자 지갑")
st.sidebar.subheader(f"보유 현금: {st.session_state.cash:,.0f} 원")

st.sidebar.write("---")
st.sidebar.subheader("💼 내 포트폴리오")
if st.session_state.portfolio:
    for ticker, q in st.session_state.portfolio.items():
        st.sidebar.write(f"- **{ticker}**: {q}주 보유")
else:
    st.sidebar.write("보유 중인 주식이 없습니다.")

# 4. 메인 화면 - 주식 검색
ticker = st.text_input("조회하고 싶은 주식의 티커를 입력하세요 (예: AAPL, TSLA, 005930.KS)", "AAPL").upper()

try:
    # 주가 데이터 가져오기 (최근 1개월)
    stock = yf.Ticker(ticker)
    df = stock.history(period="1mo")
    
    if not df.empty:
        # 환율 계산을 생략하고 1달러 = 1,300원으로 가정하거나, 미국 주식 그대로 계산 (여기선 편의상 달러 표기)
        current_price = round(df['Close'].iloc[-1], 2)
        
        # 주가 정보 및 차트 출력
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(label=f"{ticker} 현재가", value=f"${current_price}")
            
            # 매수/매도 수량 입력
            quantity = st.number_input("거래 수량 선택", min_value=1, value=1, step=1)
            total_cost = current_price * quantity
            st.write(f"총 거래 금액: **${total_cost:,.2f}**")
            
            # 매수 / 매도 버튼
            btn_buy, btn_sell = st.columns(2)
            
            with btn_buy:
                if st.button("🔴 매수하기", use_container_width=True):
                    # 가상의 환율 1달러 = 1,400원 가정하여 원화 차감
                    required_krw = total_cost * 1400 
                    if st.session_state.cash >= required_krw:
                        st.session_state.cash -= required_krw
                        st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + quantity
                        st.success(f"{ticker} {quantity}주 매수 완료!")
                        st.rerun()
                    else:
                        st.error("잔액이 부족합니다!")
                        
            with btn_sell:
                if st.button("🔵 매도하기", use_container_width=True):
                    if st.session_state.portfolio.get(ticker, 0) >= quantity:
                        gain_krw = total_cost * 1400
                        st.session_state.cash += gain_krw
                        st.session_state.portfolio[ticker] -= quantity
                        
                        # 수량이 0이 되면 포트폴리오에서 삭제
                        if st.session_state.portfolio[ticker] == 0:
                            del st.session_state.portfolio[ticker]
                            
                        st.success(f"{ticker} {quantity}주 매도 완료!")
                        st.rerun()
                    else:
                        st.error("보유 수량이 부족합니다!")

        with col2:
            st.subheader(f"📊 {ticker} 최근 1개월 주가 흐름")
            st.line_chart(df['Close'])
            
    else:
        st.warning("존재하지 않는 티커이거나 데이터를 불러올 수 없습니다.")
        
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
