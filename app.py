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

# --- [사이드바 자산 계산 로직 시작] ---
total_stock_value = 0  # 보유 주식 총 평가액

# 실시간 주가를 반영하여 내 포트폴리오의 가치 계산하기
for stock_name, info in list(st.session_state.portfolio.items()):
    if stock_name in STOCK_DICT and STOCK_DICT[stock_name][0] != "CUSTOM":
        t_code = STOCK_DICT[stock_name][0]
        c_type = STOCK_DICT[stock_name][1]
    else:
        try:
            t_code = stock_name.split("(")[1].replace(")", "")
            c_type = "KR" if (".KS" in t_code or ".KQ" in t_code) else "US"
        except:
            continue
            
    try:
        s_data = yf.Ticker(t_code).history(period="1d")
        if not s_data.empty:
            c_price = s_data['Close'].iloc[-1]
            c_price_krw = c_price * EXCHANGE_RATE if c_type == "US" else c_price
            
            # 이 주식의 현재 가치 = 현재가 * 수량
            stock_eval = c_price_krw * info["수량"]
            total_stock_value += stock_eval
            st.session_state.portfolio[stock_name]["현재가_원화"] = c_price_krw
    except:
        pass

# [핵심 계산 파트]
# 1. 총 평가 자산 = 내 현금 + 현재 보유한 주식들의 총 가치
total_assets = st.session_state.cash + total_stock_value
# 2. 총 투자 금액, 총 평가 손익 및 수익률 계산
total_invested = sum(info["매수총액_원화"] for info in st.session_state.portfolio.values())
total_profit = total_stock_value - total_invested
profit_rate = (total_profit / total_invested * 100) if total_invested > 0 else 0.0

# 3. 사이드바 - 투자 지갑 디자인 적용
st.sidebar.header("💰 내 투자 지갑")

# 메인 지표: 총 평가 자산을 보기 좋게 큰 글씨(metric)로 표시
st.sidebar.metric(label="📊 총 평가 자산 (예수금+투자금)", value=f"{total_assets:,.0f} 원")

# 세부 자산 현황을 깔끔하게 나열
st.sidebar.write(f"💵 보유 현금: {st.session_state.cash:,.0f} 원")
st.sidebar.write(f"📈 주식 평가액: {total_stock_value:,.0f} 원")

# [수익률 시각화 기능] 주식을 단 1주라도 가지고 있을 때만 손익 현황을 띄워줍니다.
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
        st.sidebar.write(f"- **{stock_name}**: {info['수량']}주")
        st.sidebar.caption(f"  (평단가: {avg_price:,.0f}원)")
else:
    st.sidebar.write("보유 중인 주식이 없습니다.")
# --- [사이드바 자산 계산 로직 끝] ---


# 4. 메인 화면 - 선택 박스
selected_option = st.selectbox("투자할 주식을 선택하거나 검색을 선택하세요 👇", list(STOCK_DICT.keys()))

if selected_option == "직접 검색해서 입력하기 🔍":
    search_ticker = st.text_input("조회하고 싶은 주식의 티커를 입력하세요 (예: MSFT, 005380.KS)", "MSFT").upper()
    ticker = search_ticker
    if ".KS" in ticker or ".KQ" in ticker or ticker.isdigit():
        country = "KR"
        if ticker.isdigit():
            ticker = ticker + ".KS"
        display_name = f"검색된 한국 주식 ({ticker})"
    else:
        country = "US"
        display_name = f"검색된 미국 주식 ({ticker})"
else:
    ticker = STOCK_DICT[selected_option][0]
    country = STOCK_DICT[selected_option][1]
    display_name = selected_option

try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1mo")
    
    if not df.empty:
        raw_price = df['Close'].iloc[-1]
        
        if country == "US":
            price_display = f"${raw_price:,.2f} (약 {raw_price * EXCHANGE_RATE:,.0f} 원)"
            current_price_krw = raw_price * EXCHANGE_RATE
        else:
            price_display = f"{raw_price:,.0f} 원"
            current_price_krw = raw_price
            
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"### {display_name}")
            st.metric(label="현재 주가", value=price_display)
            
            quantity = st.number_input("거래 수량 선택", min_value=1, value=1, step=1)
            total_cost_krw = current_price_krw * quantity
            st.write(f"총 거래 금액: **{total_cost_krw:,.0f} 원**")
            
            btn_buy, btn_sell = st.columns(2)
            
            with btn_buy:
                if st.button("🔴 매수하기", use_container_width=True):
                    if st.session_state.cash >= total_cost_krw:
                        st.session_state.cash -= total_cost_krw
                        
                        # 포트폴리오 구조에 맞게 저장
                        if display_name not in st.session_state.portfolio:
                            st.session_state.portfolio[display_name] = {"수량": 0, "매수총액_원화": 0}
                        
                        st.session_state.portfolio[display_name]["수량"] += quantity
                        st.session_state.portfolio[display_name]["매수총액_원화"] += total_cost_krw
                        
                        st.success(f"{display_name} {quantity}주 매수 완료!")
                        st.rerun()
                    else:
                        st.error("잔액이 부족합니다!")
                        
            with btn_sell:
                if st.button("🔵 매도하기", use_container_width=True):
                    if display_name in st.session_state.portfolio and st.session_state.portfolio[display_name]["수량"] >= quantity:
                        # 평단가 기준으로 매수총액 차감
                        avg_p = st.session_state.portfolio[display_name]["매수총액_원화"] / st.session_state.portfolio[display_name]["수량"]
                        
                        st.session_state.cash += total_cost_krw
                        st.session_state.portfolio[display_name]["수량"] -= quantity
                        st.session_state.portfolio[display_name]["매수총액_원화"] -= (avg_p * quantity)
                        
                        if st.session_state.portfolio[display_name]["수량"] == 0:
                            del st.session_state.portfolio[display_name]
                            
                        st.success(f"{display_name} {quantity}주 매도 완료!")
                        st.rerun()
                    else:
                        st.error("보유 수량이 부족합니다!")

        with col2:
            st.subheader("📊 최근 1개월 주가 흐름")
            st.line_chart(df['Close'])
            
    else:
        st.warning("존재하지 않는 티커이거나 데이터를 불러올 수 없습니다.")
        
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
