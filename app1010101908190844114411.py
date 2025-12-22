import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 라이브러리 체크 및 자동 새로고침 설정
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("requirements.txt에 streamlit-autorefresh를 추가하고 Reboot 해주세요.")
    st.stop()

st.set_page_config(page_title="익스트림 100종목 거래소", layout="wide")
st_autorefresh(interval=1000, key="datarefresh")

# --- 1. 종목 리스트 설정 (해외/국내 각 50개) ---
if 'stock_list' not in st.session_state:
    us_names = ["Apple", "Nvidia", "Tesla", "Microsoft", "Amazon", "Google", "Meta", "Netflix", "AMD", "Intel", 
                "Adobe", "Salesforce", "Oracle", "Cisco", "Broadcom", "Qualcomm", "Texas Inst.", "Micron", "PayPal", "Starbucks",
                "Disney", "Nike", "Boeing", "Coca-Cola", "Pepsi", "Visa", "Mastercard", "Goldman Sachs", "JPMorgan", "Morgan Stanley",
                "ExxonMobil", "Chevron", "Pfizer", "Moderna", "Johnson&Johnson", "Walmart", "Costco", "Home Depot", "McDonalds", "Uber",
                "Airbnb", "Snapchat", "Spotify", "Palantir", "Coinbase", "Roblox", "Unity", "Zoom", "Shopify", "Square"]
    
    kr_names = ["삼성전자", "SK하이닉스", "LG엔솔", "삼성바이오", "현대차", "기아", "셀트리온", "POSCO홀딩스", "NAVER", "LG화학",
                "삼성SDI", "카카오", "KB금융", "신한지주", "현대모비스", "포스코퓨처엠", "삼성물산", "에코프로", "에코프로비엠", "카카오뱅크",
                "메리츠금융", "HMM", "삼성화재", "KT&G", "고려아연", "SK이노베이션", "한화에어로", "두산에너빌리티", "LG전자", "카카오페이",
                "삼성전기", "크래프톤", "엔씨소프트", "넷마블", "하이브", "S-Oil", "대한항공", "아모레퍼시픽", "KT", "SK텔레콤",
                "LG유플러스", "한국전력", "우리금융", "하나금융", "기업은행", "삼성중공업", "HD현대중공업", "한화솔루션", "현대건설", "금호석유"]

    st.session_state.US_STOCKS = {f"US_{i+1:02d}": name for i, name in enumerate(us_names)}
    st.session_state.KR_STOCKS = {f"KR_{i+1:02d}": name for i, name in enumerate(kr_names)}

# --- 2. 세션 상태 초기화 ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'price_history' not in st.session_state: st.session_state.price_history = {}

# --- 3. 가격 생성기 (1초 변동 + 5분 주기 120% 변동 로직) ---
def get_extreme_price_data(ticker):
    now = datetime.now()
    if ticker not in st.session_state.price_history:
        base_price = 100.0 if "US" in ticker else 50000.0
        df = pd.DataFrame([[now - timedelta(seconds=1), base_price, base_price*1.02, base_price*0.98, base_price]], 
                          columns=['Date', 'Open', 'High', 'Low', 'Close'])
        st.session_state.price_history[ticker] = df

    df = st.session_state.price_history[ticker]
    last_price = float(df['Close'].iloc[-1])
    
    # 변동성 이벤트 (0.5% 확률로 폭등/폭락)
    event_roll = np.random.random()
    if event_roll < 0.005:
        move = np.random.uniform(0.5, 1.2)
        volatility = move if np.random.random() > 0.4 else -move
        st.toast(f"🚨 {ticker} 익스트림 변동 발생!!", icon="⚠️")
    else:
        volatility = np.random.uniform(-0.005, 0.005)

    new_open = last_price
    new_close = max(last_price * (1 + volatility), 0.1)
    spread = abs(new_open * 0.005)
    new_high = max(new_open, new_close) + spread
    new_low = min(new_open, new_close) - spread
    
    new_row = pd.DataFrame([[now, new_open, new_high, new_low, new_close]], 
                           columns=['Date', 'Open', 'High', 'Low', 'Close'])
    
    df = pd.concat([df, new_row], ignore_index=True).iloc[-40:]
    st.session_state.price_history[ticker] = df
    return df

