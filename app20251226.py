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

st.set_page_config(page_title="익스트림 30초 쇼크 거래소", layout="wide")
# 전 종목 실시간 동기화를 위해 1초마다 새로고침
st_autorefresh(interval=1000, key="global_extreme_sync")

# --- 1. 전 종목 리스트 생성 (총 100개) ---
if 'all_tickers' not in st.session_state:
    us_names = [f"US_STOCK_{i:02d}" for i in range(1, 51)]
    kr_names = [f"KR_STOCK_{i:02d}" for i in range(1, 51)]
    st.session_state.all_tickers = us_names + kr_names

# --- 2. 세션 상태 초기화 ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'price_history' not in st.session_state: st.session_state.price_history = {}
if 'last_sync_time' not in st.session_state: st.session_state.last_sync_time = datetime.now()

# --- 3. 전 종목 동시 변동 엔진 (30초 거대 폭 포함) ---
def sync_all_markets_extreme():
    now = datetime.now()
    seconds_passed = int((now - st.session_state.last_sync_time).total_seconds())
    
    # 초기 데이터 생성 (최초 접속 시)
    if not st.session_state.price_history:
        for t in st.session_state.all_tickers:
            base = 100.0 if "US" in t else 50000.0
            st.session_state.price_history[t] = pd.DataFrame(
                [[now - timedelta(seconds=1), base, base*1.2, base*0.8, base]],
                columns=['Date', 'Open', 'High', 'Low', 'Close']
            )

    # 부재 중 시간만큼 모든 종목에 동일하게 시세 생성
    if seconds_passed > 0:
        steps = min(seconds_passed, 180) # 과부하 방지 (최대 180초 시뮬레이션)
        
        for t in st.session_state.all_tickers:
            df = st.session_state.price_history[t]
            
            for i in range(steps):
                last_price = df['Close'].iloc[-1]
                sim_time = st.session_state.last_sync_time + timedelta(seconds=i+1)
                
                # --- 변동 로직 ---
                # 1) 기본 1초 변동: 최대 ±20%
                volatility = np.random.uniform(-0.20, 0.20)
                
                # 2) 30초 단위 거대 폭 변동 (매 30초, 00초 지점)
                # 시뮬레이션되는 시간의 초가 0 또는 30일 때 대폭등/폭락 발생
                if sim_time.second % 30 == 0:
                    extreme_shock = np.random.uniform(0.5, 1.5) # 50% ~ 150% 변동
                    direction = 1 if np.random.random() > 0.5 else -1
                    volatility = extreme_shock * direction
                    if t == st.session_state.get('current_ticker'): # 현재 보고 있는 종목만 토스트 알림
                        st.toast(f"🚨 {sim_time.second}초 주기 시장 대충격 발생!!", icon="💥")

                new_open = last_price
                new_close = max(last_price * (1 + volatility), 0.1)
                
                # 캔들 시각화 데이터 계산
                spread = abs(new_open * 0.1)
                new_high = max(new_open, new_close) + spread
                new_low = min(new_open, new_close) - spread
                
                new_row = pd.DataFrame([[sim_time, new_open, new_high, new_low, new_close]], 
                                       columns=['Date', 'Open', 'High', 'Low', 'Close'])
                df = pd.concat([df, new_row], ignore_index=True).iloc[-60:]
            
            st.session_state.price_history[t] = df
            
        st.session_state.last_sync_time = now

# 동기화 실행
sync_all_markets_extreme()

# --- 4. UI 레이아웃 ---
st.title("🎢 30초 쇼크: 전 종목 동기화 거래소")
st.sidebar.subheader(f"💰 잔고: ${st.session_state.balance:,.2f}")

# 종목 선택
m_choice = st.sidebar.radio("마켓 선택", ["해외 (US)", "국내 (KR)"])
prefix = "US" if "해외" in m_choice else "KR"
filtered_list = [t for t in st.session_state.all_tickers if t.startswith(prefix)]
ticker = st.sidebar.selectbox("종목 선택", filtered_list)
st.session_state.current_ticker = ticker # 알림용 세션 저장

# 데이터 로드 및 시세 표시
df = st.session_state.price_history[ticker]
curr_p = df['Close'].iloc[-1]
prev_p = df['Close'].iloc[-2]
pct = ((curr_p / prev_p) - 1) * 100

col_info, col_timer = st.columns([3, 1])
with col_info:
    color = "#ef5350" if curr_p < prev_p else "#26a69a"
    st.markdown(f"## {ticker}")
    st.markdown(f"<h1 style='color:{color};'>${curr_p:,.2f} ({pct:+.2f}%)</h1>", unsafe_allow_html=True)
with col_timer:
    next_shock = 30 - (datetime.now().second % 30)
    st.metric("다음 대충격까지", f"{next_shock}초")

# 캔들스틱 차트
fig = go.Figure(data=[go.Candlestick(
    x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
)])
fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(t=0,b=0,l=0,r=0))
st.plotly_chart(fig, use_container_width=True)

# --- 5. 거래 섹션 ---
st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    qty = st.number_input("거래 수량", min_value=1, value=1)
with c2:
    if st.button("🔴 즉시 매수", use_container_width=True):
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

# --- 6. 포트폴리오 ---
st.subheader("📋 실시간 포트폴리오 (전 종목 동시 시뮬레이션 중)")
pf_rows = []
for t, info in st.session_state.portfolio.items():
    if info['수량'] > 0:
        p_now = st.session_state.price_history[t]['Close'].iloc[-1]
        pf_rows.append({
            "종목": t, "보유량": info['수량'], 
            "평단가": f"${info['평단가']:,.2f}", "현재가": f"${p_now:,.2f}",
            "수익률": f"{(p_now/info['평단가']-1)*100:+.2f}%"
        })
if pf_rows: st.table(pd.DataFrame(pf_rows))
else: st.caption("보유 자산이 없습니다. 30초 쇼크가 오기 전에 매수해보세요!")
