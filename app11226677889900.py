import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# 1. 환경 설정 및 실시간 동기화 (1초 단위)
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("streamlit-autorefresh 설치가 필요합니다.")
    st.stop()

st.set_page_config(page_title="STOCK WAR: GOD-MODE", layout="wide")
st_autorefresh(interval=1000, key="omega_god_final")

# 2. [DB] 전 서버 통합 중앙 데이터베이스
@st.cache_resource
def init_server():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 81)] # 일반 80개
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM"] # VIP 3개
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE"] # 코인 3개
    all_t = stocks + vips + coins
    now = datetime.now()
    return {
        "history": {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t},
        "users": {}, "clans": {}, "market_orders": [], "chat_log": [],
        "last_payout": time.time(), "banned": set(), "market_frozen": False,
        "news": {"title": "서버 가동", "impact": 0, "target": None, "time": now},
        "auction": {"item": "뉴스 조작권", "high_bid": 1000000, "bidder_id": None, "end_time": now + timedelta(minutes=10)},
        "last_sync": now
    }

server = init_server()

# 3. [시스템] 칭호 및 계급 (능력치 및 색상)
TITLES = {
    "🌱 우주 먼지": {"min": 0, "color": "#FFFFFF"},
    "🐜 개미 대장": {"min": 1000000, "color": "#CD7F32"},
    "💰 자산가": {"min": 50000000, "color": "#FFD700"},
    "👑 억만장자": {"min": 500000000, "color": "#B9F2FF"},
    "🌌 주권자": {"min": 1000000000, "color": "#E5E4E2"},
    "🔥 SYSTEM MASTER": {"min": 0, "color": "#FF0000"} # 관리자 전용
}

# 4. [엔진] 뉴스, 시세, 클랜 수익
def run_engine():
    now = datetime.now()
    # 지능형 뉴스 엔진 (45초마다 발생)
    if (now - server['news']['time']).total_seconds() > 45:
        target = random.choice(list(server['history'].keys()))
        impact = random.uniform(-0.5, 0.5)
        title = "🚀 폭등 예고!" if impact > 0 else "📉 상장 폐지 위기?"
        server['news'] = {"title": f"{target} {title}", "impact": impact, "target": target, "time": now}
    
    # 시세 변동 및 잔상 하락 로직
    if (now - server['last_sync']).total_seconds() >= 1:
        for n, data in server['history'].items():
            last_p = data[-1][4]
            vol = 0.2 if any(c in n for c in ["₿", "💎", "🐕"]) else 0.05
            change = np.random.uniform(-vol, vol)
            if n == server['news']['target']: 
                change += server['news']['impact']
                server['news']['impact'] *= 0.8 # 뉴스 영향력 서서히 감소 (잔상 로직)
            new_p = max(last_p * (1 + change), 1.0)
            data.append([now, last_p, last_p*1.05, last_p*0.95, new_p])
            server['history'][n] = data[-30:]
        server['last_sync'] = now

run_engine()

# 5. [보안] 로그인 및 제작자 권능 체크
if 'user_id' not in st.session_state:
    st.title("🔐 OMEGA GENESIS - AUTHORIZED ONLY")
    t1, t2 = st.tabs(["로그인", "회원가입"])
    with t2:
        r_id = st.text_input("아이디")
        r_pw = st.text_input("비밀번호", type="password")
        if st.button("신규 계정 생성"):
            server['users'][r_id] = {"pw": r_pw, "nick": r_id, "balance": 100000.0, "portfolio": {}, "shorts": {}, "titles": ["🌱 우주 먼지"], "equipped_title": "🌱 우주 먼지", "clan": None}
            st.success("가입 완료")
    with t1:
        l_id = st.text_input("ID")
        l_pw = st.text_input("PW", type="password")
        if st.button("접속"):
            if l_id in server['users'] and server['users'][l_id]['pw'] == l_pw:
                if l_id in server['banned']: st.error("🚨 영구 추방된 계정입니다.")
                else: st.session_state.user_id = l_id; st.rerun()
    st.stop()

u_id = st.session_state.user_id
user = server['users'][u_id]

# 제작자 패널 인증 (비번: 190844119947201110328)
if st.sidebar.button("👑 GOD CONTROL"): st.session_state.ask_ad = True
if st.session_state.get('ask_ad'):
    if st.sidebar.text_input("MASTER PASSWORD", type="password") == "190844119947201110328":
        st.session_state.is_admin = True
        if "🔥 SYSTEM MASTER" not in user['titles']: user['titles'].append("🔥 SYSTEM MASTER")
        user['equipped_title'] = "🔥 SYSTEM MASTER"

