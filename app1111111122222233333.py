import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# 1. 자동 새로고침 설정 (데이터 실시간 동기화)
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("streamlit-autorefresh 설치가 필요합니다.")
    st.stop()

st.set_page_config(page_title="STOCK WAR: ABSOLUTE GOD", layout="wide")
st_autorefresh(interval=2000, key="god_final_v2_sync")

# 2. 전 서버 통합 데이터베이스 (중앙 메모리 시스템)
@st.cache_resource
def init_ultimate_server():
    stocks = [f"Corp_{i:02d}" for i in range(1, 81)] # 일반 80개
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM", "🚀MARS_COLONY"] # VIP 4개
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE", "🪐_SOLANA"] # 코인 4개
    all_t = stocks + vips + coins
    now = datetime.now()
    return {
        "history": {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t},
        "users": {},      
        "chat_log": [],
        "banned": set(),
        "market_frozen": False,
        "news": {"title": "시스템 가동", "impact": 0, "target": None, "time": now},
        "auction": {"item": "뉴스 조작권", "high_bid": 1000000, "bidder_id": None, "end_time": now + timedelta(minutes=10)},
        "last_sync": now
    }

server = init_ultimate_server()

# 3. 유저 계급 및 시장 접근 권한 로직
def get_user_meta(balance):
    if balance >= 1000000000: return "🌌 은하계 주권자", "#E5E4E2", True
    if balance >= 100000000: return "👑 억만장자", "#FFD700", True
    if balance >= 10000000: return "💰 자산가", "#C0C0C0", False
    return "🌱 일반 개미", "#FFFFFF", False

# 4. [기능] 로그인 및 계정 생성 시스템
if 'user_id' not in st.session_state:
    st.title("🔐 ABSOLUTE GOD EXCHANGE")
    t1, t2 = st.tabs(["로그인", "회원가입"])
    with t2:
        r_id = st.text_input("아이디", key="r_id")
        r_pw = st.text_input("비밀번호", type="password", key="r_pw")
        r_nk = st.text_input("닉네임", key="r_nk")
        if st.button("신규 계정 생성"):
            if r_id and r_pw and r_id not in server['users']:
                server['users'][r_id] = {"pw": r_pw, "nick": r_nk, "balance": 100000.0, "portfolio": {}, "shorts": {}}
                st.success("회원가입 완료! 로그인 하세요.")
            else: st.error("ID가 중복되거나 비어있습니다.")
    with t1:
        l_id = st.text_input("아이디", key="l_id")
        l_pw = st.text_input("비밀번호", type="password", key="l_pw")
        if st.button("거래소 입장"):
            if l_id in server['users'] and server['users'][l_id]['pw'] == l_pw:
                if l_id in server['banned']: st.error("🚨 영구 추방된 계정입니다.")
                else: st.session_state.user_id = l_id; st.rerun()
            else: st.error("정보가 틀렸습니다.")
    st.stop()

# 추방 실시간 체크
u_id = st.session_state.user_id
if u_id in server['banned']: st.error("당신은 추방되었습니다."); st.stop()

user = server['users'][u_id]
rank_n, rank_c, is_vip = get_user_meta(user['balance'])

# 5. [제작자 전용] 비밀번호 인증 (190844119947201110328)
if st.sidebar.button("👑 GOD CONTROL PANEL"): st.session_state.ask_ad = True
if st.session_state.get('ask_ad'):
    if st.sidebar.text_input("MASTER PASSWORD", type="password") == "190844119947201110328":
        st.session_state.is_admin = True
        st.sidebar.success("접속 성공: 신의 권능 부여")

# 6. [엔진] 시세 변동 로직
def run_engine():
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

run_engine()

