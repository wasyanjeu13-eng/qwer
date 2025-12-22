import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 라이브러리 체크 및 자동 새로고침
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("requirements.txt에 streamlit-autorefresh를 추가해주세요.")
    st.stop()

st.set_page_config(page_title="실시간 동기화 익스트림 거래소", layout="wide")
# 모든 종목 시세 동기화를 위해 1초마다 새로고침
st_autorefresh(interval=1000, key="global_refresh")

# --- 1. 전 종목 리스트 생성 (해외/국내 총 100개) ---
if 'all_tickers' not in st.session_state:
    us_names = [f"US_Tech_{i:02d}" for i in range(1, 51)]
    kr_names = [f"KR_Stock_{i:02d}" for i in range(1, 51)]
    st.session_state.all_tickers = us_names + kr_names
    st.session_state.ticker_names = {t: t for t in st.session_state.all_tickers}

# --- 2. 세션 상태 초기화 (자산, 가격 내역, 마지막 업데이트 시각) ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'price_history' not in st.session_state: st.session_state.price_history = {}
if 'last_sync_time' not in st.session_state: st.session_state.last_sync_time = datetime.now()

# --- 3. 전 종목 시간 동기화 엔진 ---
def sync_all_markets():
    now = datetime.now()
    # 마지막 업데이트로부터 흐른 시간 계산
    seconds_passed = int((now - st.session_state.last_sync_time).total_seconds())
    
    # 처음 접속 시 60초 분량의 기초 데이터 생성
    if not st.session_state.price_history:
        for t in st.session_state.all_tickers:
            base = 100.0 if "US" in t else 50000.0
            data = []
            curr = base
            for j in range(60):
                d = now - timedelta(seconds=60-j)
                vol = np.random.uniform(-0.20, 0.20)
                op, cl = curr, curr * (1 + vol)
                hi, lo = max(op, cl) * 1.05, min(op, cl) * 0.95
                data.append([d, op, hi, lo, cl])
                curr = cl
            st.session_state.price_history[t] = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close'])
    
    # 부재 중 시간(seconds_passed)만큼 모든 종목에 데이터 추가
    if seconds_passed > 0:
        # 성능을 위해 공백이 너무 길면 최근 300초만 시뮬레이션
        steps = min(seconds_passed, 300)
        
        for t in st.session_state.all_tickers:
            df = st.session_state.price_history[t]
            last_price = df['Close'].iloc[-1]
            
            new_rows = []
            temp_price = last_price
            for i in range(steps):
                vol = np.random.uniform(-0.20, 0.20) # 1초당 최대 20% 변동
                new_open = temp_price
                new_close = max(temp_price * (1 + vol), 0.1)
                new_high = max(new_open, new_close) * 1.05
                new_low = min(new_open, new_close) * 0.95
                sim_time = st.session_state.last_sync_time + timedelta(seconds=i+1)
                
                new_rows.append([sim_time, new_open, new_high, new_low, new_close])
                temp_price = new_close
            
            new_df = pd.DataFrame(new_rows, columns=['Date', 'Open', 'High', 'Low', 'Close'])
            st.session_state.price_history[t] = pd.concat([df, new_df], ignore_index=True).iloc[-60:]
            
        st.session_state.last_sync_time = now

# 동기화 실행
sync_all_markets()

# --- 4. 메인 UI 및 차트 ---
st.title("🌐 전 종목 실시간 동기화 거래소 (±20% 익스트림)")
st.sidebar.metric("💰 내 잔고", f"${st.session_state.balance:,.2f}")

# 마켓 선택 및 종목 선택
m_choice = st.sidebar.radio("마켓", ["해외 (US)", "국내 (KR)"])
filtered_tickers = [t for t in st.session_state.all_tickers if t.startswith("US" if "해외" in m_choice else "KR")]
ticker = st.sidebar.selectbox("종목 선택", filtered_tickers)

df = st.session_state.price_history[ticker]
curr_p = df['Close'].iloc[-1]
prev_p = df['Close'].iloc[-2]
pct = ((curr_p / prev_p) - 1) * 100

# 상단 시세 정보
col1, col2 = st.columns([3, 1])
with col1:
    color = "#ef5350" if curr_p < prev_p else "#26a69a"
    st.markdown(f"## {ticker}")
    st.markdown(f"<h1 style='color:{color};'>${curr_p:,.2f} <small>({pct:+.2f}%)</small></h1>", unsafe_allow_html=True)

# 캔들스틱 차트

fig = go.Figure(data=[go.Candlestick(
    x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
)])
fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(t=0,b=0,l=0,r=0))
st.plotly_chart(fig, use_container_width=True)

# --- 5. 거래 시스템 ---
st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    qty = st.number_input("거래 수량", min_value=1, value=1)
with c2:
    if st.button("🔴 매수", use_container_width=True):
        cost = qty * curr_p
        if st.session_state.balance >= cost:
            st.session_state.balance -= cost
            p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
            p['평단가'] = ((p['평단가'] * p['수량']) + cost) / (p['수량'] + qty)
            p['수량'] += qty
            st.session_state.portfolio[ticker] = p
            st.rerun()
with c3:
    hold = st.session_state.portfolio.get(ticker, {'수량': 0})['수량']
    if st.button(f"🔵 전량 매도 ({hold}주)", use_container_width=True):
        if hold > 0:
            st.session_state.balance += hold * curr_p
            st.session_state.portfolio[ticker]['수량'] = 0
            st.rerun()

# --- 6. 실시간 포트폴리오 ---
st.subheader("📊 나의 투자 현황 (모든 종목 시세 동시 연동)")
pf_data = []
for t, info in st.session_state.portfolio.items():
    if info['수량'] > 0:
        p_now = st.session_state.price_history[t]['Close'].iloc[-1]
        pf_data.append({
            "종목": t, "보유량": info['수량'], 
            "평단가": f"${info['평단가']:,.2f}", "현재가": f"${p_now:,.2f}",
            "수익률": f"{(p_now/info['평단가']-1)*100:+.2f}%"
        })
if pf_data: st.table(pd.DataFrame(pf_data))
else: st.caption("현재 보유 중인 주식이 없습니다.")