# --- 4. 메인 화면 ---
st.title("🔥 100종목 실시간 익스트림 거래소")

market = st.sidebar.radio("시장 선택", ["해외 마켓", "국내 마켓"])
stock_dict = st.session_state.US_STOCKS if "해외" in market else st.session_state.KR_STOCKS
ticker = st.sidebar.selectbox("종목 선택", options=list(stock_dict.keys()), 
                             format_func=lambda x: f"{stock_dict[x]} ({x})")

df = get_extreme_price_data(ticker)
curr_p = df['Close'].iloc[-1]
diff = curr_p - df['Close'].iloc[-2]
pct = (diff / df['Close'].iloc[-2]) * 100

# 시세 정보 표시
col_price, col_balance = st.columns([3, 1])
with col_price:
    color = "#ef5350" if diff < 0 else "#26a69a"
    st.markdown(f"### {stock_dict[ticker]} ({ticker})")
    st.markdown(f"<h1 style='color:{color};'>${curr_p:,.2f} ({pct:+.2f}%)</h1>", unsafe_allow_html=True)
with col_balance:
    st.sidebar.metric("💰 가용 잔고", f"${st.session_state.balance:,.2f}")

# 캔들스틱 차트
fig = go.Figure(data=[go.Candlestick(
    x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    increasing_line_color='#26a69a', increasing_fillcolor='#26a69a',
    decreasing_line_color='#ef5350', decreasing_fillcolor='#ef5350'
)])
fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# --- 5. 매수 / 매도 섹션 (추가 및 보강) ---
st.divider()
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    qty = st.number_input("거래 수량 설정", min_value=1, value=1, step=1)
    total_cost = qty * curr_p
    st.caption(f"예상 거래 금액: ${total_cost:,.2f}")

with c2:
    if st.button("🔴 즉시 매수", use_container_width=True):
        if st.session_state.balance >= total_cost:
            st.session_state.balance -= total_cost
            p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
            p['평단가'] = ((p['평단가'] * p['수량']) + total_cost) / (p['수량'] + qty)
            p['수량'] += qty
            st.session_state.portfolio[ticker] = p
            st.success(f"{ticker} {qty}주 매수 완료!")
            st.rerun()
        else:
            st.error("잔고가 부족합니다.")

with c3:
    # 보유 중인 주식 정보 확인
    user_holdings = st.session_state.portfolio.get(ticker, {'수량': 0})['수량']
    st.write(f"현재 보유: **{user_holdings}주**")
    
    if st.button("🔵 보유 전량 매도", use_container_width=True):
        if user_holdings > 0:
            sale_proceeds = user_holdings * curr_p
            st.session_state.balance += sale_proceeds
            st.session_state.portfolio[ticker]['수량'] = 0
            st.session_state.portfolio[ticker]['평단가'] = 0
            st.warning(f"{ticker} 전량 매도 완료! (+${sale_proceeds:,.2f})")
            st.rerun()
        else:
            st.error("매도할 주식이 없습니다.")

# --- 6. 포트폴리오 현황 ---
st.subheader("📋 실시간 나의 투자 현황")
rows = []
for t, info in st.session_state.portfolio.items():
    if info['수량'] > 0:
        live_p = st.session_state.price_history[t]['Close'].iloc[-1]
        profit_rate = ((live_p / info['평단가']) - 1) * 100
        rows.append({
            "종목명": st.session_state.US_STOCKS.get(t, st.session_state.KR_STOCKS.get(t, t)),
            "보유수량": info['수량'],
            "평균단가": f"${info['평단가']:,.2f}",
            "현재가": f"${live_p:,.2f}",
            "수익률": f"{profit_rate:+.2f}%"
        })

if rows:
    st.table(pd.DataFrame(rows))
else:
    st.caption("현재 보유 중인 주식이 없습니다. 마켓에서 종목을 골라 매수해보세요!")
