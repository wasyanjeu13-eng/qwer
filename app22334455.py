import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# [1. 시스템 초기화 및 보안 설정]
try:
    from streamlit_autorefresh import st_autorefresh
except:
    st.error("필수 패키지 설치 필요: pip install streamlit-autorefresh")
    st.stop()

# 페이지 설정: 다크 모드 최적화 및 넓은 화면
st.set_page_config(page_title="OMEGA GENESIS: ETERNAL EMPIRE", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=2000, key="omega_eternal_empire_final")

# [2. 전역 서버 데이터베이스 - 무소실 캐싱]
@st.cache_resource
def init_empire_db():
    # 주식 및 코인 종목 리스트
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 11)]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE", "🪐_SOLANA"]
    all_tickers = stocks + coins
    
    now = datetime.now()
    # 시세 히스토리 (OHLC 데이터 50개 확보)
    history = {}
    for n in all_tickers:
        history[n] = []
        base_p = 1000.0 if "Corp" in n else 50000.0 if "BIT" in n else 2500.0
        for i in range(50, 0, -1):
            t = now - timedelta(seconds=i*3)
            p = base_p * (1 + random.uniform(-0.05, 0.05))
            history[n].append([t, p, p*1.01, p*0.99, p])
            
    return {
        "history": history,
        "users": {},
        "chat": [],
        "clans": {},
        "lottery_pot": 50000000,
        "last_sync": now,
        "last_payout": time.time(),
        "server_frozen": False,
        "forced_price": {},
        "trade_requests": [],
        "system_logs": [],
        "server_msg": "OMEGA EMPIRE 서버가 가동되었습니다. 모든 기능이 활성화 상태입니다.",
        "auction": {
            "item": "👑 서버 통합 관리권 (30분)",
            "bid": 100000000,
            "bidder": None,
            "end_time": time.time() + 900
        }
    }

db = init_empire_db()

# [3. 아이템 데이터베이스 상세 정의]
ITEM_DETAILS = {
    "⚡ 시세 폭등권": {"desc": "보유 주식 중 1종을 즉시 50% 폭등시킵니다.", "color": "#FF4B4B"},
    "💰 자금 세탁권": {"desc": "현재 총 자산의 25%를 보너스로 획득합니다.", "color": "#2ECC71"},
    "❄️ 시세 동결권": {"desc": "서버 전체 시세 변동을 60초간 강제 중단합니다.", "color": "#3498DB"},
    "🎟️ 경매 역전권": {"desc": "현재 진행 중인 경매 시간을 1분으로 단축시킵니다.", "color": "#F1C40F"},
    "🎁 칭호 랜덤권": {"desc": "무작위 레어 칭호를 획득합니다.", "color": "#9B59B6"}
}

# [4. 핵심 시스템 엔진 - 시세/배당/이벤트]
def run_empire_engine():
    now = datetime.now()
    
    # 4-1. 실시간 시세 변동 로직
    if (now - db['last_sync']).total_seconds() >= 2.0:
        if not db['server_frozen']:
            for n, data in db['history'].items():
                last_p = data[-1][4]
                
                if n in db['forced_price']:
                    new_p = db['forced_price'][n]
                else:
                    # 변동성 계수 (코인은 하이리스크)
                    vol = 0.10 if any(c in n for c in ["BIT", "ETH", "DOGE", "SOL"]) else 0.03
                    change = np.random.normal(0, vol/2) 
                    new_p = max(last_p * (1 + change), 1.0)
                
                # OHLC 데이터 생성
                o = last_p
                c = new_p
                h = max(o, c) * (1 + random.uniform(0, 0.003))
                l = min(o, c) * (1 - random.uniform(0, 0.003))
                
                data.append([now, o, h, l, c])
                db['history'][n] = data[-50:] # 최대 50개 유지
        db['last_sync'] = now
    
    # 4-2. 클랜 초당 배당 시스템
    curr_t = time.time()
    if curr_t - db['last_payout'] >= 1.0:
        for u_id, u_data in db['users'].items():
            if u_data.get('clan'):
                clan = db['clans'].get(u_data['clan'])
                if clan and u_id in clan['donated']:
                    # 기본 배당률 0.012% (칭호에 따른 차등 보너스)
                    bonus = 2.5 if u_data['title'] == "🌌 제국 황제" else 1.5 if u_data['title'] == "👑 억만장자" else 1.0
                    u_data['bal'] += (clan['donated'][u_id] * 0.00012) * bonus
        db['last_payout'] = curr_t

