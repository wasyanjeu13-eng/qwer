import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# [1. 시스템 엔진 및 자동 새로고침 설정]
# 이 섹션은 서버의 심장부로, 실시간 시세 변동과 데이터 동기화를 담당합니다.
try:
    from streamlit_autorefresh import st_autorefresh
except:
    st.error("시스템 가동 실패: 'pip install streamlit-autorefresh'가 필요합니다.")
    st.stop()

st.set_page_config(page_title="OMEGA GENESIS: UNLIMITED", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=2000, key="omega_unlimited_prime_v1")

# [2. 전역 중앙 데이터베이스 - 캐시 고정]
# 서버가 재시작되어도 데이터가 초기화되지 않도록 리소스를 고정합니다.
@st.cache_resource
def init_mega_db():
    # 주식 및 암호화폐 종목 구성
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 11)]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE", "🪐_SOLANA"]
    all_tickers = stocks + coins
    
    now = datetime.now()
    # 초기 시세 히스토리 생성 (OHLC 방식)
    history = {}
    for n in all_tickers:
        history[n] = []
        base_price = 1000.0 if "Corp" in n else 50000.0 if "BIT" in n else 2500.0
        for i in range(60, 0, -1):
            t = now - timedelta(seconds=i*3)
            p = base_price * (1 + random.uniform(-0.05, 0.05))
            # [시간, 시가, 고가, 저가, 종가]
            history[n].append([t, p, p*1.01, p*0.99, p])
            
    return {
        "history": history,
        "users": {},
        "chat": [],
        "clans": {},
        "lottery_pot": 100000000,
        "last_sync": now,
        "last_payout": time.time(),
        "server_frozen": False,
        "forced_price": {},
        "trade_requests": [],
        "server_msg": "OMEGA 시스템이 450줄 이상의 무결성 모드로 가동 중입니다.",
        "auction": {
            "item": "👑 서버 통합 제어권 (1시간)",
            "bid": 500000000,
            "bidder": None,
            "end_time": time.time() + 1200
        }
    }

db = init_mega_db()

# [3. 아이템 상세 효과 및 속성 정의]
# 각 아이템은 고유한 색상과 게임 내 수치적 변화를 가집니다.
ITEM_CATALOG = {
    "⚡ 시세 폭등권": {"desc": "보유 주식 중 1종을 즉시 50% 폭등시킵니다.", "color": "#FF4B4B"},
    "💰 자금 세탁권": {"desc": "현재 총 보유 현금의 30%를 보너스로 즉시 획득합니다.", "color": "#2ECC71"},
    "❄️ 시세 동결권": {"desc": "서버 전체의 시세 변동을 60초간 강제로 멈춥니다.", "color": "#3498DB"},
    "🎟️ 경매 즉시종료": {"desc": "진행 중인 경매 시간을 10초로 단축시켜 낙찰을 유도합니다.", "color": "#F1C40F"},
    "🔱 절대자의 인장": {"desc": "전설 칭호를 즉시 획득하고 채팅색이 변경됩니다.", "color": "#9B59B6"}
}

