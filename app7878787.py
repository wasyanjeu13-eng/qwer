import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 필수 라이브러리 체크
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("requirements.txt에 streamlit-autorefresh를 추가해주세요.")
    st.stop()

st.set_page_config(page_title="익스트림 글로벌 거래소", layout="wide")
st_autorefresh(interval=1000, key="global_universal_sync_v8")

# --- 1. 전역 데이터 동기화 (서버 공통 데이터) ---
if 'global_init' not in st.session_state:
    st.session_state.all_tickers = [f"US_STOCK_{i:02d}" for i in range(1, 51)] + [f"KR_STOCK_{i:02d}" for i in range(1, 51)]
    st.session_state.delisted = set()
    st.session_state.prices = {t: 500.0 if "US" in t else 100000.0 for t in st.session_state.all_tickers}
    st.session_state.history = {t: [st.session_state.prices[t]] * 30 for t in st.session_state.all_tickers}
    st.session_state.last_sync = datetime.now()
    st.session_state.global_init = True

# 개인 세션 변수
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'is_blackmarket' not in st.session_state: st.session_state.is_blackmarket = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- 2. 통합 변동 엔진 ---
def sync_engine():
    now = datetime.now()
    diff = int((now - st.session_state.last_sync).total_seconds())
    if diff < 1: return

    for t in st.session_state.all_tickers:
        if t in st.session_state.delisted: continue
        
        # 암시장 종목(50번)은 암시장 입장 시에만 변동
        if t == "US_STOCK_50" and not st.session_state.is_blackmarket: continue 
        
        curr_p = st.session_state.prices[t]
        for _ in range(min(diff, 5)):
            vol = np.random.uniform(-0.20, 0.20)
            if now.second % 30 == 0:
                vol = np.random.uniform(0.5, 1.5) * (1 if np.random.random() > 0.5 else -1)
            
            if t == "US_STOCK_50": # 암시장 50번 필승 로직
                vol = abs(vol) if vol != 0 else 0.1
            
            curr_p *= (1 + vol)
            
            # 상장 폐지 기준 (제작자 예외 없음)
            if curr_p <= (1.0 if "US" in t else 500.0) and t != "US_STOCK_50":
                st.session_state.delisted.add(t)
                break

        st.session_state.prices[t] = max(curr_p, 0.1)
        st.session_state.history[t].append(st.session_state.prices[t])
        st.session_state.history[t] = st.session_state.history[t][-50:]

    st.session_state.last_sync = now

sync_engine()

# --- 3. UI 상단 레이아웃 (암시장 & 제작자 전용) ---
top_l, top_c, top_r = st.columns([6, 2, 2])

with top_c:
    if not st.session_state.is_blackmarket:
        if st.button("🌑 암시장 들어가기", use_container_width=True):
            st.session_state.show_black_pw = True
    else:
        if st.button("🚪 암시장 나가기", use_container_width=True, type="primary"):
            st.session_state.is_blackmarket = False
            st.rerun()

with top_r:
    if not st.session_state.is_admin:
        if st.button("🛠️ 제작자 전용 창", use_container_width=True):
            st.session_state.show_admin_pw = True
    else:
        if st.button("🔒 제작자 모드 종료", use_container_width=True, type="secondary"):
            st.session_state.is_admin = False
            st.rerun()

# 비밀번호 입력창들
if st.session_state.get('show_black_pw'):
    pw_b = st.text_input("암시장 번호 (0328)", type="password", key="pw_b")
    if pw_b == "0328":
        st.session_state.is_blackmarket = True
        st.session_state.show_black_pw = False
        st.rerun()

if st.session_state.get('show_admin_pw'):
    pw_a = st.text_input("제작자 비밀번호 입력", type="password", key="pw_a")
    if pw_a == "1908441199470328":
        st.session_state.is_admin = True
        st.session_state.show_admin_pw = False
        st.rerun()

