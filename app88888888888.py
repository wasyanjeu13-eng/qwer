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

st.set_page_config(page_title="STOCK WAR: GOD EDITION", layout="wide")
st_autorefresh(interval=1000, key="omega_genesis_v21_ultimate")

# 2. [DB] 절대 소실 방지 통합 데이터베이스
@st.cache_resource
def init_ultimate_db():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 81)]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE"]
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM"]
    all_t = stocks + coins + vips
    now = datetime.now()
    history = {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t}
    return {
        "history": history, "users": {}, "chat": [], "clans": {}, 
        "auction": {"item": "서버 지배권", "bid": 10000000, "bidder": None},
        "trade_requests": [], "last_sync": now, "last_payout": time.time(),
        "banned": set(), "server_frozen": False, "chat_mute": False, "forced_price": {}
    }

db = init_ultimate_db()

# 3. [엔진] 시세 및 클랜 배당 (능력치 보정 포함)
def run_engines():
    now = datetime.now()
    if (now - db['last_sync']).total_seconds() >= 1:
        if not db['server_frozen']:
            for n in db['history']:
                data = db['history'][n]
                if n in db['forced_price']: new_p = db['forced_price'][n]
                else:
                    last_p = data[-1][4]
                    vol = 0.6 if any(c in n for c in ["₿", "💎", "🐕"]) else 0.25
                    change = np.random.uniform(-vol, vol)
                    new_p = max(last_p * (1 + change), 1.0)
                data.append([now, new_p, new_p*1.02, new_p*0.98, new_p])
                db['history'][n] = data[-30:]
        db['last_sync'] = now
    
    cur_t = time.time()
    if cur_t - db['last_payout'] >= 1:
        for uid, udata in db['users'].items():
            if udata.get('clan'):
                clan = db['clans'].get(udata['clan'])
                if clan:
                    mult = 2 if udata['title'] == "👑 억만장자" else 1
                    udata['bal'] += clan['donated'].get(uid, 0) * 0.0001 * mult
        db['last_payout'] = cur_t

run_engines()

# 4. [보안/로그인]
if 'uid' not in st.session_state:
    st.title("🔐 OMEGA GENESIS - GOD EDITION")
    t1, t2 = st.tabs(["로그인", "회원가입"])
    with t2:
        rid = st.text_input("회원가입 ID")
        rpw = st.text_input("회원가입 PW", type="password")
        if st.button("계정 생성"):
            db['users'][rid] = {"pw": rpw, "bal": 100000.0, "port": {}, "items": ["🎁 환영 패키지"], "title": "🌱 우주 먼지", "color": "#FFF", "clan": None, "ability": "없음"}
            st.success("완료")
    with t1:
        lid = st.text_input("ID")
        lpw = st.text_input("PW", type="password")
        if st.button("입장"):
            if lid in db['banned']: st.error("🚫 밴 당한 유저입니다.")
            elif lid in db['users'] and db['users'][lid]['pw'] == lpw:
                st.session_state.uid = lid; st.rerun()
    st.stop()

uid = st.session_state.uid
user = db['users'][uid]

# 5. [신급 관리자 사이드바]
TITLE_DATA = {
    "🌱 우주 먼지": {"color": "#FFF", "ability": "없음", "price": 0},
    "🐜 개미 대장": {"color": "#CD7F32", "ability": "수수료 감면", "price": 1000000},
    "💰 자산가": {"color": "#FFD700", "ability": "도박 승률 +5%", "price": 50000000},
    "👑 억만장자": {"color": "#B9F2FF", "ability": "클랜 배당 2배", "price": 500000000},
    "🌌 주권자": {"color": "#E5E4E2", "ability": "매수 10% 할인", "price": 5000000000},
    "🔥 SYSTEM MASTER": {"color": "#FF0000", "ability": "무한 권능", "price": 0}
}