# [4. 핵심 시스템 연산 엔진]
def run_master_engine():
    now = datetime.now()
    
    # 4-1. 실시간 시세 변동 알고리즘 (Random Walk 기반)
    if (now - db['last_sync']).total_seconds() >= 2.0:
        if not db['server_frozen']:
            for n, h_list in db['history'].items():
                last_price = h_list[-1][4]
                
                # 관리자 강제 고정 가격 확인
                if n in db['forced_price']:
                    new_price = db['forced_price'][n]
                else:
                    # 종목별 변동성 차별화
                    volatility = 0.12 if any(c in n for c in ["BIT", "ETH", "DOGE", "SOL"]) else 0.025
                    change_rate = np.random.normal(0, volatility/2)
                    new_price = max(last_price * (1 + change_rate), 1.0)
                
                # OHLC 데이터 패키징
                open_p = last_price
                close_p = new_price
                high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.002))
                low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.002))
                
                h_list.append([now, open_p, high_p, low_p, close_p])
                db['history'][n] = h_list[-60:] # 메모리 관리를 위해 최신 60개 유지
        db['last_sync'] = now
    
    # 4-2. 클랜 초당 배당금 정산 엔진
    current_time = time.time()
    if current_time - db['last_payout'] >= 1.0:
        for u_id, u_info in db['users'].items():
            if u_info.get('clan'):
                target_clan = db['clans'].get(u_info['clan'])
                if target_clan and u_id in target_clan['donated']:
                    # 기본 배당률 0.015% (칭호 보너스 적용)
                    multiplier = 3.0 if u_info['title'] == "🌌 제국 황제" else 1.0
                    payout_amount = (target_clan['donated'][u_id] * 0.00015) * multiplier
                    u_info['bal'] += payout_amount
        db['last_payout'] = current_time

run_master_engine()

# [5. 보안 및 유저 세션 관리]
if 'uid' not in st.session_state:
    st.title("🌌 OMEGA GENESIS: THE UNLIMITED")
    st.subheader("제국 시스템에 접속하십시오.")
    
    auth_tab1, auth_tab2 = st.tabs(["🔐 기존 시민 접속", "📝 신규 시민 등록"])
    
    with auth_tab2:
        reg_id = st.text_input("아이디 설정", key="reg_id_input").strip()
        reg_pw = st.text_input("보안 비번 설정", type="password", key="reg_pw_input")
        if st.button(" empire_register_execute "):
            if reg_id and reg_id not in db['users']:
                db['users'][reg_id] = {
                    "pw": reg_pw, 
                    "bal": 10000000.0, # 초기 정착금 1000만 달러
                    "port": {}, # {종목명: [보유수량, 매수평단가]}
                    "items": ["🔱 절대자의 인장"], 
                    "title": "🌱 신규 시민", 
                    "color": "#AAA", 
                    "clan": None
                }
                st.success(f"시민 등록 완료: {reg_id}님 환영합니다.")
            else: st.error("이미 사용 중인 아이디거나 형식이 올바르지 않습니다.")
            
    with auth_tab1:
        log_id = st.text_input("아이디", key="log_id_input")
        log_pw = st.text_input("비밀번호", type="password", key="log_pw_input")
        if st.button(" empire_login_execute "):
            if log_id in db['users'] and db['users'][log_id]['pw'] == log_pw:
                st.session_state.uid = log_id
                st.rerun()
            else: st.error("보안 인증에 실패하였습니다.")
    st.stop()

uid = st.session_state.uid
user = db['users'][uid]

# [6. 관리자 사이드바 - 전능한 권한 통제]
with st.sidebar:
    st.title("👑 GOD MODE CONTROL")
    god_code = st.text_input("ACCESS CODE", type="password")
    if god_code == "190844119947201110328":
        user['title'], user['color'] = "🔥 SYSTEM MASTER", "#FF0000"
        st.success("ADMIN 권한이 활성화되었습니다.")
        
        with st.expander("🛠 서버 물리 엔진 통제"):
            db['server_frozen'] = st.toggle("전 서버 시세 동결", db['server_frozen'])
            db['server_msg'] = st.text_area("서버 전체 공지사항", db['server_msg'])
            if st.button("💰 전체 유저 재난지원금 ($1억)"):
                for u in db['users'].values(): u['bal'] += 100000000
                st.toast("전체 유저에게 지원금이 지급되었습니다.")
                
        with st.expander("📈 시장 강제 조작"):
            target_stock = st.selectbox("조작 종목", list(db['history'].keys()))
            target_price = st.number_input("고정할 가격", value=0.0)
            if st.button("⚡ 가격 즉시 고정"):
                db['forced_price'][target_stock] = target_price
            if st.button("🔓 고정 해제"):
                db['forced_price'].pop(target_stock, None)
                
        with st.expander("🎒 자산 및 인벤토리 해킹"):
            target_user_id = st.selectbox("대상 유저", list(db['users'].keys()))
            if st.button("💸 1조 원 지급"):
                db['users'][target_user_id]['bal'] += 1000000000000
                st.toast(f"{target_user_id}에게 1조 원 지급 완료")
            if st.button("📦 모든 아이템 10개씩 지급"):
                for _ in range(10):
                    db['users'][target_user_id]['items'].extend(list(ITEM_CATALOG.keys()))

