import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# [1. 시스템 원격 설정 및 새로고침]
try:
    from streamlit_autorefresh import st_autorefresh
except:
    st.error("설치 필요: pip install streamlit-autorefresh")
    st.stop()

# 페이지 설정
st.set_page_config(page_title="OMEGA GENESIS: OVERLORD", layout="wide")
st_autorefresh(interval=1500, key="omega_eternal_final_fixed")

# [2. 전역 DB - 데이터 무소실 락]
@st.cache_resource
def init_god_db():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 11)]
    coins = ["₿_BTC", "💎_ETH", "🐕_DOGE"]
    all_tickers = stocks + coins
    now = datetime.now()
    # 시세 히스토리 초기화 (데이터 손실 방지를 위해 견고하게 생성)
    history = {}
    for n in all_tickers:
        history[n] = []
        for i in range(30, 0, -1):
            t = now - timedelta(seconds=i*3)
            # [시가, 고가, 저가, 종가]
            history[n].append([t, 1000.0, 1010.0, 990.0, 1000.0])
    
    return {
        "history": history, 
        "users": {}, 
        "chat": [], 
        "clans": {}, 
        "lottery_pot": 10000000, 
        "last_sync": now, 
        "last_payout": time.time(),
        "server_frozen": False, 
        "forced_price": {}, 
        "trade_requests": [],
        "server_msg": "모든 시스템(P2P 거래/경매/인벤토리)이 무결성 검사를 통과했습니다.",
        "auction": {
            "item": "👑 서버 관리 권한 (15분)", 
            "bid": 50000000, 
            "bidder": None, 
            "end_time": time.time() + 600
        }
    }

db = init_god_db()

# [3. 아이템 상세 효과 정의 테이블]
ITEM_LIST = {
    "⚡ 시세 폭등권": "보유 주식 중 무작위 1종을 즉시 50% 폭등시킵니다.",
    "💰 자금 세탁권": "현재 보유 현금의 20%를 추가 보너스로 받습니다.",
    "🎟️ 골든 티켓": "카지노 당첨 확률을 다음 1회에 한해 2배로 높입니다.",
    "❄️ 시세 동결권": "서버 전체의 가격 변동을 30초간 강제로 멈춥니다."
}

# [4. 핵심 시스템 엔진 - 시세 변동 및 배당]
def run_god_engine():
    now = datetime.now()
    
    # 4-1. 시세 변동 엔진 (소실 없는 정밀 연산)
    if (now - db['last_sync']).total_seconds() >= 1.5:
        if not db['server_frozen']:
            for n in db['history']:
                data = db['history'][n]
                last_p = data[-1][4] # 마지막 종가
                
                # 관리자 강제 가격 확인
                if n in db['forced_price']: 
                    new_p = db['forced_price'][n]
                else:
                    # 변동성 부여 (코인과 주식 차별화)
                    vol = 0.07 if any(c in n for c in ["BTC", "ETH", "DOGE"]) else 0.02
                    change = np.random.uniform(-vol, vol)
                    new_p = max(last_p * (1 + change), 1.0)
                
                # OHLC(Open, High, Low, Close) 데이터 생성
                o = last_p
                c = new_p
                h = max(o, c) * (1 + random.uniform(0, 0.005))
                l = min(o, c) * (1 - random.uniform(0, 0.005))
                
                data.append([now, o, h, l, c])
                db['history'][n] = data[-30:] # 최신 30개 데이터 유지
        db['last_sync'] = now
    
    # 4-2. 초당 클랜 수익 배당 엔진
    curr_t = time.time()
    if curr_t - db['last_payout'] >= 1:
        for u_id, u_data in db['users'].items():
            if u_data.get('clan'):
                clan = db['clans'].get(u_data['clan'])
                if clan and u_id in clan['donated']:
                    # 칭호에 따른 배당 보너스 로직
                    mult = 1.0
                    if u_data['title'] == "👑 억만장자": mult = 2.0
                    elif u_data['title'] == "💰 자산가": mult = 1.5
                    
                    # 배당금 지급 (기부금의 0.01% * 배율)
                    u_data['bal'] += (clan['donated'][u_id] * 0.0001) * mult
        db['last_payout'] = curr_t

