import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("requirements.txt에 streamlit-autorefresh를 추가해주세요.")
    st.stop()

st.set_page_config(page_title="익스트림 동기화 거래소", layout="wide")
st_autorefresh(interval=1000, key="v7_safe_sync")

# --- 1. 상태 초기화 ---
if 'init' not in st.session_state:
    st.session_state.all_tickers = [f"US_STOCK_{i:02d}" for i in range(1, 51)] + [f"KR_STOCK_{i:02d}" for i in range(1, 51)]
    st.session_state.delisted = set()
    st.session_state.balance = 100000.0
    st.session_state.portfolio = {}
    st.session_state.price_history = {}
    
    now = datetime.now()
    for t in st.session_state.all_tickers:
        # 시작가를 더 높게 설정하여 생존력 강화
        base = 500.0 if "US" in t else 100000.0
        data = [[now - timedelta(seconds=20-i), base, base*1.05, base*0.95, base] for i in range(20)]
        st.session_state.price_history[t] = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close'])
    
    st.session_state.last_sync = now
    st.session_state.init = True

# --- 2. 동기화 엔진 (상장 폐지 방어 로직 추가) ---
def sync_engine():
    now = datetime.now()
    diff = int((now - st.session_state.last_sync).total_seconds())
    if diff < 1: return

    steps = min(diff, 60)
    
    for t in st.session_state.all_tickers:
        if t in st.session_state.delisted: continue
        
        df = st.session_state.price_history[t]
        curr_p = df['Close'].iloc[-1]
        
        new_rows = []
        for i in range(steps):
            sim_time = st.session_state.last_sync + timedelta(seconds=i+1)
            
            # [기본 변동] ±20%
            vol = np.random.uniform(-0.20, 0.20)
            
            # [30초 쇼크] ±150%
            if sim_time.second % 30 == 0:
                vol = np.random.uniform(0.5, 1.5) * (1 if np.random.random() > 0.5 else -1)
            
            # [보정 로직] 가격이 너무 낮아지면(상폐 위기) 상승 확률 대폭 증가 (저가 매수세)
            safety_limit = 10.0 if "US" in t else 2000.0
            if curr_p < safety_limit:
                vol = abs(vol) * 1.5 # 하락을 상승으로 반전시키고 폭을 키움
            
            # [US_50 필승] 무조건 상승
            if t == "US_STOCK_50":
                vol = abs(vol) if vol != 0 else 0.1
            
            new_o = curr_p
            new_c = curr_p * (1 + vol)
            
            # [상장 폐지 기준 하향] 더 극한까지 버티게 수정
            delist_limit = 1.0 if "US" in t else 100.0
            if new_c <= delist_limit and t != "US_STOCK_50":
                st.session_state.delisted.add(t)
                if t in st.session_state.portfolio:
                    st.session_state.portfolio[t]['수량'] = 0
                break
            
            new_h = max(new_o, new_c) * 1.05
            new_l = min(new_o, new_c) * 0.95
            new_rows.append([sim_time, new_o, new_h, new_l, new_c])
            curr_p = new_c
            
        if new_rows:
            new_df = pd.DataFrame(new_rows, columns=['Date', 'Open', 'High', 'Low', 'Close'])
            st.session_state.price_history[t] = pd.concat([df, new_df], ignore_index=True).iloc[-50:]
            
    st.session_state.last_sync = now

sync_engine()

# --- 3. 메인 UI ---
st.sidebar.title("💰 WALLET")
st.sidebar.header(f"${st.session_state.balance:,.2f}")

m_choice = st.sidebar.radio("MARKET", ["해외 (US)", "국내 (KR)"])
prefix = "US" if "해외" in m_choice else "KR"
active_options = [t for t in st.session_state.all_tickers if t.startswith(prefix) and t not in st.session_state.delisted]

if not active_options:
    if st.sidebar.button("🚨 시장 초기화 (모든 종목 재상장)"):
        del st.session_state.init
        st.rerun()
    st.error("시장 붕괴: 모든 종목이 상장 폐지되었습니다.")
else:
    ticker = st.sidebar.selectbox("종목 선택", active_options)
    df = st.session_state.price_history[ticker]
    
    curr_p = df['Close'].iloc[-1]
    prev_p = df['Close'].iloc[-2]
    pct = ((curr_p / prev_p) - 1) * 100
    
    col_l, col_r = st.columns([3, 1])
    with col_l:
        color = "#FF4B4B" if curr_p < prev_p else "#00D166"
        st.title(f"{ticker} {'🔥' if ticker == 'US_STOCK_50' else ''}")
        st.markdown(f"<h1 style='color:{color};'>${curr_p:,.2f} ({pct:+.2f}%)</h1>", unsafe_allow_html=True)
    with col_r:
        st.metric("30초 쇼크까지", f"{30 - (datetime.now().second % 30)}초")

    # 캔들스틱 차트 (원본 유지)
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#00D166', decreasing_line_color='#FF4B4B',
        increasing_fillcolor='#00D166', decreasing_fillcolor='#FF4B4B'
    )])
    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(t=0,b=0,l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)

    # 거래 섹션
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: qty = st.number_input("거래 수량", min_value=1, value=1, step=1)
    with c2:
        if st.button("🔴 매수", use_container_width=True):
            if st.session_state.balance >= qty * curr_p:
                st.session_state.balance -= qty * curr_p
                p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
                p['평단가'] = ((p['평단가']*p['수량']) + (qty*curr_p)) / (p['수량']+qty)
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

# 포트폴리오 및 폐지 현황
st.subheader("📋 실시간 포트폴리오")
pf_rows = [{"종목": t, "보유량": i['수량'], "수익률": f"{(st.session_state.price_history[t]['Close'].iloc[-1]/i['평단가']-1)*100:+.2f}%"} for t, i in st.session_state.portfolio.items() if i['수량'] > 0]
if pf_rows: st.table(pd.DataFrame(pf_rows))

if st.session_state.delisted:
    st.sidebar.divider()
    st.sidebar.error(f"🚨 상장 폐지됨: {len(st.session_state.delisted)}개")
