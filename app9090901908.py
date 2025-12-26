import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 필수 라이브러리 (pip install streamlit-autorefresh)
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("requirements.txt에 streamlit-autorefresh를 추가해주세요.")
    st.stop()

st.set_page_config(page_title="익스트림 실시간 서버 연동소", layout="wide")
st_autorefresh(interval=1000, key="true_global_sync_v10")

# --- 1. 전역 서버 데이터 (모든 유저 공유) ---
@st.cache_resource
def init_global_server():
    tickers = [f"US_STOCK_{i:02d}" for i in range(1, 51)] + [f"KR_STOCK_{i:02d}" for i in range(1, 51)]
    return {
        "prices": {t: 1000.0 if "US" in t else 200000.0 for t in tickers},
        "history": {t: [1000.0 if "US" in t else 200000.0] * 30 for t in tickers},
        "delisted": set(),
        "rankings": {}, # {user_id: total_asset}
        "last_sync": datetime.now()
    }

server = init_global_server()

# --- 2. 개인 세션 데이터 ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"Rider_{np.random.randint(1000, 9999)}"
    st.session_state.balance = 100000.0
    st.session_state.portfolio = {}
if 'is_blackmarket' not in st.session_state: st.session_state.is_blackmarket = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- 3. 서버 시세 동기화 엔진 ---
def update_server_engine():
    now = datetime.now()
    diff = int((now - server['last_sync']).total_seconds())
    if diff < 1: return

    for t in server['prices'].keys():
        if t in server['delisted']: continue
        
        # 암시장 종목(50번) 변동 조건 (암시장 활성화 시 더 크게 변동)
        curr_p = server['prices'][t]
        
        for _ in range(min(diff, 10)):
            vol = np.random.uniform(-0.15, 0.15)
            # 30초 대충격
            if now.second % 30 == 0:
                vol = np.random.uniform(0.6, 1.3) * (1 if np.random.random() > 0.5 else -1)
            
            # [상폐 절대 방어] 가격이 바닥권이면 무조건 급반등
            floor = 5.0 if "US" in t else 500.0
            if curr_p < floor * 2:
                vol = abs(vol) + 0.2 
                
            # US_50 무조건 상승
            if t == "US_STOCK_50":
                vol = abs(vol) if vol != 0 else 0.1
            
            curr_p *= (1 + vol)
            
            # 실제 상폐 기준 (거의 도달 불가능하게 설정)
            if curr_p < 0.1: 
                server['delisted'].add(t)
                break
        
        server['prices'][t] = max(curr_p, 0.1)
        server['history'][t].append(server['prices'][t])
        server['history'][t] = server['history'][t][-40:]

    server['last_sync'] = now

update_server_engine()

# --- 4. 랭킹 업데이트 ---
my_total = st.session_state.balance
for t, info in st.session_state.portfolio.items():
    my_total += info['수량'] * server['prices'].get(t, 0)
server['rankings'][st.session_state.user_id] = my_total

# --- 5. UI 구성 ---
# 우측 상단 관리 버튼들
t_l, t_c, t_r = st.columns([6, 2, 2])
with t_c:
    if not st.session_state.is_blackmarket:
        if st.button("🌑 암시장 진입"): st.session_state.ask_b = True
    else:
        if st.button("🚪 암시장 탈출"): st.session_state.is_blackmarket = False; st.rerun()

with t_r:
    if not st.session_state.is_admin:
        if st.button("🛠️ 제작자 모드"): st.session_state.ask_a = True
    else:
        if st.button("🔒 모드 해제"): st.session_state.is_admin = False; st.rerun()

# PW 입력창
if st.session_state.get('ask_b'):
    if st.text_input("Black Market PW", type="password") == "0328":
        st.session_state.is_blackmarket = True; st.session_state.ask_b = False; st.rerun()
if st.session_state.get('ask_a'):
    if st.text_input("Admin Master PW", type="password") == "1908441199470328":
        st.session_state.is_admin = True; st.session_state.ask_a = False; st.rerun()

# 사이드바 랭킹 보드
st.sidebar.title("🏆 실시간 전역 랭킹")
rdf = pd.DataFrame([{"ID": k, "Asset": v} for k, v in server['rankings'].items()])
if not rdf.empty:
    rdf = rdf.sort_values("Asset", ascending=False).head(10).reset_index(drop=True)
    st.sidebar.table(rdf.style.format({"Asset": "${:,.0f}"}))

# 제작자 컨트롤 패널
if st.session_state.is_admin:
    with st.container(border=True):
        st.write("### 🛠️ SERVER MASTER CONTROL")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔴 전 시장 강제 폭락 (-90%)"):
                for t in server['prices']: server['prices'][t] *= 0.1
        with c2:
            if st.button("🟢 전 시장 강제 폭등 (+300%)"):
                for t in server['prices']: server['prices'][t] *= 3.0
        with c3:
            pick = st.selectbox("종목 선택", [t for t in server['prices'].keys() if t not in server['delisted']])
            if st.button("🗑️ 해당 종목 강제 상폐"): server['delisted'].add(pick)

# 메인 차트 및 거래
ticker = "US_STOCK_50" if st.session_state.is_blackmarket else st.sidebar.selectbox("종목", [t for t in server['prices'].keys() if t not in server['delisted'] and t != "US_STOCK_50"])
curr_price = server['prices'][ticker]
hist_data = server['history'][ticker]

st.title(f"{ticker} {'(DARK)' if st.session_state.is_blackmarket else ''}")
st.header(f"${curr_price:,.2f}")

fig = go.Figure(data=[go.Candlestick(x=list(range(len(hist_data))), open=[p*0.99 for p in hist_data], high=[p*1.01 for p in hist_data], low=[p*0.98 for p in hist_data], close=hist_data)])
fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 거래 로직
c1, c2, c3 = st.columns(3)
with c1: qty = st.number_input("수량", min_value=1, value=1)
with c2:
    if st.button("BUY"):
        if st.session_state.balance >= qty * curr_price:
            st.session_state.balance -= qty * curr_price
            p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
            p['평단가'] = ((p['평단가']*p['수량']) + (qty*curr_price)) / (p['수량']+qty)
            p['수량'] += qty
            st.session_state.portfolio[ticker] = p
            st.rerun()
with c3:
    hold = st.session_state.portfolio.get(ticker, {'수량': 0})['수량']
    if st.button(f"SELL ALL ({hold})"):
        if hold > 0:
            st.session_state.balance += hold * curr_price
            st.session_state.portfolio[ticker]['수량'] = 0
            st.rerun()