with st.sidebar:
    st.header("👑 OMNIPOTENCE")
    if st.text_input("MASTER CODE", type="password") == "190844119947201110328":
        user['title'], user['color'] = "🔥 SYSTEM MASTER", "#FF0000"
        st.divider()
        st.subheader("👤 유저 관리")
        target = st.selectbox("유저 선택", list(db['users'].keys()))
        if st.button("💰 1000억 지급"): db['users'][target]['bal'] += 100000000000
        if st.button("🚫 유저 밴"): db['banned'].add(target)
        
        st.divider()
        st.subheader("📈 시장 조작")
        m_st = st.selectbox("종목 선택", list(db['history'].keys()))
        f_pr = st.number_input("고정 가격", value=0.0)
        if st.button("⚡ 가격 고정"): db['forced_price'][m_st] = f_pr
        if st.button("📉 전 종목 대폭락"):
            for k in db['history']: db['history'][k][-1][4] *= 0.1
        
        st.divider()
        st.subheader("🌐 서버 통제")
        db['server_frozen'] = st.toggle("❄️ 거래 동결", value=db['server_frozen'])
        db['chat_mute'] = st.toggle("🔇 채팅 금지", value=db['chat_mute'])

# 6. [메인 화면]
col_m, col_c = st.columns([3, 1])

