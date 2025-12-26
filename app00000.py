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

st.set_page_config(page_title="익스트림 글로벌 거래소 v9", layout="wide")
st_autorefresh(interval=1000, key="global_v9_sync")

# --- 1. [핵심] 전역 데이터 동기화 (서버 공유 데이터) ---
# 모든 사용자가 이 객체를 공유하여 시세가 동일하게 유지됩니다.
if 'global_init' not in st.session_state:
    st.session_state.all_tickers = [f"US_STOCK_{i:02d}" for i in range(1, 51)] + [f"KR_STOCK_{i:02d}" for i in range(1, 51)]
    st.session_state.delisted = set()
    # 시작 가격을 넉넉하게 설정
    st.session_state.prices = {t: 1000.0 if "US" in t else 200000.0 for t in st.session_state.all_tickers}
    st.session_state.history = {t: [st.session_state.prices[t]] * 30 for t in st.session_state.all_tickers}
    st.session_state.last_sync = datetime.now()
    # 전역 랭킹용 데이터 (실제 서비스 시 DB 연동 필요, 여기서는 세션 간 유사 공유 시뮬레이션)
    st.session_state.global_rankings = {} 
    st.session_state.global_init = True

# 개인 세션 변수
if 'user_id' not in st.session_state: st.session_state.user_id = f"User_{np.random.randint(1000, 9999)}"
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'is_blackmarket' not in st.session_state: st.session_state.is_blackmarket = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- 2. 통합 엔진 (상폐 방어 + 전역 동기화) ---
def sync_engine():
    now = datetime.now()
    diff = int((now - st.session_state.last_sync).total_seconds())
    if diff < 1: return

    for t in st.session_state.all_tickers:
        if t in st.session_state.delisted: continue
        
        # 암시장 50번 종목 특수성 유지
        if t == "US_STOCK_50" and not st.session_state.is_blackmarket: continue 
        
        curr_p = st.session_state.prices[t]
        for _ in range(min(diff, 5)):
            vol = np.random.uniform(-0.15, 0.15) # 변동폭을 약간 줄여 안정성 확보
            if now.second % 30 == 0:
                vol = np.random.uniform(0.5, 1.2) * (1 if np.random.random() > 0.5 else -1)
            
            # [상폐 방어 핵심] 하한선 근접 시 강제 반등
            floor = 10.0 if "US" in t else 1000.0
            if curr_p < floor:
                vol = abs(vol) + 0.1 # 무조건 상승
            
            # US_50 필승 로직
            if t == "US_STOCK_50": vol = abs(vol) if vol != 0 else 0.05
            
            curr_p *= (1 + vol)
            
            # 상장 폐지 기준을 극단적으로 낮춤
            if curr_p <= 0.5 and t != "US_STOCK_50":
                st.session_state.delisted.add(t)
                break

        st.session_state.prices[t] = max(curr_p, 0.5)
        st.session_state.history[t].append(st.session_state.prices[t])
        st.session_state.history[t] = st.session_state.history[t][-50:]

    # 랭킹 데이터 갱신 (내 자산 가치 계산)
    total_asset = st.session_state.balance
    for t, info in st.session_state.portfolio.items():
        total_asset += info['수량'] * st.session_state.prices[t]
    st.session_state.global_rankings[st.session_state.user_id] = total_asset

    st.session_state.last_sync = now

sync_engine()

# --- 3. UI 구성 (상단 버튼 및 사이드바) ---
top_l, top_c, top_r = st.columns([6, 2, 2])
with top_c:
    if not st.session_state.is_blackmarket:
        if st.button("🌑 암시장 들어가기", use_container_width=True): st.session_state.show_black_pw = True
    else:
        if st.button("🚪 암시장 나가기", use_container_width=True, type="primary"): 
            st.session_state.is_blackmarket = False
            st.rerun()
with top_r:
    if not st.session_state.is_admin:
        if st.button("🛠️ 제작자 창", use_container_width=True): st.session_state.show_admin_pw = True
    else:
        if st.button("🔒 모드 종료", use_container_width=True, type="secondary"): 
            st.session_state.is_admin = False
            st.rerun()

