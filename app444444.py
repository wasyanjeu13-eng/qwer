import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# 1. 시스템 설정 (오류 방지를 위한 안정화 로직)
try:
    from streamlit_autorefresh import st_autorefresh
except:
    st.error("터미널에 'pip install streamlit-autorefresh'를 입력하여 라이브러리를 설치해주세요.")
    st.stop()

st.set_page_config(page_title="STOCK WAR: OMEGA GENESIS", layout="wide")
st_autorefresh(interval=1000, key="omega_genesis_fixed_final")

# 다크 모드 스타일 강제 적용 (흰 화면 방지)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1A1C24; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# 2. [DB] 중앙 데이터베이스 (모든 기능 통합 저장소)
@st.cache_resource
def init_full_db():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 81)]
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM"]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE"]
    all_t = stocks + vips + coins
    now = datetime.now()
    history = {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t}
    return {
        "history": history, "users": {}, "chat": [], "clans": {}, 
        "auction": {"item": "시세 조작권", "bid": 1000000, "bidder": None},
        "trade_requests": [], # 직거래 제안함
        "last_sync": now, "last_payout": time.time(),
        "news": {"title": "오메가 시스템 정상 가동", "impact": 0, "target": None, "time": now}
    }

db = init_full_db()

# 3. [엔진] 시세 변동 + 클랜 초당 수익 엔진
def run_master_engine():
    now = datetime.now()
    if (now - db['last_sync']).total_seconds() >= 1:
        for n in db['history']:
            data = db['history'][n]
            last_p = data[-1][4]
            vol = 0.55 if any(c in n for c in ["₿", "💎", "🐕"]) else 0.20
            change = np.random.uniform(-vol, vol)
            new_p = max(last_p * (1 + change), 1.0)
            data.append([now, last_p, max(last_p, new_p)*1.02, min(last_p, new_p)*0.98, new_p])
            db['history'][n] = data[-30:]
        db['last_sync'] = now

    # 클랜 기부금 비례 초당 자동 수익 (0.01%)
    cur_t = time.time()
    if cur_t - db['last_payout'] >= 1:
        for uid in db['users']:
            udata = db['users'][uid]
            if udata.get('clan'):
                clan = db['clans'].get(udata['clan'])
                if clan:
                    donated_amt = clan['donated'].get(uid, 0)
                    udata['bal'] += donated_amt * 0.0001 
        db['last_payout'] = cur_t

run_master_engine()

# 4. [보안/로그인]
if 'uid' not in st.session_state:
    st.title("🔐 OMEGA GENESIS - 시스템 접속")
    t1, t2 = st.tabs(["로그인", "회원가입"])
    with t2:
        rid = st.text_input("새 ID")
        rpw = st.text_input("새 PW", type="password")
        if st.button("계정 생성"):
            db['users'][rid] = {"pw": rpw, "bal": 100000.0, "port": {}, "items": ["🎁 환영 패키지"], "title": "🌱 우주 먼지", "color": "#FFF", "clan": None}
            st.success("완료")
    with t1:
        lid = st.text_input("ID")
        lpw = st.text_input("PW", type="password")
        if st.button("입장"):
            if lid in db['users'] and db['users'][lid]['pw'] == lpw:
                st.session_state.uid = lid; st.rerun()
    st.stop()

uid = st.session_state.uid
user = db['users'][uid]

# 5. [제작자 권능] (사이드바)
with st.sidebar:
    st.header("👑 GOD MODE")
    m_pw = st.text_input("MASTER PW", type="password")
    if m_pw == "190844119947201110328":
        st.session_state.is_admin = True
        user['title'], user['color'] = "🔥 SYSTEM MASTER", "#FF4B4B"
        st.divider()
        target = st.selectbox("지급 대상", list(db['users'].keys()))
        amt = st.number_input("지급액 ($)", value=1000000000)
        if st.button("💰 즉시 돈 지급"):
            db['users'][target]['bal'] += amt
            st.success(f"{target}에게 ${amt:,} 지급 완료")

# 6. [메인 대시보드 및 월드 채팅]
col_main, col_chat = st.columns([3, 1])