# 6. [GOD-MODE] 제작자 전용 컨트롤 타워
if st.session_state.get('is_admin'):
    with st.expander("🛠️ 제작자 정밀 컨트롤 (신의 권능)", expanded=True):
        m1, m2, m3 = st.tabs(["🌎 시장 조작", "🎯 유저 저격", "📦 시스템"])
        with m1:
            if st.button("🔥 전 종목 1000% 폭등"):
                for k in server['history']: server['history'][k][-1][4] *= 11
            if st.button("🧊 전 종목 99% 폭락"):
                for k in server['history']: server['history'][k][-1][4] *= 0.01
            server['market_frozen'] = st.toggle("🚫 전 서버 거래 동결", value=server['market_frozen'])
        with m2:
            target_u = st.selectbox("타겟 유저 선택", list(server['users'].keys()))
            if st.button("💸 자산 몰수 (0원)"): server['users'][target_u]['balance'] = 0
            if st.button("💀 영구 추방(BAN)"): server['banned'].add(target_u)
            if st.button("🧺 보유 주식 강제 압류"): server['users'][target_u]['portfolio'] = {}
        with m3:
            s_ticker = st.selectbox("시세 고정 종목", list(server['history'].keys()))
            fixed_p = st.number_input("고정 가격", value=1000.0)
            if st.button("🎯 가격 즉시 고정"): server['history'][s_ticker][-1][4] = fixed_p

# 7. [메인 UI] 대시보드
st.title(f"[{user['equipped_title']}] {user['nick']} | 💰 ${user['balance']:,.0f}")
st.info(f"🗞️ 뉴스: {server['news']['title']}")

tabs = st.tabs(["📈 거래소", "💎 VIP(1억↑)", "🤝 직거래", "🎰 도박", "🏴‍☠️ 클랜", "🏷️ 칭호", "🔨 경매"])

with tabs[0]: # 거래소 (롱/숏)
    ticker = st.selectbox("종목", [f"K-Corp_{i:02d}" for i in range(1, 81)])
    curr_p = server['history'][ticker][-1][4]
    st.metric(ticker, f"${curr_p:,.2f}")
    if server['market_frozen']: st.error("거래가 동결되었습니다.")
    else:
        c1, c2 = st.columns(2)
        if c1.button("LONG (매수)"):
            if user['balance'] >= curr_p:
                user['balance'] -= curr_p
                user['portfolio'][ticker] = user['portfolio'].get(ticker, 0) + 1
        if c2.button("SHORT (공매도)"):
            if user['balance'] >= curr_p:
                user['balance'] -= curr_p # 증거금 담보
                user['shorts'][ticker] = user['shorts'].get(ticker, 0) + 1

with tabs[1]: # VIP 시장
    if user['balance'] < 100000000 and not st.session_state.get('is_admin'):
        st.error("🚫 자산 1억 이상의 VIP만 입장 가능합니다.")
    else:
        v_ticker = st.selectbox("VIP 종목", ["₿_BITCOIN", "🥇GOLD_FUND", "🏰ROYAL_ESTATE"])
        st.write(f"현재가: ${server['history'][v_ticker][-1][4]:,.2f}")

with tabs[3]: # 도박
    bet = st.number_input("도박 배팅", min_value=1000, max_value=int(user['balance']))
    if st.button("🎰 4배 도박 (20%)"):
        if random.random() < 0.2: user['balance'] += bet*3; st.balloons()
        else: user['balance'] -= bet; st.error("꽝")

with tabs[5]: # 칭호 장착
    user['equipped_title'] = st.selectbox("장착할 칭호", user['titles'])
    st.rerun()

with tabs[6]: # 경매 (Snipe Protection)
    auc = server['auction']
    remain = (auc['end_time'] - datetime.now()).total_seconds()
    st.subheader(f"🔨 물품: {auc['item']}")
    if remain > 0:
        st.write(f"최고 입찰: ${auc['high_bid']:,.0f} ({auc['bidder_id']})")
        st.warning(f"남은 시간: {int(remain)}초")
        bid = st.number_input("입찰가", min_value=int(auc['high_bid']*1.1))
        if st.button("입찰"):
            auc['high_bid'] = bid; auc['bidder_id'] = u_id
            auc['end_time'] += timedelta(seconds=30) # 시간 연장
            st.rerun()

# 8. [채팅]
st.sidebar.subheader("💬 월드 채팅")
for c in server['chat_log'][-20:]:
    st.sidebar.markdown(f"<b style='color:{TITLES.get(user['equipped_title'], {}).get('color', '#FFF')}'>{c['nick']}</b>: {c['msg']}", unsafe_allow_html=True)
with st.sidebar.form("chat"):
    m = st.text_input("메시지")
    if st.form_submit_button("전송"):
        server['chat_log'].append({"nick": f"[{user['equipped_title']}] {user['nick']}", "msg": m})
        st.rerun()
