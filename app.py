import streamlit as st
import yfinance as yf
import pandas as pd
import random
import time
from datetime import datetime

# 1. 페이지 설정 및 제목
st.set_page_config(layout="wide")
st.title("📈 초간단 국내/해외 주식 모의투자 시뮬레이터 (with 상점 🏪)")

# 가상의 환율 설정 (1달러 = 1,400원)
EXCHANGE_RATE = 1400

# 주식 선택 리스트 설정
STOCK_DICT = {
    "💀 코인주 🎰": ["RANDOM", "KR"],
    "삼성전자 🇰🇷": ["005930.KS", "KR"],
    "SK하이닉스 🇰🇷": ["000660.KS", "KR"],
    "애플 (Apple) 🇺🇸": ["AAPL", "US"],
    "테슬라 (Tesla) 🇺🇸": ["TSLA", "US"],
    "엔비디아 (NVIDIA) 🇺🇸": ["NVDA", "US"],
    "구글 (Google) 🇺🇸": ["GOOGL", "US"],
    "직접 검색해서 입력하기 🔍": ["CUSTOM", "CUSTOM"]
}

# 🛒 상점 아이템 도감 설정 (가격 및 아이콘)
SHOP_ITEMS = {
    "☕ 스타벅스 아이스 아메리카노": 5000,
    "🍗 치킨 기프티콘 (+콜라)": 25000,
    "닌텐도 스위치 🎮": 360000,
    "아이폰 17 프로 맥스 📱": 1800000,
    "롤렉스 서브마리너 시계 ⌚": 15000000,
    "포르쉐 911 카레라 🏎️": 160000000,
    "시그니엘 펜트하우스  penthouse 🏙️": 5000000000
}

# 2. 유저 데이터 및 세션 초기화
if 'cash' not in st.session_state:
    st.session_state.cash = 10000  # 초기 자본: 1,000만 원
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # {주식이름: {"수량": q, "매수총액_원화": total_cost}}
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []  # 거래 내역 리스트
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}  # 🎒 {아이템이름: 보유개수} 상점 인벤토리 추가!

# 랜덤 주식 가격 변동 로직
if 'random_stock_price' not in st.session_state:
    st.session_state.random_stock_price = 10000.0
if 'random_history' not in st.session_state:
    st.session_state.random_history = [10000.0] * 10

change_percent = random.uniform(-0.45, 0.45)
st.session_state.random_stock_price *= (1 + change_percent)

if st.session_state.random_stock_price < 10:
    st.session_state.random_stock_price = 10.0

st.session_state.random_history.append(st.session_state.random_stock_price)
if len(st.session_state.random_history) > 20:
    st.session_state.random_history.pop(0)


# --- [사이드바 자산 계산 로직] ---
total_stock_value = 0

for stock_name, info in list(st.session_state.portfolio.items()):
    if "코인주" in stock_name:
        total_stock_value += (st.session_state.random_stock_price * info["수량"])
        continue

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
            total_stock_value += (c_price_krw * info["수량"])
    except:
        pass

total_invested = sum(info["매수총액_원화"] for info in st.session_state.portfolio.values())

if total_invested > 0:
    total_assets = st.session_state.cash + total_stock_value
    total_profit = total_stock_value - total_invested
    profit_rate = (total_profit / total_invested) * 100
else:
    total_stock_value = 0
    total_assets = st.session_state.cash
    total_profit = 0
    profit_rate = 0.0

# 3. 사이드바 화면
st.sidebar.header("💰 내 투자 지갑")
st.sidebar.metric(label="📊 총 평가 자산 (예수금+투자금)", value=f"{total_assets:,.0f} 원")
st.sidebar.write(f"💵 보유 현금: {st.session_state.cash:,.0f} 원")
st.sidebar.write(f"📈 주식 평가액: {total_stock_value:,.0f} 원")

if total_invested > 0:
    st.sidebar.write("---")
    st.sidebar.metric(
        label="📉 총 평가 손익 (수익률)", 
        value=f"{total_profit:+,.0f} 원", 
        delta=f"{profit_rate:+.2f}%"
    )

# 🎒 [추가] 내 인벤토리 대시보드
st.sidebar.write("---")
st.sidebar.subheader("🎒 내 아이템 가방")
owned_items = {k: v for k, v in st.session_state.inventory.items() if v > 0}
if owned_items:
    for item_name, qty in owned_items.items():
        st.sidebar.write(f"✨ **{item_name}** x {qty}개")
