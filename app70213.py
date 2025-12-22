import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 에러 방지: 라이브러리 설치 여부 체크 및 호출
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("라이브러리 설치 중입니다. 잠시만 기다려주시거나 Reboot 해주세요. (요구사항: streamlit-autorefresh)")
    st.stop()

# 페이지 설정
st.set_page_config(page_title="익스트림 가상 거래소", layout="wide")

# 1초마다 자동 새로고침
st_autorefresh(interval=1000, key="datarefresh")

# --- 종목 리스트 ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'price_history' not in st.session_state: st.session_state.price_history = {}

def get_live_price_data(ticker):
    now = datetime.now()
    if ticker not in st.session_state.price_history:
        base_price = 100.0
        df = pd.DataFrame([[now - timedelta(seconds=1), base_price, base_price*1.01, base_price*0.99, base_price]], 
                          columns=['Date', 'Open', 'High', 'Low', 'Close'])
        st.session_state.price_history[ticker] = df

    df = st.session_state.price_history[ticker]
    last_price = float(df['Close'].iloc[-1])
    
    # --- 변동 로직 (0.5% 확률로 최대 120% 변동) ---
    volatility = np.random.uniform(-0.005, 0.005) # 평소 잔잔한 변동
    
    event_roll = np.random.random()
    if event_roll < 0.005: # 0.5%의 확률로 대폭등/폭락
        extreme_move = np.random.uniform(0.5, 1.2)
        if np.random.random() > 0.5:
            volatility = extreme_move
            st.toast("🚀🚀 폭등 발생! 가즈아!")
        else:
            volatility = -extreme_move
            st.toast("📉📉 폭락 발생! 탈출하세요!")

    new_open = last_price
    new_close = max(last_price * (1 + volatility), 0.01)
    new_high = max(new_open, new_close) * (1 + np.random.uniform(0, 0.005))
    new_low = min(new_open, new_close) * (1 - np.random.uniform(0, 0.005))
    
    new_row = pd.DataFrame([[now, new_open, new_high, new_low, new_close]], columns=['Date', 'Open', 'High', 'Low', 'Close'])
    df = pd.concat([df, new_row], ignore_index=True).iloc[-40:]
    st.session_state.price_history[ticker] = df
    return df

# --- 메인 화면 ---
st.title("⚡ 실시간 익스트림 거래소")
ticker = st.sidebar.selectbox("종목 선택", ["X-COIN", "DOGE-STYLE", "TO-THE-MOON"])

df = get_live_price_data(ticker)
curr_p = df['Close'].iloc[-1]
diff = curr_p - df['Close'].iloc[-2]

color = "#ef5350" if diff < 0 else "#26a69a"
st.markdown(f"<h1 style='color:{color};'>{ticker}: ${curr_p:,.2f} ({diff/df['Close'].iloc[-2]*100:+.2f}%)</h1>", unsafe_allow_html=True)

# 차트 출력
fig = go.Figure(data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450)
st.plotly_chart(fig, use_container_width=True)

# 잔고 및 매수/매도
st.sidebar.metric("내 잔고", f"${st.session_state.balance:,.2f}")
qty = st.number_input("수량", min_value=1, value=1)
if st.button("🔴 매수", use_container_width=True):
    if st.session_state.balance >= qty * curr_p:
        st.session_state.balance -= qty * curr_p
        p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
        p['평단가'] = ((p['평단가'] * p['수량']) + (qty * curr_p)) / (p['수량'] + qty)
        p['수량'] += qty
        st.session_state.portfolio[ticker] = p
        st.rerun()

# 포트폴리오
st.subheader("📋 실시간 수익 현황")
if ticker in st.session_state.portfolio and st.session_state.portfolio[ticker]['수량'] > 0:
    p = st.session_state.portfolio[ticker]
    profit_rate = (curr_p / p['평단가'] - 1) * 100
    st.write(f"보유: {p['수량']}주 | 평단가: ${p['평단가']:,.2f} | **현재 수익률: {profit_rate:+.2f}%**")
