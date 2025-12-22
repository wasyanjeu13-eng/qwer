import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 페이지 설정
st.set_page_config(page_title="익스트림 가상 거래소", layout="wide")

# 1초마다 자동 새로고침
st_autorefresh(interval=1000, key="datarefresh")

# --- 종목 리스트 ---
US_STOCKS = {f"US_{i:02d}": f"Global Tech {i}" for i in range(1, 26)}
KR_STOCKS = {f"KR_{i:02d}": f"국내 우량주 {i}" for i in range(1, 26)}

if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'price_history' not in st.session_state: st.session_state.price_history = {}

def get_live_price_data(ticker):
    now = datetime.now()
    
    if ticker not in st.session_state.price_history:
        base_price = 100.0 if "US" in ticker else 50000.0
        df = pd.DataFrame([[now - timedelta(seconds=1), base_price, base_price*1.01, base_price*0.99, base_price]], 
                          columns=['Date', 'Open', 'High', 'Low', 'Close'])
        st.session_state.price_history[ticker] = df

    df = st.session_state.price_history[ticker]
    last_price = float(df['Close'].iloc[-1])
    
    # --- 핵심: 변동 로직 ---
    # 1. 평소에는 1초마다 잔잔한 변동 (±0.1% ~ 0.5%)
    volatility = np.random.uniform(-0.005, 0.005)
    
    # 2. 아주 희박한 확률(약 0.5%)로 잭팟 또는 폭락 발생 (최대 120%)
    # 1초마다 체크하므로 실제로는 "가끔" 발생하게 됨
    event_roll = np.random.random()
    if event_roll < 0.005: # 0.5% 확률
        event_type = np.random.choice(['BOOM', 'CRASH'])
        extreme_move = np.random.uniform(0.5, 1.2) # 50% ~ 120% 변동
        if event_type == 'BOOM':
            volatility = extreme_move
            st.toast(f"🚀 {ticker} 호재 발생! 폭등 중!")
        else:
            volatility = -extreme_move
            st.toast(f"📉 {ticker} 악재 발생! 투매 주의!")

    new_open = last_price
    new_close = max(last_price * (1 + volatility), 0.01) # 가격이 0원 이하로 내려가지 않게 방어
    new_high = max(new_open, new_close) * (1 + np.random.uniform(0, 0.01))
    new_low = min(new_open, new_close) * (1 - np.random.uniform(0, 0.01))
    
    new_row = pd.DataFrame([[now, new_open, new_high, new_low, new_close]], 
                           columns=['Date', 'Open', 'High', 'Low', 'Close'])
    
    df = pd.concat([df, new_row], ignore_index=True).iloc[-50:] # 최신 50개 캔들 유지
    st.session_state.price_history[ticker] = df
    return df

# --- 메인 화면 구성 (중략 - 이전 코드와 동일) ---
st.title("⚡ 익스트림 실시간 가상 거래소 (High Volatility)")

market = st.sidebar.radio("시장 선택", ["해외", "국내"])
stock_dict = US_STOCKS if market == "해외" else KR_STOCKS
ticker = st.sidebar.selectbox("종목 선택", options=list(stock_dict.keys()), format_func=lambda x: f"{stock_dict[x]} ({x})")

df = get_live_price_data(ticker)
curr_p = df['Close'].iloc[-1]
prev_p = df['Close'].iloc[-2]
diff = curr_p - prev_p
pct = (diff / prev_p) * 100

color = "#ef5350" if diff < 0 else "#26a69a"
st.markdown(f"<h1 style='color:{color};'>{ticker} 현재가: ${curr_p:,.2f} ({pct:+.2f}%)</h1>", unsafe_allow_html=True)

# 캔들스틱 차트 출력

fig = go.Figure(data=[go.Candlestick(
    x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
)])
fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 매수/매도 버튼 및 포트폴리오 (이전 코드와 동일하게 유지)
st.divider()
c1, c2 = st.columns(2)
with c1:
    qty = st.number_input("수량", min_value=1, value=1)
    if st.button("🔴 매수", use_container_width=True):
        cost = qty * curr_p
        if st.session_state.balance >= cost:
            st.session_state.balance -= cost
            p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
            new_qty = p['수량'] + qty
            p['평단가'] = ((p['평단가'] * p['수량']) + cost) / new_qty
            p['수량'] = new_qty
            st.session_state.portfolio[ticker] = p
            st.rerun()
with c2:
    st.write(f"결제 예정: ${qty * curr_p:,.2f}")
    if st.button("🔵 전량 매도", use_container_width=True):
        p = st.session_state.portfolio.get(ticker, {'수량': 0})
        if p['수량'] > 0:
            st.session_state.balance += p['수량'] * curr_p
            p['수량'] = 0
            st.session_state.portfolio[ticker] = p
            st.rerun()

# 실시간 포트폴리오 현황
st.subheader("📋 내 투자 현황 (1초 업데이트)")
rows = []
for t, info in st.session_state.portfolio.items():
    if info['수량'] > 0:
        live_p = st.session_state.price_history[t]['Close'].iloc[-1]
        profit_rate = ((live_p / info['평단가']) - 1) * 100
        rows.append({"종목": t, "수량": info['수량'], "평단가": f"${info['평단가']:,.2f}", "현재가": f"${live_p:,.2f}", "수익률": f"{profit_rate:+.2f}%"})
if rows: st.table(pd.DataFrame(rows))