run_god_engine()

# [5. 로그인 및 계정 관리 시스템]
if 'uid' not in st.session_state:
    st.title("🌌 OMEGA GENESIS - IMMORTAL OVERLORD")
    t1, t2 = st.tabs(["🔒 시스템 로그인", "📝 신규 가입"])
    with t2:
        new_id = st.text_input("아이디 설정", key="reg_id").strip()
        new_pw = st.text_input("비밀번호 설정", type="password", key="reg_pw")
        if st.button("계정 생성"):
            if new_id and new_id not in db['users']:
                db['users'][new_id] = {
                    "pw": new_pw, 
                    "bal": 2000000.0, 
                    "port": {}, 
                    "items": [], 
                    "title": "🌱 개미", 
                    "color": "#AAA", 
                    "clan": None
                }
                st.success(f"[{new_id}] 계정 생성 완료!")
            else: st.error("사용 불가능한 ID입니다.")
    with t1:
        lid = st.text_input("ID", key="login_id")
        lpw = st.text_input("PW", type="password", key="login_pw")
        if st.button("시스템 접속"):
            if lid in db['users'] and db['users'][lid]['pw'] == lpw:
                st.session_state.uid = lid
                st.rerun()
            else: st.error("접속 정보가 올바르지 않습니다.")
    st.stop()

uid = st.session_state.uid
user = db['users'][uid]

# [6. 관리자 사이드바 - 전능한 통제]
with st.sidebar:
    st.header("👑 GOD CONTROL")
    master_key = st.text_input("GOD CODE", type="password")
    if master_key == "190844119947201110328":
        user['title'], user['color'] = "🔥 SYSTEM MASTER", "#FF0000"
        st.success("권능 활성화됨")
        
        st.divider()
        st.subheader("📊 시세 및 서버 통제")
        s_target = st.selectbox("조작 종목", list(db['history'].keys()))
        s_price = st.number_input("고정 가격 설정", value=0.0)
        if st.button("⚡ 즉시 가격 고정"):
            db['forced_price'][s_target] = s_price
        if st.button("🔓 조작 해제"):
            db['forced_price'].pop(s_target, None)
        
        db['server_frozen'] = st.toggle("❄️ 서버 전체 시세 동결", value=db['server_frozen'])
        db['server_msg'] = st.text_input("서버 공지 수정", value=db['server_msg'])
        
        st.divider()
        st.subheader("💰 유저 강제 지원")
        u_target = st.selectbox("지원 대상", list(db['users'].keys()))
        if st.button("🎁 1000억 지급"):
            db['users'][u_target]['bal'] += 100000000000
            st.toast(f"{u_target}에게 1000억 원을 지급했습니다.")
        if st.button("📦 풀 아이템 지급"):
            db['users'][u_target]['items'].extend(list(ITEM_LIST.keys()))

# [7. 상단 대시보드 및 실시간 랭킹]
st.markdown(f"<div style='background:rgba(255,0,0,0.1); padding:12px; border-radius:12px; border-left:8px solid red; font-size:18px;'><b>[ADMIN MESSAGE]</b> {db['server_msg']}</div>", unsafe_allow_html=True)

col_u, col_r = st.columns([1, 1])
with col_u:
    st.markdown(f"<h1 style='margin-bottom:0;'> <span style='color:{user['color']};'>[{user['title']}]</span> {uid}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:#2ecc71;'>보유 자산: ${user['bal']:,.2f}</h2>", unsafe_allow_html=True)
