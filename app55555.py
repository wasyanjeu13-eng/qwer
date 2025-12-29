import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# 1. 시스템 설정
try:
    from streamlit_autorefresh import st_autorefresh
except:
    st.error("설치 필요: pip install streamlit-autorefresh")
    st.stop()

st.set_page_config(page_title="STOCK WAR: OMEGA GENESIS", layout="wide")
st_autorefresh(interval=1000, key="omega_genesis_v13_fixed")

# 스타일 설정
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1A1C24; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. [DB] 중앙 데이터베이스
@st.cache_resource
def init_final_db():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 81)]
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM"]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE"]
    all_t = stocks + vips + coins
    now = datetime.now()
    history = {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t}
    return {
        "history": history, "users": {}, "chat": [], "clans": {}, 
        "auction": {"item": "시세 조작권", "bid": 1000000, "bidder": None, "end_time": time.time() + 600},
        "trade_requests": [], "last_sync": now, "last_payout": time.time()
    }

db = init_final_db()

# 3. [엔진] 시세 및 배당 수익
def run_engines():
    now = datetime.now()
    if (now - db['last_sync']).total_seconds() >= 1:
        for n in db['history']:
            data = db['history'][n]; last_p = data[-1][4]
            vol = 0.5 if any(c in n for c in ["₿", "💎", "🐕"]) else 0.2
            change = np.random.uniform(-vol, vol)
            new_p = max(last_p * (1 + change), 1.0)
            data.append([now, last_p, max(last_p, new_p)*1.02, min(last_p, new_p)*0.98, new_p])
            db['history'][n] = data[-30:]
        db['last_sync'] = now
    
    cur_t = time.time()
    if cur_t - db['last_payout'] >= 1:
        for uid, udata in db['users'].items():
            if udata.get('clan'):
                clan = db['clans'].get(udata['clan'])
                if clan: udata['bal'] += clan['donated'].get(uid, 0) * 0.0001
        db['last_payout'] = cur_t

run_engines()

# 4. [로그인]
if 'uid' not in st.session_state:
    st.title("🔐 OMEGA GENESIS - 접속")
    t1, t2 = st.tabs(["로그인", "회원가입"])
    with t2:
        rid = st.text_input("ID 생성")
        rpw = st.text_input("PW 생성", type="password")
        if st.button("계정 생성"):
            db['users'][rid] = {"pw": rpw, "bal": 100000.0, "port": {}, "items": ["🎁 환영 상자"], "title": "🌱 우주 먼지", "color": "#FFF", "clan": None}
            st.success("가입 성공!")
    with t1:
        lid = st.text_input("ID 입력")
        lpw = st.text_input("PW 입력", type="password")
        if st.button("시스템 입장"):
            if lid in db['users'] and db['users'][lid]['pw'] == lpw:
                st.session_state.uid = lid; st.rerun()
    st.stop()

uid = st.session_state.uid
user = db['users'][uid]

# 5. [제작자 권능] 사이드바
with st.sidebar:
    st.header("👑 MASTER")
    if st.text_input("MASTER PW", type="password") == "190844119947201110328":
        st.session_state.is_admin = True
        user['title'], user['color'] = "🔥 SYSTEM MASTER", "#FF4B4B"
        target = st.selectbox("지급 대상", list(db['users'].keys()))
        amt = st.number_input("지급액", value=1000000000)
        if st.button("💰 즉시 입금"):
            db['users'][target]['bal'] += amt; st.success("지급 완료")

# 6. [메인 대시보드]
col_m, col_c = st.columns([3, 1])