run_empire_engine()

# [5. 보안 인증 및 세션 관리]
if 'uid' not in st.session_state:
    st.title("🌌 OMEGA GENESIS: THE ETERNAL EMPIRE")
    st.subheader("서버에 접속하기 위해 인증이 필요합니다.")
    
    login_tab, sign_tab = st.tabs(["🔐 기존 계정 접속", "📝 신규 시민 등록"])
    
    with sign_tab:
        new_id = st.text_input("희망 아이디", key="s_id").strip()
        new_pw = st.text_input("보안 비밀번호", type="password", key="s_pw")
        if st.button(" empire_register_v1 "):
            if new_id and new_id not in db['users']:
                db['users'][new_id] = {
                    "pw": new_pw, "bal": 5000000.0, 
                    "port": {}, # {종목명: [수량, 평단가]}
                    "items": ["🎁 칭호 랜덤권"], 
                    "title": "🌱 하층민", "color": "#888", "clan": None
                }
                st.success("등록 성공! 접속 탭으로 이동하세요.")
            else: st.error("이미 존재하는 아이디거나 형식이 잘못되었습니다.")
            
    with login_tab:
        lid = st.text_input("아이디", key="l_id")
        lpw = st.text_input("비밀번호", type="password", key="l_pw")
        if st.button(" empire_login_v1 "):
            if lid in db['users'] and db['users'][lid]['pw'] == lpw:
                st.session_state.uid = lid
                st.rerun()
            else: st.error("인증 정보가 일치하지 않습니다.")
    st.stop()

uid = st.session_state.uid
user = db['users'][uid]

# [6. 관리자(제작자) 전능 모드]
with st.sidebar:
    st.title("👑 ADMINISTRATION")
    god_key = st.text_input("GOD_ACCESS_CODE", type="password")
    if god_key == "190844119947201110328":
        user['title'], user['color'] = "🌌 제국 황제", "#E74C3C"
        st.success("MASTER AUTHENTICATED")
        
        with st.expander("🛠 서버 물리 통제"):
            db['server_frozen'] = st.toggle("시세 동결(Freeze)", db['server_frozen'])
            db['server_msg'] = st.text_area("서버 공지 사항", db['server_msg'])
            if st.button("전 유저 강제 배당 ($10M)"):
                for u in db['users'].values(): u['bal'] += 10000000
                
        with st.expander("📈 시장 조작"):
            t_stock = st.selectbox("조작 대상", list(db['history'].keys()))
            f_price = st.number_input("목표 가격", value=0.0)
            if st.button("가격 고정"): db['forced_price'][t_stock] = f_price
            if st.button("고정 해제"): db['forced_price'].pop(t_stock, None)
            
        with st.expander("🎒 자산 및 템 생성"):
            t_user = st.selectbox("대상 유저", list(db['users'].keys()))
            if st.button("1000억 지급"): db['users'][t_user]['bal'] += 100000000000
            if st.button("모든 아이템 지급"): db['users'][t_user]['items'].extend(list(ITEM_DETAILS.keys()))

# [7. 메인 헤더 및 통계]
st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:20px; border-radius:15px; border-bottom: 5px solid {user['color']};">
        <h1 style="margin:0;">OVERLORD: <span style="color:{user['color']};">{user['title']}</span> {uid}</h1>
        <h2 style="color:#2ecc71; margin:0;">Available Balance: ${user['bal']:,.2f}</h2>
    </div>