with col_r:
    st.write("🏆 **REAL-TIME RANKING TOP 5**")
    rank_list = []
    for k, v in db['users'].items():
        rank_list.append({"ID": k, "자산": v['bal'], "칭호": v['title']})
    rank_df = pd.DataFrame(rank_list)
    if not rank_df.empty:
        st.dataframe(rank_df.sort_values("자산", ascending=False).head(5), use_container_width=True)

# [8. 통합 기능 시스템 (탭 인터페이스)]
t_market, t_p2p, t_inv, t_gamble, t_auc, t_clan, t_shop = st.tabs([
    "📈 거래소", "🤝 P2P거래", "🎒 인벤토리", "🎰 카지노", "🔨 경매장", "🏴‍☠️ 클랜", "🏷️ 상점"
])

# --- 탭 1: 거래소 ---
with t_market:
    sel = st.selectbox("종목 선택", list(db['history'].keys()), key="market_select")
    df = pd.DataFrame(db['history'][sel], columns=['t', 'o', 'h', 'l', 'c'])
    
    # 캔들스틱 차트 생성
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['t'], open=df['o'], high=df['h'], low=df['l'], close=df['c'],
        increasing_line_color='#FF4B4B', decreasing_line_color='#0077FF'
    )])
    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    
    curr_price = df['c'].iloc[-1]
    st.subheader(f"현재가: ${curr_price:,.2f}")
    
    c1, c2, c3 = st.columns([1, 1, 1])
    buy_q = c1.number_input("거래 수량", min_value=1, value=1, key="main_buy_q")
    
    if c2.button("🚀 전 재산 풀매수 (ALL-IN)"):
        max_q = int(user['bal'] // curr_price)
        if max_q > 0:
            user['bal'] -= (curr_price * max_q)
            user['port'][sel] = user['port'].get(sel, 0) + max_q
            st.success(f"{sel} {max_q}주 풀매수 완료!")
            st.rerun()
    
    if c3.button("💰 선택 수량 매도"):
        if user['port'].get(sel, 0) >= buy_q:
            user['bal'] += (curr_price * buy_q)
            user['port'][sel] -= buy_q
            st.info(f"{sel} {buy_q}주 매도 완료.")
            st.rerun()
        else: st.error("보유 수량이 부족합니다.")

# --- 탭 2: P2P 거래 ---
with t_p2p:
    st.subheader("🤝 유저 간 1:1 개인 거래소")
    p1, p2 = st.columns(2)
    with p1:
        st.write("📤 거래 제안 보내기")
        t_user = st.selectbox("거래 대상 선택", [u for u in db['users'].keys() if u != uid], key="p2p_target")
        t_mode = st.radio("종류 선택", ["현금(Cash)", "아이템(Item)"], key="p2p_mode")
        
        if t_mode == "현금(Cash)":
            amt = st.number_input("송금액", min_value=1000, max_value=int(user['bal']), key="p2p_amt")
            if st.button("거래 제안 전송"):
                db['trade_requests'].append({"from": uid, "to": t_user, "type": "CASH", "val": amt, "id": time.time()})
                st.toast(f"{t_user}에게 거래 제안을 보냈습니다.")
        else:
            if user['items']:
                itm = st.selectbox("보낼 아이템 선택", list(set(user['items'])), key="p2p_itm")
                if st.button("아이템 거래 제안"):
                    db['trade_requests'].append({"from": uid, "to": t_user, "type": "ITEM", "val": itm, "id": time.time()})
                    st.toast("아이템 제안 완료.")
            else: st.warning("보유한 아이템이 없습니다.")

    with p2:
        st.write("📥 나에게 온 거래 제안")
        my_reqs = [r for r in db['trade_requests'] if r['to'] == uid]
        if not my_reqs: st.info("수신된 거래 제안이 없습니다.")
        for r in my_reqs:
            with st.container(border=True):
                st.write(f"보낸이: **{r['from']}**")
                st.write(f"내용: {r['val']} ({r['type']})")
                if st.button(f"거래 수락", key=f"p2p_acc_{r['id']}"):
                    sender = db['users'][r['from']]
                    if r['type'] == "CASH":
                        if sender['bal'] >= r['val']:
                            sender['bal'] -= r['val']
                            user['bal'] += r['val']
                            db['trade_requests'].remove(r)
                            st.rerun()
                        else: st.error("상대방의 잔액이 부족합니다.")
                    else:
                        if r['val'] in sender['items']:
                            sender['items'].remove(r['val'])
                            user['items'].append(r['val'])
                            db['trade_requests'].remove(r)
                            st.rerun()
                        else: st.error("상대방이 아이템을 더 이상 보유하고 있지 않습니다.")

# --- 탭 3: 인벤토리 ---
with t_inv:
    st.subheader("🎒 나의 인벤토리")
    if not user['items']:
        st.info("가방이 비어있습니다. 카지노에서 아이템을 획득하세요!")
    else:
        for i, item in enumerate(user['items']):
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 5, 1.5])
                c1.markdown(f"### **{item}**")
                c2.write(ITEM_LIST.get(item, "특수 효과 없음"))
                if c3.button("아이템 사용", key=f"item_use_{i}"):
                    if item == "💰 자금 세탁권":
                        bonus = user['bal'] * 0.2
                        user['bal'] += bonus
                        st.success(f"자금 세탁 성공! ${bonus:,.0f} 획득.")
                    elif item == "⚡ 시세 폭등권":
                        if user['port']:
                            target = random.choice(list(user['port'].keys()))
                            db['history'][target][-1][4] *= 1.5
                            st.warning(f"보유 종목 [{target}]이(가) 50% 폭등했습니다!")
                        else: st.error("보유 중인 주식이 없어 효과가 무효화되었습니다.")
                    elif item == "❄️ 시세 동결권":
                        db['server_frozen'] = True
                        st.info("관리자 권한을 해킹하여 시세를 30초간 동결했습니다.")
                    
                    user['items'].pop(i) # 사용 후 삭제
                    st.rerun()