with col_m:
    st.markdown(f"<h1><span style='color:{user['color']}; text-shadow:0 0 10px {user['color']}'>[{user['title']}]</span> {uid}</h1>", unsafe_allow_html=True)
    st.header(f"💰 자산: ${user['bal']:,.2f}")

    tabs = st.tabs(["📈 거래소", "💎 VIP", "🤝 직거래", "🎰 도박", "🏴‍☠️ 클랜", "🏷️ 칭호", "🔨 경매"])

    with tabs[0]: # 거래소 (주권자 할인 적용)
        sel = st.selectbox("종목", list(db['history'].keys()))
        df = pd.DataFrame(db['history'][sel], columns=['t', 'o', 'h', 'l', 'c'])
        fig = go.Figure(data=[go.Candlestick(x=df['t'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
        fig.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        cp = df['c'].iloc[-1]
        buy_p = cp * 0.9 if user['title'] == "🌌 주권자" else cp
        st.metric(sel, f"${cp:,.2f}", delta="FORCED" if sel in db['forced_price'] else None)
        qty = st.number_input("수량", min_value=1, value=1, key="q_buy")
        if st.button("매수하기") and not db['server_frozen']:
            if user['bal'] >= buy_p * qty:
                user['bal'] -= buy_p * qty
                user['port'][sel] = user['port'].get(sel, 0) + qty
                st.rerun()

    with tabs[1]: # VIP
        st.subheader("💎 VIP 상점")
        if user['bal'] < 100000000: st.error("1억 달러 이상 소지자 전용입니다.")
        else: st.success("VIP 전용 자산 목록 활성화")

    with tabs[2]: # 직거래 (아이템/주식)
        st.subheader("🤝 유저간 직거래")
        tr_to = st.selectbox("거래 유저", [u for u in db['users'] if u != uid])
        tr_item = st.selectbox("내 자산", user['items'] + [f"STOCK:{k} x{v}" for k,v in user['port'].items() if v > 0])
        tr_val = st.number_input("판매가", min_value=0)
        if st.button("제안 전송"):
            db['trade_requests'].append({"seller": uid, "buyer": tr_to, "item": tr_item, "price": tr_val})
        st.divider()
        for i, r in enumerate(db['trade_requests']):
            if r['buyer'] == uid:
                st.warning(f"[{r['seller']}] {r['item']} -> ${r['price']:,}")
                if st.button(f"수락 #{i}"):
                    if user['bal'] >= r['price']:
                        user['bal'] -= r['price']; db['users'][r['seller']]['bal'] += r['price']
                        user['items'].append(r['item']); db['trade_requests'].pop(i); st.rerun()

    with tabs[3]: # 도박 (자산가 확률 보정)
        st.subheader("🎰 카지노")
        bet = st.number_input("배팅액", min_value=1000, max_value=int(user['bal']+1))
        win_p = 0.25 if user['title'] == "💰 자산가" else 0.20
        if st.button(f"배율 4배 도전 (확률 {win_p*100:.0f}%)"):
            if random.random() < win_p:
                user['bal'] += bet * 3; st.balloons()
            else: user['bal'] -= bet; st.error("낙첨")
            st.rerun()

    with tabs[4]: # 클랜 (승인제/초당수익/억만장자보정)
        st.subheader("🏴‍☠️ 클랜 & 패시브 수입")
        if not user['clan']:
            c_nm = st.text_input("클랜 창설")
            if st.button("창설"):
                db['clans'][c_nm] = {"owner": uid, "members": [uid], "donated": {}, "pending": []}
                user['clan'] = c_nm; st.rerun()
            st.divider()
            target_c = st.selectbox("가입 신청", list(db['clans'].keys()))
            if st.button("가입 신청"):
                if uid not in db['clans'][target_c]['pending']:
                    db['clans'][target_c]['pending'].append(uid); st.info("신청됨")
        else:
            clan = db['clans'][user['clan']]
            st.write(f"현재 기부금: ${clan['donated'].get(uid, 0):,}")
            if clan['owner'] == uid:
                for p in clan['pending']:
                    if st.button(f"승인: {p}"):
                        clan['members'].append(p); db['users'][p]['clan'] = user['clan']
                        clan['pending'].remove(p); st.rerun()
            d_val = st.number_input("기부하기", min_value=1000)
            if st.button("기부"):
                if user['bal'] >= d_val:
                    user['bal'] -= d_val; clan['donated'][uid] = clan['donated'].get(uid, 0) + d_val
                    st.rerun()

    with tabs[5]: # 칭호
        st.subheader("🏷️ 칭호 상점")
        for t_nm, d in TITLE_DATA.items():
            if t_nm == "🔥 SYSTEM MASTER": continue
            if st.button(f"{t_nm} (${d['price']:,}) - {d['ability']}"):
                if user['bal'] >= d['price']:
                    user['bal'] -= d['price']; user['title'], user['color'], user['ability'] = t_nm, d['color'], d['ability']
                    st.rerun()

    with tabs[6]: # 경매
        st.subheader("🔨 실시간 경매")
        auc = db['auction']
        st.info(f"품목: {auc['item']} | 최고가: ${auc['bid']:,} ({auc['bidder']})")
        bid_a = st.number_input("입찰가", min_value=auc['bid']+100000)
        if st.button("입찰"):
            if user['bal'] >= bid_a:
                if auc['bidder']: db['users'][auc['bidder']]['bal'] += auc['bid']
                user['bal'] -= bid_a; db['auction'].update({"bid": bid_a, "bidder": uid}); st.rerun()

with col_chat: # 월드 채팅 (제작자 강조)
    st.subheader("💬 월드 채팅")
    c_box = st.container(height=600)
    for m in db['chat'][-30:]:
        u_inf = db['users'].get(m['u'], {"color":"#FFF", "title":"🌱"})
        if u_inf['title'] == "🔥 SYSTEM MASTER":
            chat_h = f"<div style='background:linear-gradient(90deg, rgba(255,0,0,0.2), transparent); border-left:5px solid red; padding:10px; margin:5px 0; box-shadow:0 0 10px red;'><b style='color:red;'>⚡[GOD] {m['u']}</b>: <span style='color:white; font-weight:bold;'>{m['msg']}</span></div>"
        else:
            chat_h = f"<div><b style='color:{u_inf['color']}'>[{u_inf['title']}] {m['u']}</b>: {m['msg']}</div>"
        c_box.markdown(chat_h, unsafe_allow_html=True)
    with st.form("chat_f", clear_on_submit=True):
        m_in = st.text_input("메시지")
        if st.form_submit_button("전송"):
            if not db['chat_mute'] or user['title'] == "🔥 SYSTEM MASTER":
                db['chat'].append({"u": uid, "msg": m_in}); st.rerun()