with col_m:
    st.markdown(f"<h1><span style='color:{user['color']}'>[{user['title']}]</span> {uid} | 💰 ${user['bal']:,.2f}</h1>", unsafe_allow_html=True)
    tabs = st.tabs(["📈 거래소", "💎 VIP(1억↑)", "🤝 직거래", "🎰 도박", "🏴‍☠️ 클랜", "🏷️ 칭호", "🔨 경매"])

    with tabs[0]: # 거래소
        sel = st.selectbox("종목", list(db['history'].keys()))
        df = pd.DataFrame(db['history'][sel], columns=['t', 'o', 'h', 'l', 'c'])
        fig = go.Figure(data=[go.Candlestick(x=df['t'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
        fig.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        cp = df['c'].iloc[-1]
        st.metric(sel, f"${cp:,.2f}")
        qty = st.number_input("거래량", min_value=1, value=1, key="q_st")
        if st.button("매수", key="btn_buy"):
            if user['bal'] >= cp * qty:
                user['bal'] -= cp * qty
                user['port'][sel] = user['port'].get(sel, 0) + qty
                st.rerun()

    with tabs[1]: # VIP
        st.subheader("💎 VIP 전용 자산 시장")
        if user['bal'] < 100000000:
            st.error("자산 1억 달러 이상만 입장 가능합니다.")
        else:
            st.success("VIP 전용 자산 거래 가능")
            vip_ticker = st.selectbox("VIP 종목", ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM"])
            st.write(f"현재가: ${db['history'][vip_ticker][-1][4]:,.2f}")

    with tabs[2]: # 직거래
        st.subheader("🤝 아이템 및 주식 판매")
        t_user = st.selectbox("대상 선택", [u for u in db['users'] if u != uid])
        t_item = st.selectbox("판매 항목", user['items'] + [f"주식:{k}" for k, v in user['port'].items() if v > 0])
        t_price = st.number_input("판매가", min_value=0)
        if st.button("제안 보내기"):
            db['trade_requests'].append({"seller": uid, "buyer": t_user, "item": t_item, "price": t_price})
            st.info("제안 전송 완료")
        
        st.divider()
        st.subheader("📥 받은 제안")
        for i, r in enumerate(db['trade_requests']):
            if r['buyer'] == uid:
                st.write(f"[{r['seller']}] {r['item']} -> ${r['price']:,}")
                if st.button(f"수락 #{i}"):
                    if user['bal'] >= r['price']:
                        user['bal'] -= r['price']; db['users'][r['seller']]['bal'] += r['price']
                        user['items'].append(r['item']) # 단순화된 이전
                        db['trade_requests'].pop(i); st.rerun()

    with tabs[3]: # 도박 (복구 완료)
        st.subheader("🎰 카지노 홀짝/확률")
        bet = st.number_input("배팅액", min_value=1000, max_value=int(user['bal']), step=1000)
        col1, col2 = st.columns(2)
        if col1.button("🔥 4배 챌린지 (20%)"):
            if random.random() < 0.2:
                user['bal'] += bet * 3; st.balloons()
            else: user['bal'] -= bet; st.error("낙첨")
            st.rerun()
        if col2.button("🎲 2배 홀짝 (50%)"):
            if random.random() < 0.5:
                user['bal'] += bet; st.success("당첨!")
            else: user['bal'] -= bet; st.error("낙첨")
            st.rerun()

    with tabs[4]: # 클랜 (승인제)
        st.subheader("🏴‍☠️ 클랜 시스템")
        if not user['clan']:
            c_name = st.text_input("클랜 창설")
            if st.button("창설"):
                db['clans'][c_name] = {"owner": uid, "members": [uid], "donated": {}, "pending": []}
                user['clan'] = c_name; st.rerun()
            st.divider()
            target_c = st.selectbox("가입 신청", list(db['clans'].keys()))
            if st.button("신청하기"):
                if uid not in db['clans'][target_c]['pending']:
                    db['clans'][target_c]['pending'].append(uid); st.info("신청 완료")
        else:
            clan = db['clans'][user['clan']]
            st.write(f"소속: {user['clan']} | 초당 수익: ${clan['donated'].get(uid, 0)*0.0001:,.2f}")
            if clan['owner'] == uid:
                for p in clan['pending']:
                    if st.button(f"승인: {p}"):
                        clan['members'].append(p); db['users'][p]['clan'] = user['clan']
                        clan['pending'].remove(p); st.rerun()
            d_amt = st.number_input("기부금액", min_value=1000)
            if st.button("기부"):
                if user['bal'] >= d_amt:
                    user['bal'] -= d_amt; clan['donated'][uid] = clan['donated'].get(uid, 0) + d_amt
                    st.rerun()

    with tabs[5]: # 칭호 (복구 완료)
        st.subheader("🏷️ 계급 상점")
        titles = {"🐜 개미 대장": 1000000, "💰 자산가": 10000000, "👑 억만장자": 100000000, "🌌 주권자": 1000000000}
        for t_name, price in titles.items():
            if st.button(f"{t_name} 구매 (${price:,})"):
                if user['bal'] >= price:
                    user['bal'] -= price; user['title'] = t_name
                    st.success("장착 완료"); st.rerun()

    with tabs[6]: # 경매 (복구 완료)
        st.subheader("🔨 실시간 경매")
        auc = db['auction']
        st.info(f"품목: {auc['item']} | 현재가: ${auc['bid']:,} | 입찰자: {auc['bidder']}")
        new_bid = st.number_input("입찰가", min_value=auc['bid'] + 100000)
        if st.button("입찰 참여"):
            if user['bal'] >= new_bid:
                if auc['bidder']: db['users'][auc['bidder']]['bal'] += auc['bid'] # 이전 입찰자 환급
                user['bal'] -= new_bid
                db['auction'].update({"bid": new_bid, "bidder": uid})
                st.success("최고 입찰자 등극!"); st.rerun()

with col_c: # 채팅
    st.subheader("💬 월드 채팅")
    c_box = st.container(height=500)
    for m in db['chat'][-30:]:
        u_inf = db['users'].get(m['u'], {"color":"#FFF", "title":"???"})
        c_box.markdown(f"<span style='color:{u_inf['color']}'>[{u_inf['title']}] {m['u']}</span>: {m['msg']}", unsafe_allow_html=True)
    with st.form("ch_f", clear_on_submit=True):
        m_in = st.text_input("메시지")
        if st.form_submit_button("전송"):
            db['chat'].append({"u": uid, "msg": m_in}); st.rerun()