# --- 탭 4: 카지노 ---
with t_gamble:
    st.subheader("🎰 지하 카지노")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"🎫 **로또 누적 당첨금: ${db['lottery_pot']:,.0f}**")
        if st.button("복권 구매 ($100,000)"):
            if user['bal'] >= 100000:
                user['bal'] -= 100000
                db['lottery_pot'] += 80000
                if random.random() < 0.01: # 1% 확률
                    win_amt = db['lottery_pot']
                    user['bal'] += win_amt
                    db['lottery_pot'] = 10000000
                    st.balloons()
                    st.success(f"🎊 대박! 로또 당첨! ${win_amt:,.0f}를 얻었습니다!")
                else: st.error("꽝! 다음 기회에...")
    with col2:
        st.write("🎁 **랜덤 아이템 박스**")
        if st.button("박스 개봉 ($5,000,000)"):
            if user['bal'] >= 5000000:
                user['bal'] -= 5000000
                new_item = random.choice(list(ITEM_LIST.keys()))
                user['items'].append(new_item)
                st.success(f"[{new_item}] 아이템을 획득했습니다!")
            else: st.error("현금이 부족합니다.")

# --- 탭 5: 경매장 ---
with t_auc:
    st.subheader("🔨 실시간 라이브 경매")
    auc = db['auction']
    t_left = int(auc['end_time'] - time.time())
    
    if t_left > 0:
        st.warning(f"현재 품목: **{auc['item']}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 최고가", f"${auc['bid']:,}")
        c2.metric("최고 입찰자", f"{auc['bidder'] if auc['bidder'] else '없음'}")
        c3.metric("남은 시간", f"{t_left}초")
        
        bid_input = st.number_input("입찰 금액 입력 (현재가보다 10% 이상 높아야 함)", min_value=int(auc['bid'] * 1.1), step=1000000)
        if st.button("🔨 입찰하기"):
            if user['bal'] >= bid_input:
                # [핵심] 이전 입찰자 환불 로직
                if auc['bidder']:
                    db['users'][auc['bidder']]['bal'] += auc['bid']
                
                user['bal'] -= bid_input
                db['auction'].update({
                    "bid": bid_input,
                    "bidder": uid
                })
                st.success("입찰에 성공했습니다!")
                st.rerun()
            else: st.error("잔액이 부족합니다.")
    else:
        st.write("진행 중인 경매가 없습니다.")
        if st.button("새 경매 등록 (관리자 전용)"):
            db['auction'].update({
                "item": "💎 신의 은총 (자산 2배권)",
                "bid": 100000000,
                "bidder": None,
                "end_time": time.time() + 300
            })