# --- 4. 제작자 전용 관리 패널 (모든 유저에게 실시간 반영) ---
if st.session_state.is_admin:
    with st.container(border=True):
        st.subheader("🛠️ 제작자 마스터 컨트롤 패널")
        a1, a2, a3 = st.columns(3)
        with a1:
            if st.button("📉 전 종목 강제 하락 (90% 폭락)"):
                for t in st.session_state.prices:
                    if t != "US_STOCK_50": st.session_state.prices[t] *= 0.1
                st.toast("시장 대재앙 발생!")
        with a2:
            if st.button("📈 전 종목 강제 상승 (200% 폭등)"):
                for t in st.session_state.prices:
                    st.session_state.prices[t] *= 2.0
                st.toast("전 종목 골드러시!")
        with a3:
            reset_target = st.selectbox("종목 선택", st.session_state.all_tickers, key="reset_box")
            if st.button(f"🚨 {reset_target} 즉시 상장폐지"):
                st.session_state.delisted.add(reset_target)
        
        b1, b2 = st.columns(2)
        with b1:
            target_t = st.selectbox("개별 조작 종목", st.session_state.all_tickers)
        with b2:
            amt = st.slider("조작 강도 (%)", -99, 500, 50)
            if st.button(f"⚡ {target_t} 가격 즉시 반영"):
                st.session_state.prices[target_t] *= (1 + amt/100)
    st.divider()

# --- 5. 메인 화면 구성 ---
if st.session_state.is_blackmarket:
    st.markdown("### 🌑 DARK MARKET")
    ticker = "US_STOCK_50"
else:
    st.title("🎢 글로벌 익스트림 실시간 거래소")
    m_choice = st.sidebar.radio("마켓", ["US Market", "KR Market"])
    prefix = "US" if "US" in m_choice else "KR"
    active_options = [t for t in st.session_state.all_tickers if t.startswith(prefix) and t not in st.session_state.delisted and t != "US_STOCK_50"]
    if active_options:
        ticker = st.sidebar.selectbox("종목 선택", active_options)
    else:
        st.error("마켓이 마비되었습니다.")
        st.stop()

# 시세 차트 표시
df_hist = st.session_state.history[ticker]
curr_p = st.session_state.prices[ticker]
pct = ((curr_p / df_hist[-2]) - 1) * 100 if len(df_hist) > 1 else 0
color = "#FF4B4B" if pct < 0 else "#00D166"

st.header(f"{ticker} {'(암시장)' if st.session_state.is_blackmarket else ''}")
st.markdown(f"<h1 style='color:{color};'>${curr_p:,.2f} ({pct:+.2f}%)</h1>", unsafe_allow_html=True)

fig = go.Figure(data=[go.Candlestick(
    x=list(range(len(df_hist))),
    open=[p*0.99 for p in df_hist], high=[p*1.05 for p in df_hist],
    low=[p*0.95 for p in df_hist], close=df_hist,
    increasing_line_color='#00D166', decreasing_line_color='#FF4B4B'
)])
fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 개인 거래 시스템
st.sidebar.divider()
st.sidebar.metric("나의 잔고", f"${st.session_state.balance:,.2f}")
qty = st.sidebar.number_input("거래 수량", min_value=1, value=1)
if st.sidebar.button("🔴 매수", use_container_width=True):
    if st.session_state.balance >= qty * curr_p:
        st.session_state.balance -= qty * curr_p
        p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
        p['평단가'] = ((p['평단가']*p['수량']) + (qty*curr_p)) / (p['수량']+qty)
        p['수량'] += qty
        st.session_state.portfolio[ticker] = p
        st.rerun()

hold = st.session_state.portfolio.get(ticker, {'수량': 0})['수량']
if st.sidebar.button(f"🔵 매도 ({hold}주)", use_container_width=True):
    if hold > 0:
        st.session_state.balance += hold * curr_p
        st.session_state.portfolio[ticker]['수량'] = 0
        st.rerun()