else:
    st.sidebar.write("아직 획득한 아이템이 없습니다. 상점에서 플렉스 하세요!")

st.sidebar.write("---")
st.sidebar.subheader("💼 내 포트폴리오")
if st.session_state.portfolio:
    for stock_name, info in st.session_state.portfolio.items():
        avg_price = info["매수총액_원화"] / info["수량"]
        st.sidebar.write(f"- **{stock_name}**: {info['수량']}주")
        st.sidebar.caption(f"  (평단가: {avg_price:,.0f}원)")
else:
    st.sidebar.write("보유 중인 주식이 없습니다.")

st.sidebar.write("---")
st.sidebar.subheader("📜 실시간 거래 히스토리")
if st.session_state.trade_history:
    for log in reversed(st.session_state.trade_history):
        st.sidebar.caption(log)
else:
    st.sidebar.write("아직 거래 내역이 없습니다.")


# 4. 메인 화면 상단 탭 나누기 (주식 거래 vs 아이템 상점)
tab_trade, tab_shop = st.tabs(["📊 주식 모의투자 거래소", "🏪 플렉스 아이템 상점"])

# ==================== [탭 1: 주식 거래기능] ====================
with tab_trade:
    selected_option = st.selectbox("투자할 주식을 선택하거나 검색을 선택하세요 👇", list(STOCK_DICT.keys()), key="main_stock_select")

    if "코인주" in selected_option:
        display_name = "💀 코인주 🎰"
        current_price_krw = st.session_state.random_stock_price
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### {display_name}")
            st.metric(label="현재 주가 (1초마다 자동 변동)", value=f"{current_price_krw:,.0f} 원")
            
            current_owned = st.session_state.portfolio.get(display_name, {}).get("수량", 0)
            st.info(f"💼 **현재 내 보유 수량: {current_owned}주**")
            
            quantity = st.number_input("거래 수량 선택", min_value=1, value=1, step=1, key="rand_qty")
            total_cost_krw = current_price_krw * quantity
            st.write(f"총 거래 금액: **{total_cost_krw:,.0f} 원**")
            
            btn_buy, btn_sell = st.columns(2)
            with btn_buy:
                if st.button("🔴 매수하기", use_container_width=True, key="rand_buy"):
                    if st.session_state.cash >= total_cost_krw:
                        st.session_state.cash -= total_cost_krw
                        if display_name not in st.session_state.portfolio:
                            st.session_state.portfolio[display_name] = {"수량": 0, "매수총액_원화": 0}
                        st.session_state.portfolio[display_name]["수량"] += quantity
                        st.session_state.portfolio[display_name]["매수총액_원화"] += total_cost_krw
                        
                        now_str = datetime.now().strftime("%H:%M:%S")
                        st.session_state.trade_history.append(f"[{now_str}] 🔴 매수: 💀 코인주 🎰 {quantity}주")
                        st.success(f"{display_name} {quantity}주 매수 완료!")
                        st.rerun()
                    else:
                        st.error("잔액이 부족합니다!")
                        
            with btn_sell:
                if st.button("🔵 매도하기", use_container_width=True, key="rand_sell"):
                    if display_name in st.session_state.portfolio and st.session_state.portfolio[display_name]["수량"] >= quantity:
                        avg_p = st.session_state.portfolio[display_name]["매수총액_원화"] / st.session_state.portfolio[display_name]["수량"]
                        st.session_state.cash += total_cost_krw
                        st.session_state.portfolio[display_name]["수량"] -= quantity
                        st.session_state.portfolio[display_name]["매수총액_원화"] -= (avg_p * quantity)
                        
                        now_str = datetime.now().strftime("%H:%M:%S")
                        st.session_state.trade_history.append(f"[{now_str}] 🔵 매도: 💀 코인주 🎰 {quantity}주")
                        
                        if st.session_state.portfolio[display_name]["수량"] == 0:
                            del st.session_state.portfolio[display_name]
                        st.success(f"{display_name} {quantity}주 매도 완료!")
                        st.rerun()
                    else:
                        st.error("보유 수량이 부족합니다!")
                        
        with col2:
            st.subheader("📊 실시간 떡락 주의 차트")
            st.line_chart(st.session_state.random_history)
            
        time.sleep(1)
        st.rerun()

    else:
        # 기존 실제 주식 및 검색 로직
        if selected_option == "직접 검색해서 입력하기 🔍":
            search_ticker = st.text_input("조회하고 싶은 주식의 티커를 입력하세요 (예: MSFT, 005380.KS)", "MSFT", key="custom_ticker_input").upper()
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
                current_price_krw = raw_price * EXCHANGE_RATE if country == "US" else raw_price
                    
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"### {display_name}")
                    
                    if country == "US":
                        metric_col1, metric_col2 = st.columns(2)
                        with metric_col1:
                            st.metric(label="현재 주가 (달러)", value=f"${raw_price:,.2f}")
                        with metric_col2:
                            st.metric(label="원화 환산 가격 (적용 환율: 1,400원)", value=f"약 {current_price_krw:,.0f} 원")
                    else:
                        st.metric(label="현재 주가", value=f"{raw_price:,.0f} 원")
                    
                    current_owned = st.session_state.portfolio.get(display_name, {}).get("수량", 0)
                    st.info(f"💼 **현재 내 보유 수량: {current_owned}주**")
                    
                    quantity = st.number_input("거래 수량 선택", min_value=1, value=1, step=1, key="normal_qty")
                    total_cost_krw = current_price_krw * quantity
                    st.write(f"총 거래 금액: **{total_cost_krw:,.0f} 원**")
                    
                    btn_buy, btn_sell = st.columns(2)
                    with btn_buy:
                        if st.button("🔴 매수하기", use_container_width=True, key="normal_buy"):
                            if st.session_state.cash >= total_cost_krw:
                                st.session_state.cash -= total_cost_krw
                                if display_name not in st.session_state.portfolio:
                                    st.session_state.portfolio[display_name] = {"수량": 0, "매수총액_원화": 0}
                                st.session_state.portfolio[display_name]["수량"] += quantity
                                st.session_state.portfolio[display_name]["매수총액_원화"] += total_cost_krw
                                
                                now_str = datetime.now().strftime("%H:%M:%S")
                                st.session_state.trade_history.append(f"[{now_str}] 🔴 매수: {display_name} {quantity}주")
                                st.success(f"{display_name} {quantity}주 매수 완료!")
                                st.rerun()
                            else:
                                st.error("잔액이 부족합니다!")
                                
                    with btn_sell:
                        if st.button("🔵 매도하기", use_container_width=True, key="normal_sell"):
                            if display_name in st.session_state.portfolio and st.session_state.portfolio[display_name]["수량"] >= quantity:
                                avg_p = st.session_state.portfolio[display_name]["매수총액_원화"] / st.session_state.portfolio[display_name]["수량"]
                                st.session_state.cash += total_cost_krw
                                st.session_state.portfolio[display_name]["수량"] -= quantity
                                st.session_state.portfolio[display_name]["매수총액_원화"] -= (avg_p * quantity)
                                
                                now_str = datetime.now().strftime("%H:%M:%S")
                                st.session_state.trade_history.append(f"[{now_str}] 🔵 매도: {display_name} {quantity}주")
                                
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