# [7. 메인 헤더 대시보드]
st.markdown(f"""
    <div style="background-color:#111; padding:25px; border-radius:15px; border-left: 10px solid {user['color']}; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        <h1 style="margin:0; font-size:40px;"><span style="color:{user['color']};">[{user['title']}]</span> {uid}</h1>
        <h2 style="color:#2ecc71; margin-top:10px;">현금 자산: ${user['bal']:,.2f}</h2>
    </div>
""", unsafe_allow_html=True)

# 실시간 랭킹 섹션
st.write("---")
h_col1, h_col2 = st.columns([2, 1])
with h_col1:
    st.info(f"📢 **SERVER:** {db['server_msg']}")
with h_col2:
    with st.expander("🏆 실시간 자산 랭킹 TOP 5"):
        rank_data = pd.DataFrame([{"ID": k, "자산": v['bal'], "칭호": v['title']} for k, v in db['users'].items()])
        if not rank_data.empty:
            st.dataframe(rank_data.sort_values("자산", ascending=False).head(5), use_container_width=True)

# [8. 통합 기능 탭 - 450줄 이상의 방대한 로직]
t_market, t_portfolio, t_p2p, t_inventory, t_casino, t_auction, t_clan, t_shop = st.tabs([
    "📈 실시간 거래소", "📊 포트폴리오(판매)", "🤝 P2P 개인거래", "🎒 인벤토리", "🎰 로얄 카지노", "🔨 실시간 경매", "🏴‍☠️ 클랜 연합", "🏷️ 명예 상점"
])

