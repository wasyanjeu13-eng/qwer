import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# 1. 환경 설정 및 실시간 동기화
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("streamlit-autorefresh 설치가 필요합니다.")
    st.stop()

st.set_page_config(page_title="STOCK WAR: ABSOLUTE GOD", layout="wide")
st_autorefresh(interval=2000, key="god_final_sync")

# 2. 전 서버 통합 데이터베이스 (DB)
@st.cache_resource
def init_ultimate_server():
    # 100개 이상의 종목 구성 (일반, VIP, 코인)
    stocks = [f"Corp_{i:02d}" for i in range(1, 81)]
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM", "🚀MARS_COLONY"]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE", "🪐_SOLANA"]
    all_t = stocks + vips + coins
    now = datetime.now()
    return {
        "history": {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t},
        "users": {},      
        "chat_log": [],
        "banned": set(),
        "market_frozen": False,
        "news": {"title": "서버 가동 완료", "impact": 0, "target": None, "time": now},
        "auction": {"item": "뉴스 조작권", "high_bid": 1000000, "bidder_id": None, "end_time": now + timedelta(minutes=10)},
        "last_sync": now
    }

server = init_ultimate_server()

# 3. 유저 칭호 및 시장 접근 권한 로직
def get_user_meta(balance):
    if balance >= 1000000000: return "🌌 은하계 주권자", "#E5E4E2", True
    if balance >= 100000000: return "👑 억만장자", "#FFD700", True
    if balance >= 10000000: return "💰 자산가", "#C0C0C0", False
    return "🌱 일반 개미", "#FFFFFF", False

# 4. 로그인 / 계정 생성 시스템
if 'user_id' not in st.session_state:
    st.title("🔐 ABSOLUTE GOD EXCHANGE")
    t1, t2 = st.tabs(["로그인", "계정 생성"])
    with t2:
        r_id = st.text_input("아이디", key="r_id")
        r_pw = st.text_input("비번", type="password", key="r_pw")
        r_nk = st.text_input("닉네임", key="r_nk")
        if st.button("신규 가입"):
            if r_id and r_pw and r_id not in server['users']:
                server['users'][r_id] = {"pw": r_pw, "nick": r_nk, "balance": 100000.0, "portfolio": {}, "shorts": {}, "log": []}
                st.success("가입 성공! 로그인 하세요.")
    with t1:
        l_id = st.text_input("ID", key="l_id")
        l_pw = st.text_input("PW", type="password", key="l_pw")
        if st.button("서버 접속"):
            if l_id in server['users'] and server['users'][l_id]['pw'] == l_pw:
                if l_id in server['banned']: st.error("추방된 계정입니다.")
                else: st.session_state.user_id = l_id; st.rerun()
            else: st.error("정보 불일치")
    st.stop()

u_id = st.session_state.user_id
user = server['users'][u_id]
rank_n, rank_c, is_vip = get_user_meta(user['balance'])

# 5. 제작자 마스터 권한 (비밀번호: 190844119947201110328)
if st.sidebar.button("👑 GOD CONTROL"): st.session_state.ask_ad = True
if st.session_state.get('ask_ad'):
    if st.sidebar.text_input("MASTER PASSWORD", type="password") == "190844119947201110328":
        st.session_state.is_admin = True
        st.sidebar.success("접속 성공: 신의 권능이 부여되었습니다.")

# 6. 시세 엔진 (롱/숏 및 뉴스 영향)
def run_master_engine():
    now = datetime.now()
    if (now - server['last_sync']).total_seconds() < 1: return
    for n, data in server['history'].items():
        last_p = data[-1][4]
        vol = 0.25 if "₿" in n else 0.07
        change = np.random.uniform(-vol, vol)
        if n == server['news']['target']:
            change += server['news']['impact'] if (now - server['news']['time']).total_seconds() < 10 else -0.05
        new_p = max(last_p * (1 + change), 1.0)
        data.append([now, last_p, last_p*1.05, last_p*0.95, new_p])
        server['history'][n] = data[-30:]
    server['last_sync'] = now

run_master_engine()

# --- 7. 제작자 전용 초정밀 컨트롤 패널 (기능 대폭 세분화) ---
if st.session_state.get('is_admin'):
    with st.container(border=True):
        st.subheader("🛠️ GOD-MODE 초정밀 컨트롤러")
        m_t1, m_t2, m_t3, m_t4 = st.tabs(["시세 조작", "유저 감시 및 처벌", "아이템/경매 조작", "서버 관리"])
        
        with m_t1:
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🔥 시장 전체 폭등"): 
                    for t in server['history']: server['history'][t][-1][4] *= 5
            with c2:
                if st.button("🧊 시장 전체 폭락"):
                    for t in server['history']: server['history'][t][-1][4] *= 0.1
            with c3:
                server['market_frozen'] = st.toggle("🚫 전 서버 거래 동결", value=server['market_frozen'])
            
            t_stock = st.selectbox("정밀 조작 종목", list(server['history'].keys()))
            set_p = st.number_input("강제 가격 설정", value=1000.0)
            if st.button("🎯 가격 즉시 수정"): server['history'][t_stock][-1][4] = set_p

        with m_t2:
            t_u = st.selectbox("처벌 대상 유저", list(server['users'].keys()))
            u_ref = server['users'][t_u]
            st.json({"닉네임": u_ref['nick'], "잔고": u_ref['balance'], "포트폴리오": u_ref['portfolio']})
            cc1, cc2, cc3 = st.columns(3)
            if cc1.button("💸 자산 몰수 (0원)"): u_ref['balance'] = 0
            if cc2.button("🎒 주식 강제 매도"): u_ref['portfolio'] = {}
            if cc3.button("💀 영구 추방(BAN)"): server['banned'].add(t_u)
            
        with m_t3:
            st.write("경매장 아이템 강제 변경")
            new_item = st.text_input("새 아이템 명", "관리자의 축복")
            if st.button("♻️ 경매 즉시 리셋"):
                server['auction'] = {"item": new_item, "high_bid": 1000000, "bidder_id": None, "end_time": datetime.now() + timedelta(minutes=5)}

        with m_