# 비밀번호 로직 (암시장: 0328, 제작자: 1908441199470328)
if st.session_state.get('show_black_pw'):
    if st.text_input("암시장 PW", type="password") == "0328":
        st.session_state.is_blackmarket = True
        st.session_state.show_black_pw = False
        st.rerun()
if st.session_state.get('show_admin_pw'):
    if st.text_input("제작자 PW", type="password") == "1908441199470328":
        st.session_state.is_admin = True
        st.session_state.show_admin_pw = False
        st.rerun()

# --- 4. 랭킹 보드 (사이드바) ---
st.sidebar.title("🏆 글로벌 랭킹")
rank_df = pd.DataFrame([{"Player": k, "Asset": v} for k, v in st.session_state.global_rankings.items()])
if not rank_df.empty:
    rank_df = rank_df.sort_values(by="Asset", ascending=False).head(5)
    st.sidebar.table(rank_df.assign(Asset=rank_df['Asset'].apply(lambda x: f"${x:,.0f}")))
st.sidebar.divider()
st.sidebar.subheader(f"내 ID: {st.session_state.user_id}")
st.sidebar.metric("총 자산", f"${st.session_state.global_rankings[st.session_state.user_id]:,.2f}")

# --- 5. 제작자 관리 패널 ---
if st.session_state.is_admin:
    with st.expander("🛠️ ADMIN CONTROL PANEL", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📉 전 종목 90% 하락"):
                for t in st.session_state.prices: st.session_state.prices[t] *= 0.1
        with c2:
            if st.button("📈 전 종목 200% 상승"):
                for t in st.session_state.prices: st.session_state.prices[t] *= 2.0
        with c3:
            t_target = st.selectbox("조작 종목", st.session_state.all_tickers)
            if st.button("⚡ 즉시 폭등 (+500%)"): st.session_state.prices[t_target] *= 6.0

# --- 6. 메인 거래 화면 ---
ticker = "US_STOCK_50" if st.session_state.is_blackmarket else st.sidebar.selectbox("종목 선택", [t for t in st.session_state.all_tickers if t not in st.session_state.delisted and t != "US_STOCK_50"])

curr_p = st.session_state.prices[ticker]
df_hist = st.session_state.history[ticker]
pct = ((curr_p / df_hist[-2]) - 1) * 100 if len(df_hist) > 1 else 0
color = "#FF4B4B" if pct < 0 else "#00D166"

st.header(f"{ticker} {'🌑' if st.session_state.is_blackmarket else ''}")
st.markdown(f"<h1 style='color:{color};'>${curr_p:,.2f} ({pct:+.2f}%)</h1>", unsafe_allow_html=True)

# 캔들스틱 차트 (원본 유지)
fig = go.Figure(data=[go.Candlestick(x=list(range(len(df_hist))), open=[p*0.99 for p in df_hist], high=[p*1.02 for p in df_hist], low=[p*0.98 for p in df_hist], close=df_hist, increasing_line_color='#00D166', decreasing_line_color='#FF4B4B')])
fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 매수/매도 시스템
c1, c2, c3 = st.columns(3)
with c1: qty = st.number_input("수량", min_value=1, value=1)
with c2:
    if st.button("🔴 BUY", use_container_width=True):
        if st.session_state.balance >= qty * curr_p:
            st.session_state.balance -= qty * curr_p
            p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
            p['평단가'] = ((p['평단가']*p['수량']) + (qty*curr_p)) / (p['수량']+qty)
            p['수량'] += qty
            st.session_state.portfolio[ticker] = p
            st.rerun()
with c3:
    hold = st.session_state.portfolio.get(ticker, {'수량': 0})['수량']
    if st.button(f"🔵 SELL ALL ({hold})", use_container_width=True):
        if hold > 0:
            st.session_state.balance += hold * curr_p
            st.session_state.portfolio[ticker]['수량'] = 0
            st.rerun()