# ==================== [탭 2: 아이템 상점 기능] ====================
with tab_shop:
    st.header("🏪 모의투자 플렉스 백화점")
    st.write("주식투자로 번 현금(`보유 현금`)으로 살 수 있는 초호화 보상 리스트입니다. 한강 갈지 펜트하우스 갈지 증명해 보세요!")
    st.write(f"💵 **내 보유 현금: {st.session_state.cash:,.0f} 원**")
    st.write("---")
    
    # 그리드 레이아웃으로 아이템 리스트 나열하기
    cols = st.columns(3)
    for index, (item_name, price) in enumerate(SHOP_ITEMS.items()):
        with cols[index % 3]:
            st.subheader(item_name)
            st.write(f"💰 가격: **{price:,.0f} 원**")
            
            # 아이템 구매 버튼 만들기
            if st.button(f"🛒 {item_name.split()[0]} 구매", key=f"buy_item_{index}", use_container_width=True):
                if st.session_state.cash >= price:
                    st.session_state.cash -= price
                    # 인벤토리에 아이템 개수 추가
                    st.session_state.inventory[item_name] = st.session_state.inventory.get(item_name, 0) + 1
                    
                    # 거래 히스토리에 상점 구매 내역도 기록!
                    now_str = datetime.now().strftime("%H:%M:%S")
                    st.session_state.trade_history.append(f"[{now_str}] 🏪 상점: {item_name} 1개 구입")
                    
                    st.success(f"🎉 {item_name} 구매 성공! 인벤토리에 저장되었습니다.")
                    st.rerun()
                else:
                    st.error("❌ 현금이 부족합니다! 주식으로 돈을 더 벌어오세요.")