# --- 탭 6: 클랜 ---
with t_clan:
    st.subheader("🏴‍☠️ 클랜 연합")
    if not user['clan']:
        c_name = st.text_input("새로운 클랜 이름").strip()
        if st.button("클랜 창설 ($20,000,000)"):
            if len(c_name) > 1 and user['bal'] >= 20000000:
                user['bal'] -= 20000000
                db['clans'][c_name] = {"owner": uid, "donated": {uid: 10000000}}
                user['clan'] = c_name
                st.success(f"[{c_name}] 클랜을 창설했습니다!")
                st.rerun()
    else:
        clan = db['clans'][user['clan']]
        st.info(f"🚩 소속 클랜: {user['clan']} | 클랜장: {clan['owner']}")
        st.write("기부한 금액에 따라 매초 배당금이 지급됩니다.")
        
        d_amt = st.number_input("클랜 기부액", min_value=100000, step=100000)
        if st.button("💰 기부하기"):
            if user['bal'] >= d_amt:
                user['bal'] -= d_amt
                clan['donated'][uid] = clan['donated'].get(uid, 0) + d_amt
                st.success(f"클랜에 ${d_amt:,.0f}를 기부했습니다.")
                st.rerun()

# --- 탭 7: 칭호 상점 ---
with t_shop:
    st.subheader("🏷️ 명예 칭호 구매")
    shop_items = {
        "🐜 개미 대장": 10000000,
        "💰 자산가": 100000000,
        "👑 억만장자": 1000000000,
        "🌌 주권자": 10000000000
    }
    for t_name, t_price in shop_items.items():
        col_t, col_p, col_b = st.columns([2, 3, 1.5])
        col_t.write(f"### {t_name}")
        col_p.write(f"가격: ${t_price:,}")
        if col_b.button("구매하기", key=f"buy_title_{t_name}"):
            if user['bal'] >= t_price:
                user['bal'] -= t_price
                user['title'] = t_name
                # 칭호에 따른 색상 변경
                if t_name == "🌌 주권자": user['color'] = "#9b59b6"
                elif t_name == "👑 억만장자": user['color'] = "#f1c40f"
                elif t_name == "💰 자산가": user['color'] = "#3498db"
                st.success(f"[{t_name}] 칭호를 획득했습니다!")
                st.rerun()

# [9. 월드 채팅 시스템]
st.divider()
st.subheader("💬 REAL-TIME WORLD CHAT")
chat_container = st.container(height=200)
for m in db['chat'][-15:]:
    u_info = db['users'].get(m['u'], {"color": "#FFF", "title": "🌱"})
    chat_container.markdown(f"<span style='color:{u_info['color']};'>[{u_info['title']}] <b>{m['u']}</b></span>: {m['msg']}", unsafe_allow_html=True)

with st.form("chat_input", clear_on_submit=True):
    msg = st.text_input("메시지를 입력하세요 (관리자는 공지 권한)")
    if st.form_submit_button("전송"):
        if msg:
            db['chat'].append({"u": uid, "msg": msg})
            st.rerun()