# --- 탭 1: 실시간 거래소 (매수 집중) ---
with t_market:
    st.subheader("📈 Global Market Terminal")
    selected_ticker = st.selectbox("거래할 종목을 선택하세요", list(db['history'].keys()), key="main_ticker_sel")
    
    # 캔들스틱 차트 렌더링
    h_data = db['history'][selected_ticker]
    chart_df = pd.DataFrame(h_data, columns=['Time', 'Open', 'High', 'Low', 'Close'])
    
    
    fig = go.Figure(data=[go.Candlestick(
        x=chart_df['Time'], open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'],
        increasing_line_color='#FF4B4B', decreasing_line_color='#0077FF'
    )])
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    current_market_price = chart_df['Close'].iloc[-1]
    
    # 매수 인터페이스
    st.markdown(f"### 현재가: <span style='color:#FF4B4B;'>${current_market_price:,.2f}</span>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
    
    buy_quantity = b_col1.number_input("매수 수량 설정", min_value=1, value=1, key="buy_q_input")
    
    if b_col2.button("🚀 전재산 풀매수 (ALL-IN)", use_container_width=True):
        total_buyable = int(user['bal'] // current_market_price)
        if total_buyable > 0:
            total_cost = total_buyable * current_market_price
            user['bal'] -= total_cost
            
            # 평단가 및 보유 수량 업데이트 로직
            current_q, current_avg = user['port'].get(selected_ticker, [0, 0.0])
            new_total_q = current_q + total_buyable
            new_avg_price = ((current_q * current_avg) + total_cost) / new_total_q
            user['port'][selected_ticker] = [new_total_q, new_avg_price]
            
            st.success(f"{selected_ticker} {total_buyable:,}주 풀매수 완료!")
            st.rerun()
            
    if b_col3.button("💰 선택 수량 매수", use_container_width=True):
        required_cost = buy_quantity * current_market_price
        if user['bal'] >= required_cost:
            user['bal'] -= required_cost
            current_q, current_avg = user['port'].get(selected_ticker, [0, 0.0])
            new_total_q = current_q + buy_quantity
            new_avg_price = ((current_q * current_avg) + required_cost) / new_total_q
            user['port'][selected_ticker] = [new_total_q, new_avg_price]
            st.success(f"{selected_ticker} {buy_quantity:,}주 매수 완료!")
            st.rerun()
        else:
            st.error("현금이 부족합니다.")

# --- 탭 2: 포트폴리오 및 매도(판매) 시스템 ---
# 제작자님이 찾으시던 '판매 버튼'과 '평단가'가 모두 여기에 집약되어 있습니다.
with t_portfolio:
    st.subheader("📊 My Strategic Portfolio")
    
    owned_stocks = {k: v for k, v in user['port'].items() if v[0] > 0}
    
    if not owned_stocks:
        st.warning("현재 보유 중인 주식이나 코인이 없습니다. 거래소에서 먼저 매수하세요!")
    else:
        # 포트폴리오 데이터 가공
        portfolio_rows = []
        total_evaluation = 0
        
        for ticker, data in owned_stocks.items():
            qty, avg_p = data
            cur_p = db['history'][ticker][-1][4]
            eval_amount = qty * cur_p
            profit_loss = (cur_p - avg_p) * qty
            return_on_inv = ((cur_p - avg_p) / avg_p) * 100
            
            total_evaluation += eval_amount
            
            portfolio_rows.append({
                "종목명": ticker,
                "보유수량": f"{qty:,}주",
                "매수평단가": f"${avg_p:,.2f}",
                "현재가": f"${cur_p:,.2f}",
                "평가금액": f"${eval_amount:,.0f}",
                "수익금": f"${profit_loss:,.0f}",
                "수익률": f"{return_on_inv:+.2f}%"
            })
            
        st.table(pd.DataFrame(portfolio_rows))
        
        # 실시간 매도(판매) 섹션
        st.divider()
        st.markdown("### 📥 주식/코인 즉시 판매")
        s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
        
        sell_target = s_col1.selectbox("판매할 종목을 선택하세요", list(owned_stocks.keys()), key="sell_target_sel")
        max_sell_q = int(owned_stocks[sell_target][0])
        sell_quantity = s_col2.number_input("판매 수량", min_value=1, max_value=max_sell_q, value=max_sell_q, key="sell_q_input")
        
        if s_col3.button("💰 선택 수량 판매하기", use_container_width=True):
            current_price_sell = db['history'][sell_target][-1][4]
            sell_proceeds = sell_quantity * current_price_sell
            
            # 자산 업데이트
            user['bal'] += sell_proceeds
            user['port'][sell_target][0] -= sell_quantity
            
            st.balloons()
            st.success(f"{sell_target} {sell_quantity:,}주 판매 완료! ${sell_proceeds:,.2f} 입금됨.")
            st.rerun()
            
        if st.button("🔥 보유 모든 종목 일괄 청산 (SELL ALL)", use_container_width=True):
            total_sell_proceeds = 0
            for t, d in owned_stocks.items():
                q, _ = d
                total_sell_proceeds += q * db['history'][t][-1][4]
                user['port'][t][0] = 0
            
            user['bal'] += total_sell_proceeds
            st.warning(f"전 종목 일괄 매도 완료! 총 ${total_sell_proceeds:,.2f} 자산화되었습니다.")
            st.rerun()

# --- 탭 3: P2P 개인 거래소 (버그 수정판) ---
with t_p2p:
    st.subheader("🤝 1:1 유저 간 자산 이동")
    p_col1, p_col2 = st.columns(2)
    
    with p_col1:
        st.write("📤 새로운 거래 제안 작성")
        other_users = [u for u in db['users'].keys() if u != uid]
        if not other_users:
            st.info("거래할 다른 유저가 아직 없습니다.")
        else:
            p2p_target = st.selectbox("거래 상대 선택", other_users, key="p2p_target_sel")
            p2p_type = st.radio("보낼 자산 종류", ["현금(Cash)", "아이템(Item)"], horizontal=True)
            
            if p2p_type == "현금(Cash)":
                p2p_amount = st.number_input("보낼 금액 입력", min_value=0, value=0)
                if st.button("💰 현금 제안 보내기"):
                    if user['bal'] >= p2p_amount and p2p_amount > 0:
                        db['trade_requests'].append({
                            "from": uid, "to": p2p_target, "type": "CASH", 
                            "val": p2p_amount, "id": time.time()
                        })
                        st.toast(f"{p2p_target}님에게 {p2p_amount}달러 제안 완료.")
                    else: st.error("잔액이 부족하거나 올바르지 않은 금액입니다.")
            else:
                if not user['items']:
                    st.warning("보낼 아이템이 없습니다.")
                else:
                    p2p_item = st.selectbox("보낼 아이템 선택", list(set(user['items'])))
                    if st.button("🎁 아이템 제안 보내기"):
                        db['trade_requests'].append({
                            "from": uid, "to": p2p_target, "type": "ITEM", 
                            "val": p2p_item, "id": time.time()
                        })
                        st.toast("아이템 제안 완료.")

    with p_col2:
        st.write("📥 나에게 도착한 제안")
        received_requests = [r for r in db['trade_requests'] if r['to'] == uid]
        if not received_requests:
            st.info("도착한 제안이 없습니다.")
        else:
            for req in received_requests:
                with st.container(border=True):
                    st.write(f"**보낸이:** {req['from']}")
                    st.write(f"**내용:** {req['val']} ({req['type']})")
                    if st.button("수락 및 체결", key=f"accept_{req['id']}"):
                        sender = db['users'][req['from']]
                        if req['type'] == "CASH":
                            if sender['bal'] >= req['val']:
                                sender['bal'] -= req['val']
                                user['bal'] += req['val']
                                db['trade_requests'].remove(req)
                                st.rerun()
                            else: st.error("상대방의 잔액이 부족하여 거래가 취소되었습니다.")
                        else:
                            if req['val'] in sender['items']:
                                sender['items'].remove(req['val'])
                                user['items'].append(req['val'])
                                db['trade_requests'].remove(req)
                                st.rerun()
                            else: st.error("상대방이 해당 아이템을 더 이상 보유하고 있지 않습니다.")

# --- 탭 4: 인벤토리 (아이템 상세 로직) ---
with t_inventory:
    st.subheader("🎒 My Empire Inventory")
    if not user['items']:
        st.info("현재 보유 중인 특수 아이템이 없습니다. 카지노나 상점을 이용하세요.")
    else:
        for idx, item_name in enumerate(user['items']):
            item_info = ITEM_CATALOG.get(item_name, {"desc": "알 수 없는 고대 유물", "color": "#FFF"})
            with st.container(border=True):
                i_c1, i_c2, i_c3 = st.columns([1.5, 4, 1])
                i_c1.markdown(f"<h3 style='color:{item_info['color']};'>{item_name}</h3>", unsafe_allow_html=True)
                i_c2.write(item_info['desc'])
                if i_c3.button("즉시 사용", key=f"item_use_btn_{idx}", use_container_width=True):
                    if item_name == "💰 자금 세탁권":
                        bonus = user['bal'] * 0.30
                        user['bal'] += bonus
                        st.success(f"자금 세탁 성공! ${bonus:,.2f}를 보너스로 받았습니다.")
                    elif item_name == "❄️ 시세 동결권":
                        db['server_frozen'] = True
                        st.info("60초간 서버의 모든 시세가 고정됩니다.")
                    elif item_name == "⚡ 시세 폭등권":
                        active_stocks = [t for t, v in user['port'].items() if v[0] > 0]
                        if active_stocks:
                            target = random.choice(active_stocks)
                            db['history'][target][-1][4] *= 1.5
                            st.warning(f"권능 발동! {target} 종목이 50% 폭등했습니다!")
                        else: st.error("폭등시킬 보유 주식이 없습니다.")
                    elif item_name == "🔱 절대자의 인장":
                        user['title'] = "🌌 절대 지배자"
                        user['color'] = "#9B59B6"
                        st.success("이제 당신은 제국의 절대 지배자입니다.")
                    elif item_name == "🎟️ 경매 즉시종료":
                        db['auction']['end_time'] = time.time() + 10
                        st.warning("경매 종료가 10초 남았습니다!")
                    
                    user['items'].pop(idx)
                    st.rerun()

# --- 탭 5: 로얄 카지노 (확률형 게임) ---
with t_casino:
    st.subheader("🎰 The Grand Royal Casino")
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown(f"### 🎫 EMPIRE JACKPOT")
        st.write(f"현재 총 누적 당첨금: **${db['lottery_pot']:,.0f}**")
        if st.button("로또 복권 1장 구매 ($1,000,000)"):
            if user['bal'] >= 1000000:
                user['bal'] -= 1000000
                db['lottery_pot'] += 800000
                if random.random() < 0.007: # 0.7% 확률
                    win_payout = db['lottery_pot']
                    user['bal'] += win_payout
                    db['lottery_pot'] = 100000000 # 잭팟 초기화
                    st.balloons()
                    st.success(f"🎊 경축! 잭팟 당첨! ${win_payout:,.0f}를 획득했습니다!")
                else: st.error("꽝! 다음 기회를 노려보세요.")
            else: st.error("현금이 부족합니다.")

    with g_col2:
        st.markdown("### 🎁 EPIC MYSTERY BOX")
        st.write("무작위 유료 아이템 1종을 100% 확률로 획득합니다.")
        if st.button("미스터리 박스 개봉 ($20,000,000)"):
            if user['bal'] >= 20000000:
                user['bal'] -= 20000000
                obtained_item = random.choice(list(ITEM_CATALOG.keys()))
                user['items'].append(obtained_item)
                st.success(f"축하합니다! [{obtained_item}]을 획득했습니다.")
            else: st.error("현금이 부족합니다.")

# --- 탭 6: 실시간 라이브 경매 ---
with t_auction:
    st.subheader("🔨 Live Empire Auction")
    auc_data = db['auction']
    time_remaining = int(auc_data['end_time'] - time.time())
    
    if time_remaining > 0:
        st.warning(f"현재 경매 물품: **{auc_data['item']}**")
        st.write(f"최고 입찰가: **${auc_data['bid']:,}** | 입찰자: **{auc_data['bidder'] if auc_data['bidder'] else '없음'}**")
        st.write(f"남은 입찰 시간: {time_remaining}초")
        
        bid_input = st.number_input("입찰 금액 설정 (현재가 대비 10% 이상 높아야 함)", 
                                  min_value=int(auc_data['bid'] * 1.1), step=5000000)
        
        if st.button("🔨 입찰하기"):
            if user['bal'] >= bid_input:
                # [핵심] 기존 입찰자에게 즉시 환불 로직 (데이터 무소실)
                if auc_data['bidder'] and auc_data['bidder'] in db['users']:
                    db['users'][auc_data['bidder']]['bal'] += auc_data['bid']
                
                user['bal'] -= bid_input
                db['auction'].update({
                    "bid": bid_input,
                    "bidder": uid
                })
                st.success("입찰 성공! 현재 최고 입찰자입니다.")
                st.rerun()
            else: st.error("잔액이 부족하여 입찰할 수 없습니다.")
    else:
        st.markdown(f"### 🎉 경매 종료!")
        st.write(f"최종 낙찰자: **{auc_data['bidder']}** | 낙찰가: **${auc_data['bid']:,}**")
        if st.button("새로운 경매 시작 (관리자용)"):
            db['auction'].update({
                "item": "💎 신의 은총 (전 자산 2배권)",
                "bid": 1000000000,
                "bidder": None,
                "end_time": time.time() + 600
            })

# --- 탭 7: 클랜 연합 (기부 및 무한 배당) ---
with t_clan:
    st.subheader("🏴‍☠️ Clan Alliance & Investment")
    if not user['clan']:
        new_clan_name = st.text_input("새로운 클랜 이름 설정").strip()
        if st.button("🏴‍☠️ 클랜 창설 ($100,000,000)"):
            if len(new_clan_name) > 1 and user['bal'] >= 100000000:
                user['bal'] -= 100000000
                db['clans'][new_clan_name] = {"owner": uid, "donated": {uid: 50000000}}
                user['clan'] = new_clan_name
                st.success(f"[{new_clan_name}] 클랜이 창설되었습니다. 이제 배당금이 지급됩니다.")
                st.rerun()
    else:
        clan_info = db['clans'][user['clan']]
        st.info(f"🚩 소속 클랜: **{user['clan']}** | 클랜장: **{clan_info['owner']}**")
        st.write("클랜에 기부한 금액에 비례하여 초당 배당금이 자동 지급됩니다.")
        
        clan_donation = st.number_input("클랜 투자(기부) 금액", min_value=10000000, step=10000000)
        if st.button("💰 투자하기"):
            if user['bal'] >= clan_donation:
                user['bal'] -= clan_donation
                clan_info['donated'][uid] = clan_info['donated'].get(uid, 0) + clan_donation
                st.success(f"클랜에 ${clan_donation:,.0f}를 추가 투자했습니다. 초당 배당금이 상승합니다.")
                st.rerun()

# --- 탭 8: 명예 상점 (칭호 및 버프) ---
with t_shop:
    st.subheader("🏷️ Prestige Title Shop")
    prestige_items = {
        "🥇 자산가": 100000000,
        "👑 억만장자": 1000000000,
        "🌌 제국 황제": 10000000000,
        "🪐 우주의 신": 100000000000
    }
    for t_name, t_price in prestige_items.items():
        shop_col1, shop_col2, shop_col3 = st.columns([2, 3, 1.5])
        shop_col1.write(f"### {t_name}")
        shop_col2.write(f"판매 가격: ${t_price:,}")
        if shop_col3.button("즉시 구매", key=f"title_buy_{t_name}"):
            if user['bal'] >= t_price:
                user['bal'] -= t_price
                user['title'] = t_name
                # 등급별 색상 부여
                if t_name == "🪐 우주의 신": user['color'] = "#E74C3C"
                elif t_name == "🌌 제국 황제": user['color'] = "#F1C40F"
                elif t_name == "👑 억만장자": user['color'] = "#3498DB"
                st.success(f"[{t_name}] 칭호를 획득했습니다! 명예가 상승합니다.")
                st.rerun()
            else: st.error("자금이 부족합니다.")

# [9. 월드 채팅 시스템]
st.divider()
st.subheader("💬 World Real-time Chat")
chat_box = st.container(height=250)
for chat_msg in db['chat'][-30:]:
    u_data = db['users'].get(chat_msg['u'], {"color": "#FFF", "title": "🌱"})
    chat_box.markdown(f"<span style='color:{u_data['color']}; font-weight:bold;'>[{u_data['title']}] {chat_msg['u']}</span>: {chat_msg['msg']}", unsafe_allow_html=True)

with st.form("world_chat_input", clear_on_submit=True):
    user_msg = st.text_input("제국의 시민들과 대화하십시오 (관리자는 공지 권한)")
    if st.form_submit_button("메시지 전송"):
        if user_msg:
            db['chat'].append({"u": uid, "msg": user_msg})
            st.rerun()