# 7. [UI] 제작자 초정밀 컨트롤 타워
if st.session_state.get('is_admin'):
    with st.container(border=True):
        st.markdown("### 👑 GOD-MODE MASTER CONTROL TOWER")
        m_t1, m_t2, m_t3 = st.tabs(["🌎 시세/서버 조작", "👤 유저 정밀 타격", "🔨 아이템/공지"])
        with m_t1:
            c1, c2, c3 = st.columns(3)
            if c1.button("🔥 전 종목 폭등 (+500%)"):
                for t in server['history']: server['history'][t][-1][4] *= 6
            if c2.button("🧊 전 종목 폭락 (-90%)"):
                for t in server['history']: server['history'][t][-1][4] *= 0.1
            server['market_frozen'] = c3.toggle("🚫 시장 동결", value=server['market_frozen'])
            st.divider()
            t_stock = st.selectbox("종목 선택", list(server['history'].keys()), key="ad_s")
            set_p = st.number_input("가격 강제 설정", value=1000.0)
            if st.button("🎯 시세 즉시 고정"): server['history'][t_stock][-1][4] = set_p
        with m_t2:
            t_u = st.selectbox("타겟 유저", list(server['users'].keys()))
            u_ref = server['users'][t_u]
            st.json(u_ref)
            if st.button("💸 자산 몰수 (0원)"): u_ref['balance'] = 0
            if st.button("💀 영구 추방(BAN)"): server['banned'].add(t_u)
        with m_t3:
            ann = st.text_input("서버 긴급 공지")
            if st.button("📢 공지 살포"): server['chat_log'].append({"nick":"⚠️[ADMIN]","msg":ann,"id":"SYS"})
            if st.button("♻️ 경매 리셋"):
                server['auction'] = {"item": "뉴스 조작권", "high_bid": 1000000, "bidder_id": None, "end_time": datetime.now() + timedelta(minutes=5)}

# 8. [UI] 메인 게임 화면
st.markdown(f"### <span style='color:{rank_c}'>[{rank_n}]</span> {user['nick']} | 자산: ${user['balance']:,.0f}", unsafe_allow_html=True)
st.warning(f"📡 속보: {server['news']['target']} - {server['news']['title']}")

tab_tr, tab_auc, tab_chat = st.tabs(["📈 거래소(롱/숏)", "🔨 블랙마켓 경매", "💬 채팅 및 랭킹"])

with tab_tr:
    ticker = st.selectbox("종목 선택", list(server['history'].keys()))
    df = pd.DataFrame(server['history'][ticker], columns=['Date','Open','High','Low','Close'])
    curr_p = df.iloc[-1]['Close']
    fig = go.Figure(data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    if server['market_frozen']: st.error("🛑 시장이 동결되어 거래가 불가능합니다.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚀 LONG")
            l_qty = st.number_input("수량", min_value=1, key="l_q")
            if st.button("매수"):
                if user['balance'] >= l_qty * curr_p:
                    user['balance'] -= l_qty * curr_p
                    user['portfolio'][ticker] = user['portfolio'].get(ticker, 0) + l_qty
                    st.rerun()
            h = user['portfolio'].get(ticker, 0)
            if st.button(f"청산 (보유:{h})"):
                if h > 0: user['balance'] += h * curr_p; user['portfolio'][ticker] = 0; st.rerun()
        with col2:
            st.subheader("📉 SHORT")
            s_qty = st.number_input("수량", min_value=1, key="s_q")
            if st.button("공매도 진입"):
                if user['balance'] >= s_qty * curr_p:
                    user['shorts'][ticker] = user['shorts'].get(ticker, 0) + s_qty
                    user['balance'] -= (s_qty * curr_p)
                    st.rerun()
            sh = user['shorts'].get(ticker, 0)
            if st.button(f"숏 환매수 ({sh})"):
                if sh > 0: user['balance'] += sh * curr_p; user['shorts'][ticker] = 0; st.rerun()

with tab_auc:
    auc = server['auction']
    st.subheader(f"🔨 경매 물품: {auc['item']}")
    st.info(f"최고 입찰가: ${auc['high_bid']:,.0f} | 입찰자: {auc['bidder_id']}")
    bid = st.number_input("입찰가", min_value=int(auc['high_bid']*1.1), step=100000)
    if st.button("입찰하기"):
        if user['balance'] >= bid:
            auc['high_bid'] = bid; auc['bidder_id'] = u_id
            auc['end_time'] += timedelta(seconds=20); st.rerun()

with tab_chat:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.write("🏆 실시간 랭킹")
        st.table(pd.DataFrame([{"닉네임": u['nick'], "자산": u['balance']} for u in server['users'].values()]).sort_values("자산", ascending=False))
    with c2:
        st.write("💬 채팅창")
        for c in server['chat_log'][-10:]: st.write(f"**{c['nick']}**: {c['msg']}")
        msg = st.text_input("채팅 입력")
        if st.button("전송"):
            server['chat_log'].append({"nick": user['nick'], "msg": msg, "id": u_id}); st.rerun()