""", unsafe_allow_html=True)

# 랭킹 상위 5명
st.write("---")
r_cols = st.columns([2, 1])
with r_cols[0]:
    st.info(f"📢 **SERVER NOTICE:** {db['server_msg']}")
with r_cols[1]:
    with st.expander("🏆 실시간 자산 순위"):
        ranking = pd.DataFrame([{"ID": k, "Assets": v['bal'], "Rank": v['title']} for k, v in db['users'].items()])
        if not ranking.empty:
            st.dataframe(ranking.sort_values("Assets", ascending=False).head(5), use_container_width=True)

# [8. 탭 시스템 - 전 기능 무소실 통합]
tabs = st.tabs(["📈 거래소", "📊 포트폴리오", "🤝 P2P거래", "🎒 인벤토리", "🎰 카지노", "🔨 경매장", "🏴‍☠️ 클랜", "🏷️ 상점"])

# --- 탭 1: 거래소 (주식/코인 매매) ---
with tabs[0]:
    st.subheader("📈 Global Market Terminal")
    sel_ticker = st.selectbox("거래 종목 선택", list(db['history'].keys()), key="main_ticker")
    
    h_data = db['history'][sel_ticker]
    df = pd.DataFrame(h_data, columns=['Time', 'Open', 'High', 'Low', 'Close'])
    
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#FF4B4B', decreasing_line_color='#0077FF'
    )])
    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    curr_p = df['Close'].iloc[-1]
    
    c1, c2, c3 = st.columns([1, 1, 1])
    trade_q = c1.number_input("주문 수량", min_value=1, value=1, key="trade_qty")
    
    if c2.button("🚀 전재산 풀매수 (ALL-IN)", use_container_width=True):
        total_q = int(user['bal'] // curr_p)
        if total_q > 0:
            cost = total_q * curr_p
            user['bal'] -= cost
            # 평단가 계산 로직
            old_q, old_avg = user['port'].get(sel_ticker, [0, 0])
            new_q = old_q + total_q
            new_avg = ((old_q * old_avg) + cost) / new_q
            user['port'][sel_ticker] = [new_q, new_avg]
            st.success(f"{sel_ticker} {total_q}주 풀매수 완료!")
            st.rerun()
            
    if c3.button("💰 선택 수량 매수", use_container_width=True):
        cost = trade_q * curr_p
        if user['bal'] >= cost:
            user['bal'] -= cost
            old_q, old_avg = user['port'].get(sel_ticker, [0, 0])
            new_q = old_q + trade_q
            new_avg = ((old_q * old_avg) + cost) / new_q
            user['port'][sel_ticker] = [new_q, new_avg]
            st.rerun()
        else: st.error("잔액이 부족합니다.")

# --- 탭 2: 포트폴리오 (보유 주식/수익률) ---
with tabs[1]:
    st.subheader("📊 My Portfolio Assets")
    if not user['port'] or sum(x[0] for x in user['port'].values()) == 0:
        st.warning("현재 보유 중인 자산이 없습니다.")
    else:
        p_list = []
        for t, val in user['port'].items():
            qty, avg = val
            if qty > 0:
                cur_v = db['history'][t][-1][4]
                total_val = qty * cur_v
                profit = (cur_v - avg) * qty
                roi = ((cur_v - avg) / avg) * 100
                p_list.append({
                    "종목": t, "보유량": f"{qty:,}", "평단가": f"${avg:,.2f}", 
                    "현재가": f"${cur_v:,.2f}", "평가금액": f"${total_val:,.0f}", 
                    "수익": f"${profit:,.0f}", "수익률": f"{roi:+.2f}%"
                })
        
        pdf = pd.DataFrame(p_list)
        st.table(pdf)
        
        st.divider()
        st.write("📥 **부분 매도 시스템**")
        s_col1, s_col2 = st.columns(2)
        sell_ticker = s_col1.selectbox("매도 종목", [t for t, v in user['port'].items() if v[0] > 0])
        sell_q = s_col2.number_input("매도 수량", min_value=1, max_value=int(user['port'].get(sell_ticker, [0])[0]) if sell_ticker else 1)
        
        if st.button("💰 즉시 매도 실행"):
            s_price = db['history'][sell_ticker][-1][4]
            user['bal'] += (s_price * sell_q)
            user['port'][sell_ticker][0] -= sell_q
            st.success(f"{sell_ticker} {sell_q}주 매도 완료!")
            st.rerun()

# --- 탭 3: P2P거래 (유저간 거래) ---
with tabs[2]:
    st.subheader("🤝 P2P Trading Hub")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("📤 제안 보내기")
        t_user = st.selectbox("거래 상대", [u for u in db['users'].keys() if u != uid], key="p_target")
        t_kind = st.radio("제안 종류", ["현금", "아이템"], horizontal=True)
        if t_kind == "현금":
            p_amt = st.number_input("보낼 금액", min_value=1000, max_value=int(user['bal']))
            if st.button("💰 현금 제안 전송"):
                db['trade_requests'].append({"from": uid, "to": t_user, "type": "CASH", "val": p_amt, "id": time.time()})
                st.toast("제안이 전송되었습니다.")
        else:
            if user['items']:
                p_itm = st.selectbox("보낼 아이템", list(set(user['items'])))
                if st.button("🎁 아이템 제안 전송"):
                    db['trade_requests'].append({"from": uid, "to": t_user, "type": "ITEM", "val": p_itm, "id": time.time()})
                    st.toast("제안이 전송되었습니다.")
    
    with col_b:
        st.write("📥 받은 제안 목록")
        my_reqs = [r for r in db['trade_requests'] if r['to'] == uid]
        if not my_reqs: st.info("수신된 제안이 없습니다.")
        for r in my_reqs:
            with st.container(border=True):
                st.write(f"보낸이: {r['from']} | 내용: {r['val']} ({r['type']})")
                if st.button("수락하기", key=f"acc_{r['id']}"):
                    sender = db['users'][r['from']]
                    if r['type'] == "CASH" and sender['bal'] >= r['val']:
                        sender['bal'] -= r['val']; user['bal'] += r['val']
                        db['trade_requests'].remove(r); st.rerun()
                    elif r['type'] == "ITEM" and r['val'] in sender['items']:
                        sender['items'].remove(r['val']); user['items'].append(r['val'])
                        db['trade_requests'].remove(r); st.rerun()
                    else: st.error("거래 조건이 더 이상 충족되지 않습니다.")

# --- 탭 4: 인벤토리 (아이템 사용) ---
with tabs[3]:
    st.subheader("🎒 Empire Inventory")
    if not user['items']:
        st.info("가방이 텅 비었습니다.")
    else:
        for i, itm in enumerate(user['items']):
            with st.container(border=True):
                i_c1, i_c2, i_c3 = st.columns([1.5, 4, 1])
                details = ITEM_DETAILS.get(itm, {"desc": "알 수 없는 아이템", "color": "#FFF"})
                i_c1.markdown(f"<h3 style='color:{details['color']};'>{itm}</h3>", unsafe_allow_html=True)
                i_c2.write(details['desc'])
                if i_c3.button("사용", key=f"use_{itm}_{i}", use_container_width=True):
                    if itm == "💰 자금 세탁권":
                        bonus = user['bal'] * 0.25
                        user['bal'] += bonus; st.success(f"${bonus:,.0f} 세탁 완료!")
                    elif itm == "⚡ 시세 폭등권":
                        if user['port']:
                            target = random.choice([k for k, v in user['port'].items() if v[0] > 0])
                            db['history'][target][-1][4] *= 1.5; st.warning(f"{target} 폭등!")
                        else: st.error("보유 주식이 없습니다.")
                    elif itm == "❄️ 시세 동결권":
                        db['server_frozen'] = True; st.info("시세가 동결되었습니다.")
                    elif itm == "🎁 칭호 랜덤권":
                        titles = ["💎 다이아몬드 수저", "🃏 도박의 신", "🔱 바다의 지배자"]
                        user['title'] = random.choice(titles); st.success(f"새 칭호: {user['title']}")
                    
                    user['items'].pop(i); st.rerun()

# --- 탭 5: 카지노 (로또 및 뽑기) ---
with tabs[4]:
    st.subheader("🎰 The Royal Casino")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown(f"### 🎫 EMPIRE LOTTO")
        st.write(f"현재 누적 잭팟: **${db['lottery_pot']:,.0f}**")
        if st.button("복권 구매 ($500,000)"):
            if user['bal'] >= 500000:
                user['bal'] -= 500000; db['lottery_pot'] += 400000
                if random.random() < 0.01:
                    win = db['lottery_pot']; user['bal'] += win; db['lottery_pot'] = 50000000
                    st.balloons(); st.success(f"축하합니다! 잭팟 당첨: ${win:,.0f}")
                else: st.error("꽝! 다음 기회를 노리세요.")
    with g_col2:
        st.markdown("### 🎁 MYSTERY BOX")
        st.write("랜덤 아이템 1종 획득 가능")
        if st.button("상자 열기 ($10,000,000)"):
            if user['bal'] >= 10000000:
                user['bal'] -= 10000000
                new_itm = random.choice(list(ITEM_DETAILS.keys()))
                user['items'].append(new_itm); st.success(f"아이템 획득: {new_itm}")

# --- 탭 6: 경매장 (실시간 입찰/환불) ---
with tabs[5]:
    st.subheader("🔨 Real-time Auction")
    auc = db['auction']
    t_left = int(auc['end_time'] - time.time())
    if t_left > 0:
        st.warning(f"경매 진행 중: **{auc['item']}**")
        st.write(f"현재 최고 입찰가: **${auc['bid']:,}** | 입찰자: **{auc['bidder'] if auc['bidder'] else '없음'}**")
        st.write(f"남은 시간: {t_left}초")
        bid_val = st.number_input("입찰가 입력 ($)", min_value=int(auc['bid'] * 1.1), step=1000000)
        if st.button("🔨 입찰 실행"):
            if user['bal'] >= bid_val:
                if auc['bidder']: db['users'][auc['bidder']]['bal'] += auc['bid'] # 환불
                user['bal'] -= bid_val
                db['auction'].update({"bid": bid_val, "bidder": uid})
                st.rerun()
    else:
        st.write("현재 경매가 종료되었습니다.")
        if st.button("관리자: 경매 초기화"):
            db['auction'].update({"bid": 100000000, "bidder": None, "end_time": time.time() + 600})

# --- 탭 7: 클랜 (기부 및 배당) ---
with tabs[6]:
    st.subheader("🏴‍☠️ Clan Alliance")
    if not user['clan']:
        c_name = st.text_input("새로운 클랜명")
        if st.button("🏴‍☠️ 클랜 창설 ($50,000,000)"):
            if user['bal'] >= 50000000:
                user['bal'] -= 50000000
                db['clans'][c_name] = {"owner": uid, "donated": {uid: 10000000}}
                user['clan'] = c_name; st.rerun()
    else:
        clan = db['clans'][user['clan']]
        st.success(f"소속 클랜: {user['clan']} | 클랜장: {clan['owner']}")
        d_val = st.number_input("기부할 금액", min_value=1000000)
        if st.button("💰 기부하고 배당률 높이기"):
            if user['bal'] >= d_val:
                user['bal'] -= d_amt
                clan['donated'][uid] = clan['donated'].get(uid, 0) + d_val
                st.rerun()

# --- 탭 8: 상점 (칭호 구매) ---
with tabs[7]:
    st.subheader("🏷️ Title Boutique")
    shop_titles = {"🪙 평민": 10000000, "🥈 은수저": 50000000, "🥇 금수저": 500000000, "💎 다이아 수저": 5000000000}
    for t, p in shop_titles.items():
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{t}** - 가격: ${p:,}")
        if col2.button("구매", key=f"t_buy_{t}"):
            if user['bal'] >= p:
                user['bal'] -= p; user['title'] = t; st.rerun()

# [9. 월드 채팅 및 로그]
st.divider()
st.subheader("💬 World Chatroom")
chat_win = st.container(height=200)
for m in db['chat'][-20:]:
    u_info = db['users'].get(m['u'], {"color": "#FFF", "title": "🌱"})
    chat_win.markdown(f"<span style='color:{u_info['color']};'>[{u_info['title']}] {m['u']}</span>: {m['msg']}", unsafe_allow_html=True)

with st.form("chat_box", clear_on_submit=True):
    msg = st.text_input("메시지를 입력하세요")
    if st.form_submit_button("전송"):
        if msg:
            db['chat'].append({"u": uid, "msg": msg})
            st.rerun()
