import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# 1. 환경 설정 및 다크 테마 강제 적용
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("streamlit-autorefresh 설치가 필요합니다. 'pip install streamlit-autorefresh'를 실행하세요.")
    st.stop()

st.set_page_config(
    page_title="STOCK WAR: OMEGA GENESIS", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS를 이용해 배경을 어둡게 강제 설정 (흰 화면 방지)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1A1C24; border-radius: 5px; color: white; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(interval=1000, key="omega_infinity_dark_v6")

# 2. [DB] 중앙 데이터베이스 (링크 앱 기반 86개 종목)
@st.cache_resource
def init_server():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 81)]
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM"]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE"]
    all_t = stocks + vips + coins
    now = datetime.now()
    history = {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t}
    return {
        "history": history, "users": {}, "chat_log": [], "banned": set(), 
        "market_frozen": False, "last_sync": now,
        "news": {"title": "오메가 엔진 온라인", "impact": 0, "target": None, "time": now},
        "auction": {"item": "뉴스 조작권", "high_bid": 1000000, "bidder_id": None, "end_time": now + timedelta(minutes=10)}
    }

server = init_server()

# 3. [데이터] 계급 색상 정의
TITLES = {
    "🌱 우주 먼지": {"color": "#FFFFFF"},
    "🐜 개미 대장": {"color": "#CD7F32"},
    "💰 자산가": {"color": "#FFD700"},
    "👑 억만장자": {"color": "#B9F2FF"},
    "🌌 주권자": {"color": "#E5E4E2"},
    "🔥 SYSTEM MASTER": {"color": "#FF4B4B"}
}

# 4. [엔진] 극심한 변동성 엔진
def run_engine():
    now = datetime.now()
    if (now - server['last_sync']).total_seconds() >= 1:
        for n in server['history']:
            data = server['history'][n]
            last_p = data[-1][4]
            # 극강의 변동폭 (코인 최대 60%, 일반주 30%)
            vol = 0.6 if any(c in n for c in ["₿", "💎", "🐕"]) else 0.3
            change = np.random.uniform(-vol, vol)
            
            # 뉴스 영향력
            if n == server['news']['target']:
                change += server['news']['impact']
                server['news']['impact'] *= 0.8
                
            new_p = max(last_p * (1 + change), 1.0)
            data.append([now, last_p, max(last_p, new_p)*1.02, min(last_p, new_p)*0.98, new_p])
            server['history'][n] = data[-30:]
        server['last_sync'] = now

run_engine()

# 5. [보안/로그인]
if 'user_id' not in st.session_state:
    st.title("🌌 OMEGA GENESIS: INFINITY")
    col_l, col_r = st.columns(2)
    with col_l:
        l_id = st.text_input("ID")
        l_pw = st.text_input("PW", type="password")
        if st.button("시스템 접속"):
            if l_id in server['users'] and server['users'][l_id]['pw'] == l_pw:
                st.session_state.user_id = l_id; st.rerun()
    with col_r:
        r_id = st.text_input("ID 생성")
        r_pw = st.text_input("PW 설정", type="password")
        if st.button("계정 생성"):
            server['users'][r_id] = {"pw": r_pw, "nick": r_id, "balance": 100000.0, "portfolio": {}, "shorts": {}, "titles": ["🌱 우주 먼지"], "equipped_title": "🌱 우주 먼지"}
            st.success("가입 완료")
    st.stop()

user = server['users'][st.session_state.user_id]

# 6. [사이드바] 제작자 컨트롤 패널 (자산 지급 포함)
with st.sidebar:
    st.header("👑 CONTROL TOWER")
    if st.button("GOD MODE 활성화"): st.session_state.master_access = True
    if st.session_state.get('master_access'):
        if st.text_input("PASSWORD", type="password") == "190844119947201110328":
            st.session_state.is_admin = True
            user['equipped_title'] = "🔥 SYSTEM MASTER"
            st.success("신의 권능이 부여되었습니다.")
            
            st.divider()
            target = st.selectbox("지급 타겟", list(server['users'].keys()))
            amt = st.number_input("금액($)", value=1000000000)
            if st.button("💰 자산 즉시 주입"):
                server['users'][target]['balance'] += amt
                st.balloons()
            
            if st.button("🔥 시장 1000% 폭등"):
                for k in server['history']: server['history'][k][-1][4] *= 11

# 7. [메인 UI]
col_main, col_chat = st.columns([3, 1])

with col_main:
    u_color = TITLES[user['equipped_title']]['color']
    st.markdown(f"<h1 style='color:{u_color}'>[{user['equipped_title']}] {user['nick']} | 💰 ${user['balance']:,.0f}</h1>", unsafe_allow_html=True)
    st.warning(f"📢 속보: {server['news']['title']}")

    tabs = st.tabs(["📈 거래소", "💎 VIP", "🤝 직거래", "🎰 도박", "🏴‍☠️ 클랜", "🏷️ 칭호", "🔨 경매"])

    with tabs[0]:
        ticker = st.selectbox("종목 선택", list(server['history'].keys()))
        df = pd.DataFrame(server['history'][ticker], columns=['time', 'open', 'high', 'low', 'close'])
        
        # 그래프 생성
        fig = go.Figure(data=[go.Candlestick(
            x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            increasing_line_color='#FF4B4B', decreasing_line_color='#0080FF'
        )])
        fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig, use_container_width=True)
        
        curr_p = df['close'].iloc[-1]
        st.metric(ticker, f"${curr_p:,.2f}")
        
        c1, c2 = st.columns(2)
        qty = st.number_input("거래량", min_value=1, value=1)
        if c1.button("LONG"):
            if user['balance'] >= curr_p * qty:
                user['balance'] -= curr_p * qty
                user['portfolio'][ticker] = user['portfolio'].get(ticker, 0) + qty
        if c2.button("SHORT"):
            if user['balance'] >= curr_p * qty:
                user['balance'] -= curr_p * qty
                user['shorts'][ticker] = user['shorts'].get(ticker, 0) + qty

with col_chat:
    st.subheader("💬 월드 채팅")
    chat_box = st.container(height=500)
    with chat_box:
        for c in server['chat_log'][-25:]:
            color = TITLES.get(c['title'], {"color":"#FFF"})['color']
            st.markdown(f"<span style='color:{color}'><b>[{c['title']}] {c['nick']}</b></span>: {c['msg']}", unsafe_allow_html=True)
    
    with st.form("chat", clear_on_submit=True):
        m = st.text_input("메시지")
        if st.form_submit_button("전송") and m:
            server['chat_log'].append({"nick": user['nick'], "title": user['equipped_title'], "msg": m})
            st.rerun()