with col_main:
    st.markdown(f"<h1><span style='color:{user['color']}'>[{user['title']}]</span> {uid} | 💰 ${user['bal']:,.2f}</h1>", unsafe_allow_html=True)
    
    # 이미지에 있던 탭 순서 그대로 재현
    tabs = st.tabs(["📈 거래소", "💎 VIP(1억↑)", "🤝 직거래", "🎰 도박", "🏴‍☠️ 클랜", "🏷️ 칭호", "🔨 경매"])

    with tabs[0]: # 거래소
        sel = st.selectbox("종목 선택", list(db['history'].keys()))
        df = pd.DataFrame(db['history'][sel], columns=['t', 'o', 'h', 'l', 'c'])
        fig = go.Figure(data=[go.Candlestick(x=df['t'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.metric(sel, f"${df['c'].iloc[-1]:,.2f}")
        qty = st.number_input("수량", min_value=1, value=1, key="trade_q")
        if st.button("매수 (LONG)"):
            if user['bal'] >= df['c'].iloc[-1] * qty:
                user['bal'] -= df['c'].iloc[-1] * qty
                user['port'][sel] = user['port'].get(sel, 0) + qty
                st.rerun()

    with tabs[2]: # 직거래 (아이템/주식/코인 팔기)
        st.subheader("🤝 직거래 (아이템 및 자산 판매)")
        target_u = st.selectbox("거래 유저 선택", [u for u in db['users'] if u != uid])
        t_type = st.radio("판매 항목", ["아이템", "주식/코인"])
        
        asset = st.selectbox("보유 자산 선택", user['items'] if t_type == "아이템" else [k for k, v in user['port'].items() if v > 0])
        price = st.number_input("판매 가격", min_value=0)
        t_qty = st.number_input("판매 수량", min_value=1, value=1) if t_type == "주식/코인" else 1

        if st.button("거래 제안 보내기"):
            db['trade_requests'].append({"seller": uid, "buyer": target_u, "asset": asset, "price": price, "qty": t_qty, "type": t_type})
            st.success("제안 전송됨!")

        st.divider()
        st.subheader("📥 나에게 온 제안")
        for i, req in enumerate(db['trade_requests']):
            if req['buyer'] == uid:
                st.warning(f"{req['seller']}의 제안: {req['asset']} x{req['qty']} -> ${req['price']:,}")
                if st.button(f"수락 #{i}"):
                    if user['bal'] >= req['price']:
                        user['bal'] -= req['price']
                        db['users'][req['seller']]['bal'] += req['price']
                        if req['type'] == "아이템":
                            user.setdefault('items', []).append(req['asset'])
                            db['users'][req['seller']]['items'].remove(req['asset'])
                        else:
                            user['port'][req['asset']] = user['port'].get(req['asset'], 0) + req['qty']
                            db['users'][req['seller']]['port'][req['asset']] -= req['qty']
                        db['trade_requests'].pop(i); st.rerun()

    with tabs[4]: # 클랜 (승인제 및 초당 배당)
        st.subheader("🏴‍☠️ 클랜 시스템")
        if not user['clan']:
            c_name = st.text_input("클랜 창설 이름")
            if st.button("창설하기"):
                db['clans'][c_name] = {"owner": uid, "members": [uid], "donated": {}, "pending": []}
                user['clan'] = c_name; st.rerun()
            
            st.divider()
            target_clan = st.selectbox("가입 신청할 클랜", list(db['clans'].keys()))
            if st.button("가입 신청"):
                if uid not in db['clans'][target_clan]['pending']:
                    db['clans'][target_clan]['pending'].append(uid)
                    st.info("신청 완료! 클랜장의 승인을 기다리세요.")
        else:
            clan = db['clans'][user['clan']]
            st.write(f"🏷️ 소속 클랜: **{user['clan']}**")
            st.write(f"📈 나의 기부액: ${clan['donated'].get(uid, 0):,}")
            st.write(f"💰 초당 배당 수익: **${(clan['donated'].get(uid, 0) * 0.0001):,.2f}/sec**")
            
            if clan['owner'] == uid: # 클랜장 전용 승인 목록
                st.subheader("🔔 가입 신청 관리")
                for p_uid in clan['pending']:
                    c1, c2 = st.columns(2)
                    if c1.button(f"승인: {p_uid}"):
                        clan['members'].append(p_uid)
                        db['users'][p_uid]['clan'] = user['clan']
                        clan['pending'].remove(p_uid); st.rerun()
                    if c2.button(f"거절: {p_uid}"):
                        clan['pending'].remove(p_uid); st.rerun()

            donate_val = st.number_input("기부할 금액", min_value=1000)
            if st.button("클랜 기부"):
                if user['bal'] >= donate_val:
                    user['bal'] -= donate_val
                    clan['donated'][uid] = clan['donated'].get(uid, 0) + donate_val
                    st.rerun()

with col_chat: # 월드 채팅
    st.subheader("💬 월드 채팅")
    c_box = st.container(height=500)
    for m in db['chat'][-30:]:
        u_info = db['users'].get(m['u'], {"color": "#FFF", "title": "???"})
        c_box.markdown(f"<span style='color:{u_info['color']}'><b>[{u_info['title']}] {m['u']}</b></span>: {m['msg']}", unsafe_allow_html=True)
    with st.form("chat_f", clear_on_submit=True):
        msg = st.text_input("메시지 입력")
        if st.form_submit_button("전송"):
            db['chat'].append({"u": uid, "msg": msg}); st.rerun()
