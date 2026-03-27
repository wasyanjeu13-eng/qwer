import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# [1. 시스템 엔진 및 자동 새로고침 설정]
# 서버의 실시간 동기화를 담당하는 핵심 엔진입니다.
try:
    from streamlit_autorefresh import st_autorefresh
except:
    st.error("시스템 가동 실패: 'pip install streamlit-autorefresh'가 필요합니다.")
    st.stop()

st.set_page_config(page_title="OMEGA GENESIS: UNLIMITED", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=2000, key="omega_ultimate_war_v1")

# [2. 뉴스 시나리오 데이터베이스 40종 - 절대 생략 금지]
# 이 데이터는 시장 변동성의 근거가 되며, 주가에 직접적인 Impact를 줍니다.
NEWS_DATABASE = [
    {"msg": "💊 아카 제약, 탈모 완치 신약 '모모린' 임상 3상 최종 통과!", "target": "K-Corp_01", "impact": 0.55},
    {"msg": "📱 넥스 테크, 세계 최초 롤러블 투명 스마트폰 양산 발표", "target": "K-Corp_02", "impact": 0.38},
    {"msg": "🚀 스페이스 오메가, 달 뒷면 희토류 채굴 기지 건설 완료", "target": "K-Corp_03", "impact": 0.62},
    {"msg": "⚡ 테슬라 아머, 1회 충전 7000km 주행 고체 배터리 개발", "target": "K-Corp_04", "impact": 0.45},
    {"msg": "🏗️ 제국 건설, 사우디 네옴시티 500조 원 규모 추가 수주 성공", "target": "K-Corp_05", "impact": 0.35},
    {"msg": "🎮 넥슨트리, 메타버스 게임 '오메가 월드' 전세계 1위 등극", "target": "K-Corp_06", "impact": 0.28},
    {"msg": "🧪 바이오 제네시스, 인간 수명 150세 연장 프로젝트 성공", "target": "K-Corp_07", "impact": 0.75},
    {"msg": "📉 글로벌 중앙은행 금리 2% 깜짝 인상... 증시 대폭락 쇼크", "target": "ALL", "impact": -0.30},
    {"msg": "🐕 도지코인, 화성 이주 프로젝트 '머스크 시티' 공식 화폐 채택", "target": "🐕_DOGE", "impact": 0.95},
    {"msg": "₿ 비트코인, 미국 연준 비축 자산 정식 편입 뉴스", "target": "₿_BITCOIN", "impact": 0.25},
    {"msg": "🪐 솔라나, 메인넷 속도 200% 향상 '파이어댄서' 업데이트 완료", "target": "🪐_SOLANA", "impact": 0.40},
    {"msg": "💎 이더리움, 소각 메커니즘 강화로 공급량 역대 최저 기록", "target": "💎_ETHEREUM", "impact": 0.32},
    {"msg": "⚠️ 넥스 테크, 반도체 생산 라인 대규모 화재 발생... 공급 중단", "target": "K-Corp_02", "impact": -0.45},
    {"msg": "💸 아카 제약, 리콜 사태 발생 및 CEO 배임 혐의 구속 영장", "target": "K-Corp_01", "impact": -0.60},
    {"msg": "🏦 정부, 디지털 자산 거래 소득세 5년 유예 및 비과세 검토", "target": "CRYPTO", "impact": 0.42},
    {"msg": "🏢 오메가 쇼핑, 드론 배송 시스템 전국 상용화... 인건비 80% 절감", "target": "K-Corp_08", "impact": 0.22},
    {"msg": "🥗 웰빙 푸드, 배양육 시장 점유율 세계 1위 달성", "target": "K-Corp_09", "impact": 0.18},
    {"msg": "⚔️ 아이언 돔, 차세대 레이저 방패 시스템 전세계 독점 수출", "target": "K-Corp_10", "impact": 0.48},
    {"msg": "🌊 해양 에너지, 심해 열수광상 채굴권 획득 소식", "target": "K-Corp_03", "impact": 0.25},
    {"msg": "📉 경기 침체 우려 가중... 안전 자산인 금/달러로 자산 쏠림", "target": "ALL", "impact": -0.12},
    {"msg": "🍎 애플 오메가, AR 글래스 '비전 킹' 역대급 사전 예약", "target": "K-Corp_02", "impact": 0.30},
    {"msg": "🚙 무인 택시 '오메가 드라이브', 유료 운행 허가 획득", "target": "K-Corp_04", "impact": 0.25},
    {"msg": "🏰 제국 건설, 화성 신도시 설계권 단독 낙찰", "target": "K-Corp_05", "impact": 0.50},
    {"msg": "🕹️ 넥슨트리, 구글 마이크로소프트 인수 합병설 제기", "target": "K-Corp_06", "impact": 0.40},
    {"msg": "🧬 바이오 제네시스, 암 정복 백신 상용화 임박", "target": "K-Corp_07", "impact": 0.65},
    {"msg": "📊 오메가 쇼핑, 블랙프라이데이 역대 최대 매출 기록", "target": "K-Corp_08", "impact": 0.20},
    {"msg": "🌾 웰빙 푸드, 대체 식품 유럽 시장 점유율 1위", "target": "K-Corp_09", "impact": 0.15},
    {"msg": "🛰️ 아이언 돔, 저궤도 위성 요격 시스템 실전 배치", "target": "K-Corp_10", "impact": 0.38},
    {"msg": "⛓️ 솔라나, 네트워크 48시간 중단... 투자자 이탈 가속", "target": "🪐_SOLANA", "impact": -0.50},
    {"msg": "💎 이더리움, 창시자 비탈릭 부테린 대규모 매도설 루머", "target": "💎_ETHEREUM", "impact": -0.25},
    {"msg": "🌋 아이슬란드 화산 폭발... 항공 물류 대란으로 실적 저하 우려", "target": "K-Corp_05", "impact": -0.15},
    {"msg": "🤖 넥스 테크, 휴머노이드 로봇 '오메가 봇' 가정 보급 시작", "target": "K-Corp_02", "impact": 0.45},
    {"msg": "💉 아카 제약, 치매 예방 보조제 약국 출시 직후 매진", "target": "K-Corp_01", "impact": 0.25},
    {"msg": "💎 이더리움, 레이저 2 솔루션 도입으로 수수료 0원 육박", "target": "💎_ETHEREUM", "impact": 0.20},
    {"msg": "⚡ 테슬라 아머, 태양광 충전 차량 '솔라 킹' 출시", "target": "K-Corp_04", "impact": 0.33},
    {"msg": "🎥 넥슨트리, VR 영화관 서비스 시작", "target": "K-Corp_06", "impact": 0.15},
    {"msg": "🏪 오메가 쇼핑, 무인 편의점 1만 개 지점 돌파", "target": "K-Corp_08", "impact": 0.12},
    {"msg": "🍔 웰빙 푸드, 인공 배양 패티 전세계 맥도날드 공급", "target": "K-Corp_09", "impact": 0.30},
    {"msg": "🔥 아이언 돔, 레일건 함포 개발 완료 및 해군 배치", "target": "K-Corp_10", "impact": 0.28},
    {"msg": "🏴‍☠️ 거래소 해킹 발생... 도지코인 5,000억 원 탈취 소식", "target": "🐕_DOGE", "impact": -0.40}
]

# [3. 아이템 상세 정의 및 색상 카탈로그]
ITEM_CATALOG = {
    "⚡ 시세 폭등권": {"desc": "보유 주식 중 1종을 즉시 50% 폭등시킵니다.", "color": "#FF4B4B"},
    "💰 자금 세탁권": {"desc": "현재 총 보유 현금의 30%를 보너스로 즉시 획득합니다.", "color": "#2ECC71"},
    "❄️ 시세 동결권": {"desc": "서버 전체의 시세 변동을 60초간 강제로 멈춥니다.", "color": "#3498DB"},
    "🎟️ 경매 즉시종료": {"desc": "진행 중인 경매 시간을 10초로 단축시켜 낙찰을 유도합니다.", "color": "#F1C40F"},
    "🔱 절대자의 인장": {"desc": "전설 칭호를 즉시 획득하고 채팅색이 변경됩니다.", "color": "#9B59B6"},
    "🧪 기술력 도약권": {"desc": "제국 기술력(공격/방어)을 즉시 0.5 포인트 올립니다.", "color": "#E67E22"}
}

# [4. 전역 데이터베이스 초기화 - 캐시 고정]
@st.cache_resource
def init_mega_db():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 11)]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE", "🪐_SOLANA"]
    all_tickers = stocks + coins
    now = datetime.now()
    history = {}
    for n in all_tickers:
        history[n] = []
        base_p = 1000.0 if "Corp" in n else 50000.0 if "BIT" in n else 2500.0
        for i in range(60, 0, -1):
            t = now - timedelta(seconds=i*3)
            p = base_p * (1 + random.uniform(-0.05, 0.05))
            # [시간, 시가, 고가, 저가, 종가]
            history[n].append([t, p, p*1.01, p*0.99, p])
    return {
        "history": history, "users": {}, "chat": [], "clans": {}, "lottery_pot": 100000000,
        "last_sync": now, "last_payout": time.time(), "server_frozen": False,
        "forced_price": {}, "trade_requests": [], "war_logs": [], "news": NEWS_DATABASE[0],
        "server_msg": "OMEGA 시스템이 정식 가동 중입니다. 제국 건설을 시작하세요.",
        "auction": {"item": "👑 서버 통합 제어권 (1시간)", "bid": 500000000, "bidder": None, "end_time": time.time() + 1200}
    }

db = init_mega_db()

# [5. 핵심 연산 엔진 (실시간 시세/배당/뉴스)]
def run_master_engine():
    now = datetime.now()
    # 15초마다 뉴스 갱신
    if int(time.time()) % 15 == 0:
        db['news'] = random.choice(NEWS_DATABASE)

    if (now - db['last_sync']).total_seconds() >= 2.0:
        if not db['server_frozen']:
            for n, h_list in db['history'].items():
                last_p = h_list[-1][4]
                if n in db['forced_price']:
                    new_p = db['forced_price'][n]
                else:
                    # 뉴스 영향력 적용
                    impact = db['news']['impact'] if (db['news']['target'] == n or db['news']['target'] == "ALL") else 0
                    if db['news']['target'] == "CRYPTO" and any(c in n for c in ["BIT", "ETH", "DOGE", "SOL"]):
                        impact = db['news']['impact']
                    
                    vol = 0.12 if any(c in n for c in ["BIT", "ETH", "DOGE", "SOL"]) else 0.03
                    change_rate = np.random.normal(impact/4, vol/2)
                    new_p = max(last_p * (1 + change_rate), 1.0)
                
                open_p, close_p = last_p, new_p
                high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.003))
                low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.003))
                h_list.append([now, open_p, high_p, low_p, close_p])
                db['history'][n] = h_list[-60:]
        db['last_sync'] = now

    # 초당 배당금 정산
    curr_time = time.time()
    if curr_time - db['last_payout'] >= 1.0:
        for u_id, u_info in db['users'].items():
            if u_info.get('clan') and u_info['clan'] in db['clans']:
                clan = db['clans'][u_info['clan']]
                if u_id in clan['donated']:
                    mult = 3.0 if u_info['title'] == "🌌 제국 황제" else 1.0
                    u_info['bal'] += (clan['donated'][u_id] * 0.00015) * mult
        db['last_payout'] = curr_time

run_master_engine()

# [6. 보안 인증 및 로그인]
if 'uid' not in st.session_state:
    st.title("🌌 OMEGA GENESIS: THE SUPREME EMPIRE")
    auth_tab1, auth_tab2 = st.tabs(["🔐 기존 시민 접속", "📝 신규 시민 등록"])
    with auth_tab2:
        reg_id = st.text_input("아이디 설정", key="reg_id").strip()
        reg_pw = st.text_input("비번 설정", type="password", key="reg_pw")
        if st.button(" empire_register_execute "):
            if reg_id and reg_id not in db['users']:
                db['users'][reg_id] = {
                    "pw": reg_pw, "bal": 10000000.0, "port": {}, "items": ["🔱 절대자의 인장"],
                    "title": "🌱 신규 시민", "color": "#AAA", "clan": None, "atk_lvl": 1.0, "def_lvl": 1.0
                }
                st.success(f"시민 등록 완료: {reg_id}님 환영합니다.")
            else: st.error("이미 사용 중인 아이디입니다.")
    with auth_tab1:
        log_id = st.text_input("아이디", key="log_id")
        log_pw = st.text_input("비밀번호", type="password", key="log_pw")
        if st.button(" empire_login_execute "):
            if log_id in db['users'] and db['users'][log_id]['pw'] == log_pw:
                st.session_state.uid = log_id; st.rerun()
            else: st.error("보안 인증에 실패하였습니다.")
    st.stop()

uid = st.session_state.uid
user = db['users'][uid]

# [7. 관리자 사이드바 - GOD MODE]
with st.sidebar:
    st.title("👑 GOD MODE CONTROL")
    god_code = st.text_input("ACCESS CODE", type="password")
    if god_code == "190844119947201110328":
        user['title'], user['color'] = "🔥 SYSTEM MASTER", "#FF0000"
        st.success("ADMIN 권한 활성화됨")
        if st.button("💰 1조 원 즉시 지급"): user['bal'] += 1000000000000
        db['server_frozen'] = st.toggle("전 서버 시세 동결", db['server_frozen'])
        target_stock = st.selectbox("조작 종목", list(db['history'].keys()))
        target_price = st.number_input("고정 가격", value=0.0)
        if st.button("⚡ 가격 즉시 고정"): db['forced_price'][target_stock] = target_price
        if st.button("🔓 고정 해제"): db['forced_price'].pop(target_stock, None)

# [8. 메인 대시보드 및 실시간 뉴스]
st.markdown(f"""
    <div style="background-color:#111; padding:25px; border-radius:15px; border-left: 10px solid {user['color']};">
        <h1 style="margin:0; font-size:40px;"><span style="color:{user['color']};">[{user['title']}]</span> {uid}</h1>
        <h2 style="color:#2ecc71; margin-top:10px;">현금 자산: ${user['bal']:,.2f}</h2>
    </div>
""", unsafe_allow_html=True)

st.info(f"📺 **[속보]** {db['news']['msg']}")

# [9. 통합 기능 탭 - 600줄 이상의 방대한 기능군]
t_market, t_portfolio, t_p2p, t_inventory, t_casino, t_auction, t_clan, t_war, t_shop = st.tabs([
    "📈 실시간 거래소", "📊 내 자산 및 판매", "🤝 P2P 개인거래", "🎒 인벤토리", "🎰 로얄 카지노", "🔨 실시간 경매", "🏴‍☠️ 클랜 가입/기부", "⚔️ 제국 전쟁연구소", "🏷️ 명예 상점"
])

# --- 탭 1: 거래소 (매수 전용) ---
with t_market:
    st.subheader("📈 Global Market Terminal")
    selected_ticker = st.selectbox("거래 종목 선택", list(db['history'].keys()))
    h_data = db['history'][selected_ticker]
    df = pd.DataFrame(h_data, columns=['Time', 'Open', 'High', 'Low', 'Close'])
    fig = go.Figure(data=[go.Candlestick(x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#FF4B4B', decreasing_line_color='#0077FF')])
    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    cur_p = df['Close'].iloc[-1]
    st.markdown(f"### 현재가: <span style='color:#FF4B4B;'>${cur_p:,.2f}</span>", unsafe_allow_html=True)
    
    m_col1, m_col2 = st.columns(2)
    buy_q = m_col1.number_input("매수 수량", min_value=1, value=1)
    if m_col2.button("🚀 전재산 풀매수 (ALL-IN)", use_container_width=True):
        total_q = int(user['bal'] // cur_p)
        if total_q > 0:
            user['bal'] -= (total_q * cur_p)
            q, a = user['port'].get(selected_ticker, [0, 0.0])
            user['port'][selected_ticker] = [q + total_q, ((q*a) + (total_q*cur_p))/(q+total_q)]
            st.success("매수 완료"); st.rerun()
    if st.button("💰 지정 수량 매수"):
        if user['bal'] >= (buy_q * cur_p):
            user['bal'] -= (buy_q * cur_p)
            q, a = user['port'].get(selected_ticker, [0, 0.0])
            user['port'][selected_ticker] = [q + buy_q, ((q*a) + (buy_q*cur_p))/(q+buy_q)]
            st.success("매수 성공"); st.rerun()

# --- 탭 2: 자산 및 매도(판매) 시스템 (형이 찾던 것) ---
with t_portfolio:
    st.subheader("📊 My Strategic Portfolio")
    owned = {k: v for k, v in user['port'].items() if v[0] > 0}
    if not owned: st.warning("보유 중인 자산이 없습니다.")
    else:
        p_data = []
        for ticker, (qty, avg_p) in owned.items():
            cur_p = db['history'][ticker][-1][4]
            eval_v = qty * cur_p
            profit = (cur_p - avg_p) * qty
            rate = ((cur_p - avg_p) / avg_p) * 100
            p_data.append({"종목": ticker, "수량": f"{qty:,}", "평단가": f"${avg_p:,.2f}", "현재가": f"${cur_p:,.2f}", "평가금": f"${eval_v:,.0f}", "수익률": f"{rate:+.2f}%"})
        st.table(pd.DataFrame(p_data))
        
        st.divider()
        st.markdown("### 📥 즉시 판매(청산) 시스템")
        sell_sel = st.selectbox("판매할 종목", list(owned.keys()))
        sell_qty = st.number_input("판매 수량", min_value=1, max_value=int(owned[sell_sel][0]), value=int(owned[sell_sel][0]))
        if st.button("💰 선택 수량 판매하기"):
            cp = db['history'][sell_sel][-1][4]
            user['bal'] += (sell_qty * cp)
            user['port'][sell_sel][0] -= sell_qty
            st.success(f"판매 완료! ${sell_qty * cp:,.2f} 입금됨"); st.rerun()
        if st.button("🔥 전 종목 일괄 청산 (SELL ALL)", use_container_width=True):
            total_sell = 0
            for t, d in owned.items():
                total_sell += d[0] * db['history'][t][-1][4]
                user['port'][t][0] = 0
            user['bal'] += total_sell
            st.warning(f"전 종목 매도 완료! ${total_sell:,.2f} 확보됨"); st.rerun()

# --- 탭 3: P2P 개인 거래 ---
with t_p2p:
    st.subheader("🤝 1:1 유저 간 자산 이동")
    pc1, pc2 = st.columns(2)
    with pc1:
        st.write("📤 새로운 제안 작성")
        others = [u for u in db['users'].keys() if u != uid]
        if others:
            target = st.selectbox("상대방", others)
            p_type = st.radio("자산", ["CASH", "ITEM"])
            if p_type == "CASH":
                val = st.number_input("금액", min_value=0)
                if st.button("💰 제안 보내기"):
                    if user['bal'] >= val:
                        db['trade_requests'].append({"from": uid, "to": target, "type": "CASH", "val": val, "id": time.time()})
                        st.toast("전송 완료")
            else:
                if user['items']:
                    item = st.selectbox("아이템", list(set(user['items'])))
                    if st.button("🎁 아이템 제안"):
                        db['trade_requests'].append({"from": uid, "to": target, "type": "ITEM", "val": item, "id": time.time()})
    with pc2:
        st.write("📥 도착한 제안")
        received = [r for r in db['trade_requests'] if r['to'] == uid]
        for r in received:
            with st.container(border=True):
                st.write(f"보낸이: {r['from']} | 내용: {r['val']}")
                if st.button("수락 및 체결", key=f"p2p_{r['id']}"):
                    sender = db['users'][r['from']]
                    if r['type'] == "CASH" and sender['bal'] >= r['val']:
                        sender['bal'] -= r['val']; user['bal'] += r['val']
                    elif r['type'] == "ITEM" and r['val'] in sender['items']:
                        sender['items'].remove(r['val']); user['items'].append(r['val'])
                    db['trade_requests'].remove(r); st.rerun()

# --- 탭 4: 인벤토리 ---
with t_inventory:
    st.subheader("🎒 My Inventory")
    if not user['items']: st.info("보유 아이템 없음")
    else:
        for idx, item_name in enumerate(user['items']):
            info = ITEM_CATALOG.get(item_name, {"desc": "설명 없음", "color": "#FFF"})
            with st.container(border=True):
                ic1, ic2, ic3 = st.columns([1, 4, 1])
                ic1.markdown(f"<h4 style='color:{info['color']};'>{item_name}</h4>", unsafe_allow_html=True)
                ic2.write(info['desc'])
                if ic3.button("사용", key=f"inv_btn_{idx}"):
                    if item_name == "💰 자금 세탁권": user['bal'] *= 1.3
                    elif item_name == "❄️ 시세 동결권": db['server_frozen'] = True
                    elif item_name == "⚡ 시세 폭등권":
                        owned_list = [t for t, v in user['port'].items() if v[0] > 0]
                        if owned_list: 
                            target = random.choice(owned_list)
                            db['history'][target][-1][4] *= 1.5
                    elif item_name == "🧪 기술력 도약권":
                        user['atk_lvl'] += 0.5; user['def_lvl'] += 0.5
                    user['items'].pop(idx); st.rerun()

# --- 탭 5: 로얄 카지노 ---
with t_casino:
    st.subheader("🎰 The Grand Royal Casino")
    cas1, cas2 = st.columns(2)
    with cas1:
        st.write(f"총 누적 잭팟: **${db['lottery_pot']:,.0f}**")
        if st.button("로또 구매 ($1,000,000)"):
            if user['bal'] >= 1000000:
                user['bal'] -= 1000000; db['lottery_pot'] += 800000
                if random.random() < 0.007:
                    user['bal'] += db['lottery_pot']; db['lottery_pot'] = 100000000; st.balloons()
                else: st.error("꽝!")
    with cas2:
        st.write("무작위 아이템 상자 ($2,000,000)")
        if st.button("미스터리 박스 개봉"):
            if user['bal'] >= 2000000:
                user['bal'] -= 2000000
                it = random.choice(list(ITEM_CATALOG.keys()))
                user['items'].append(it); st.success(f"획득: {it}")

# --- 탭 6: 실시간 경매 ---
with t_auction:
    st.subheader("🔨 Live Auction")
    auc = db['auction']
    remain = int(auc['end_time'] - time.time())
    if remain > 0:
        st.warning(f"물품: {auc['item']} | 최고가: ${auc['bid']:,} | 입찰자: {auc['bidder']}")
        st.write(f"남은 시간: {remain}초")
        bid_input = st.number_input("입찰금액", min_value=int(auc['bid']*1.1), step=10000000)
        if st.button("🔨 입찰"):
            if user['bal'] >= bid_input:
                if auc['bidder']: db['users'][auc['bidder']]['bal'] += auc['bid']
                user['bal'] -= bid_input; auc.update({"bid": bid_input, "bidder": uid}); st.rerun()
    else: st.write("현재 진행 중인 경매가 없습니다.")

# --- 탭 7: 클랜 시스템 (가입/기부 리스트) ---
with t_clan:
    st.subheader("🏴‍☠️ Clan Alliance")
    cl_col1, cl_col2 = st.columns(2)
    with cl_col1:
        st.write("🌐 가입 가능한 클랜 리스트")
        if not db['clans']: st.info("창설된 클랜 없음")
        for cn, ci in db['clans'].items():
            with st.container(border=True):
                st.write(f"**{cn}** (클랜장: {ci['owner']})")
                st.write(f"총 기부금: ${sum(ci['donated'].values()):,.0f} | 인원: {len(ci['donated'])}명")
                if user['clan'] is None:
                    if st.button(f"{cn} 가입하기", key=f"join_{cn}"):
                        user['clan'] = cn; ci['donated'][uid] = 0; st.rerun()
                elif user['clan'] == cn: st.success("소속됨")
    with cl_col2:
        if user['clan'] is None:
            c_name = st.text_input("클랜 이름").strip()
            if st.button("🏴‍☠️ 클랜 창설 ($1억)"):
                if user['bal'] >= 100000000:
                    user['bal'] -= 100000000
                    db['clans'][c_name] = {"owner": uid, "donated": {uid: 50000000}, "atk": 1.0, "def": 1.0, "mil": 0}
                    user['clan'] = c_name; st.rerun()
        else:
            clan_info = db['clans'][user['clan']]
            st.info(f"🚩 내 클랜: {user['clan']}")
            don_amt = st.number_input("기부 금액 (배당금에 비례)", min_value=10000000, step=10000000)
            if st.button("💰 기부하기"):
                if user['bal'] >= don_amt:
                    user['bal'] -= don_amt; clan_info['donated'][uid] += don_amt; st.rerun()

# --- 탭 8: 제국 전쟁 연구소 (돈 소모 핵심) ---
with t_war:
    st.subheader("⚔️ Military Research & War")
    if not user['clan']: st.warning("클랜 소속 시민만 전쟁에 참여할 수 있습니다.")
    else:
        my_c = db['clans'][user['clan']]
        st.write(f"🛠️ 공격 기술: **x{my_c['atk']:.2f}** | 🛡️ 방어 기술: **x{my_c['def']:.2f}** | 🎖️ 상비군: {my_c['mil']:,}명")
        
        w1, w2 = st.columns(2)
        if w1.button("⚔️ 무기 고도화 연구 ($5,000만)"):
            if user['bal'] >= 50000000: 
                user['bal'] -= 50000000; my_c['atk'] += 0.1; st.success("공격력 상승!"); st.rerun()
        if w2.button("🛡️ 장갑 강화 연구 ($5,000만)"):
            if user['bal'] >= 50000000: 
                user['bal'] -= 50000000; my_c['def'] += 0.1; st.success("방어력 상승!"); st.rerun()
        
        st.divider()
        mil_qty = st.number_input("병력 모집 (1,000명당 $1,000만)", min_value=1000, step=1000)
        if st.button("🎖️ 병력 모집 실행"):
            cost = (mil_qty / 1000) * 10000000
            if user['bal'] >= cost:
                user['bal'] -= cost; my_c['mil'] += mil_qty; st.rerun()
    
# --- 탭 9: 명예 상점 ---
with t_shop:
    shop_items = {"🥇 자산가": 100000000, "👑 억만장자": 1000000000, "🌌 제국 황제": 10000000000, "🪐 우주의 신": 100000000000}
    for tn, tp in shop_items.items():
        sc1, sc2, sc3 = st.columns([2, 2, 1])
        sc1.write(f"### {tn}")
        sc2.write(f"가격: ${tp:,}")
        if sc3.button("구매", key=f"t_{tn}"):
            if user['bal'] >= tp:
                user['bal'] -= tp; user['title'] = tn; st.rerun()

# [10. 월드 채팅 시스템]
st.divider()
st.subheader("💬 World Chat")
chat_box = st.container(height=250)
for msg in db['chat'][-20:]:
    u_info = db['users'].get(msg['u'], {"color": "#FFF", "title": "🌱"})
    chat_box.markdown(f"<span style='color:{u_info['color']}'>[{u_info['title']}] {msg['u']}</span>: {msg['m']}", unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    user_msg = st.text_input("메시지 입력")
    if st.form_submit_button("전송"):
        if user_msg: db['chat'].append({"u": uid, "m": user_msg}); st.rerun()
            
# --- [기존 코드 맨 아래에 이어서 붙여넣으세요] ---


# --- [기존 코드 맨 아래에 이어서 붙여넣으세요] ---

st.divider()

# [1. 칭호 및 능력치 데이터 정의]
# 칭호에 따라 공격력(atk)과 방어력(def) 보너스 부여
TITLES = {
    "시민": {"atk": 1.0, "def": 1.0, "color": "#AAA", "req": 0},
    "용병": {"atk": 1.1, "def": 1.0, "color": "#5DADE2", "req": 1},
    "기사": {"atk": 1.2, "def": 1.1, "color": "#52BE80", "req": 3},
    "정복자": {"atk": 1.5, "def": 1.2, "color": "#F39C12", "req": 5},
    "전쟁의 신": {"atk": 9.0, "def": 2.0, "color": "#E74C3C", "req": 10} # 10연승 전용
}

# 유저 데이터에 연승 카운트가 없으면 초기화 (세션 유지용)
if 'win_streak' not in user: user['win_streak'] = 0

# [2. 전쟁 순위표 (TOP 10)]
st.subheader("🏆 전 서버 제국 서열 (전투력 순)")
rank_data = []
for u_id, u_info in db['users'].items():
    # 전투력 지표 = 병력 * 칭호 공격력
    current_title = u_info.get('title', '시민')
    atk_bonus = TITLES.get(current_title, TITLES['시민'])['atk']
    
    my_c_name = u_info.get('clan')
    mil_count = db['clans'][my_c_name]['mil'] if my_c_name and my_c_name in db['clans'] else 0
    
    rank_data.append({
        "시민": f"[{current_title}] {u_id}",
        "연승": f"{u_info.get('win_streak', 0)}회",
        "현재 병력": f"{mil_count:,}명",
        "전투력": int(mil_count * atk_bonus)
    })

if rank_data:
    w_df = pd.DataFrame(rank_data).sort_values(by="전투력", ascending=False).reset_index(drop=True)
    w_df.index += 1
    st.table(w_df.head(10))

# [3. 전쟁 지휘소 (10연승 로직 포함)]
st.divider()
st.subheader("⚔️ 제국 전면 전쟁 지휘소")

my_cn = user.get('clan')
if not my_cn or my_cn not in db['clans']:
    st.info("💡 클랜에 먼저 가입해야 전쟁 지휘가 가능합니다.")
else:
    my_c = db['clans'][my_cn]
    if uid not in my_c['donated']: my_c['donated'][uid] = 0 # 권한 부여
    
    # 현재 내 칭호 능력치 적용
    my_title = user.get('title', '시민')
    my_buff = TITLES.get(my_title, TITLES['시민'])
    
    st.markdown(f"**현재 칭호:** <span style='color:{my_buff['color']}'>{my_title}</span> (공격력 x{my_buff['atk']})", unsafe_allow_html=True)
    st.write(f"현재 연승 기록: **{user['win_streak']}** / 10 (10연승 시 '전쟁의 신' 등극)")

    targets = [c for c in db['clans'].keys() if c != my_cn]
    if targets:
        target_sel = st.selectbox("🎯 타겟 제국 선택", targets)
        en_c = db['clans'][target_sel]
        
        if st.button("🔥 침 공 개 시 (30초 진격)", use_container_width=True):
            if my_c['mil'] < 1000:
                st.error("❌ 병력이 1,000명 이상 필요합니다!")
            else:
                # 30초 대기 연출
                prog = st.progress(0); status = st.empty()
                for s in range(30):
                    time.sleep(1)
                    prog.progress((s+1)/30)
                    msgs = ["📡 적진 정찰", "🚜 전선 돌파", "⚔️ 육상 교전", "💣 최종 섬멸"]
                    status.text(f"⚔️ {msgs[s//8]} 중... ({30-(s+1)}초)")
                status.empty(); prog.empty()

                # --- 결과 계산 ---
                # 전투력 = 병력 * (클랜 기본공격력 + 칭호 보너스)
                my_total_atk = my_c.get('atk', 1.0) * my_buff['atk']
                my_p = (my_c['mil'] * my_total_atk) * random.uniform(0.8, 1.2)
                en_p = (en_c['mil'] * en_c.get('def', 1.0)) * random.uniform(0.8, 1.2)

                if my_p > en_p:
                    # 승리 시
                    user['win_streak'] += 1
                    loot = int(sum(en_c['donated'].values()) * 0.4)
                    user['bal'] += loot
                    
                    # 칭호 자동 승급 시스템
                    for t_name, t_info in TITLES.items():
                        if user['win_streak'] >= t_info['req']:
                            user['title'] = t_name
                    
                    # 병력 소모 (승리 시 20% 감소)
                    loss = int(my_c['mil'] * 0.2)
                    my_c['mil'] -= loss
                    en_c['mil'] = int(en_c['mil'] * 0.2) # 적 80% 궤멸
                    
                    st.balloons()
                    st.success(f"🎊 대승리! ${loot:,.0f} 약탈! (현재 {user['win_streak']}연승)")
                    if user['win_streak'] == 10:
                        st.warning("🔥 전설의 탄생! [전쟁의 신] 칭호를 획득했습니다!")
                else:
                    # 패배 시
                    user['win_streak'] = 0 # 연승 초기화
                    user['title'] = "시민" # 칭호 박탈 (다시 시작)
                    loss = int(my_c['mil'] * 0.9)
                    my_c['mil'] -= loss
                    st.error("💀 패배... 연승 기록과 칭호가 초기화되었습니다.")

# --- [기존 코드 맨 아래에 이어서 붙여넣으세요] ---

st.divider()
st.header("📊 제국 통합 랭킹 시스템")

# 1. 데이터 집계 (모든 유저 대상)
leaderboard_data = []
for u_id, u_info in db['users'].items():
    # [자산 계산] 현금 + 보유 주식/코인 현재가치 합산
    total_asset = u_info['bal']
    for t, v in u_info.get('port', {}).items():
        if t in db['history'] and v[0] > 0:
            total_asset += (v[0] * db['history'][t][-1][4])
    
    # [전투력 계산] 칭호 버프 반영 (칭호 데이터가 없으면 기본 1.0)
    current_title = u_info.get('title', '시민')
    # 위에서 정의한 TITLES 딕셔너리 참조 (없으면 기본값)
    atk_val = TITLES.get(current_title, {"atk": 1.0})['atk']
    
    # [클랜 병력 확인]
    c_name = u_info.get('clan')
    mil_count = db['clans'][c_name]['mil'] if c_name and c_name in db['clans'] else 0
    power_score = int(mil_count * atk_val)

    leaderboard_data.append({
        "순위": 0, # 임시
        "시민": f"[{current_title}] {u_id}",
        "총 자산": total_asset,
        "전투력": power_score,
        "연승": f"{u_info.get('win_streak', 0)}회",
        "소속": c_name if c_name else "무소속"
    })

# 2. 화면 출력 (탭으로 구분해서 깔끔하게)
t_asset, t_war = st.tabs(["💰 자산가 순위 (TOP 10)", "⚔️ 전쟁광 순위 (TOP 10)"])

with t_asset:
    # 자산 순으로 정렬
    df_asset = pd.DataFrame(leaderboard_data).sort_values(by="총 자산", ascending=False).reset_index(drop=True)
    df_asset["순위"] = df_asset.index + 1
    # 금액 포맷팅
    df_asset["총 자산"] = df_asset["총 자산"].apply(lambda x: f"${x:,.0f}")
    st.table(df_asset[["순위", "시민", "총 자산", "소속"]].head(10))

with t_war:
    # 전투력 순으로 정렬
    df_war = pd.DataFrame(leaderboard_data).sort_values(by="전투력", ascending=False).reset_index(drop=True)
    df_war["순위"] = df_war.index + 1
    # 숫자 포맷팅
    df_war["전투력"] = df_war["전투력"].apply(lambda x: f"{x:,}")
    st.table(df_war[["순위", "시민", "전투력", "연승", "소속"]].head(10))

# --- [순위표 코드 끝] ---

import time

# 1. 전쟁 진행 상태를 기억할 저장소 만들기 (맨 위에 한 번만 선언)
if 'war_ongoing' not in st.session_state:
    st.session_state.war_ongoing = False

# 2. 전쟁 시작 버튼 로직
if not st.session_state.war_ongoing:
    if st.button("🔥 전 면 전 쟁 개 시"):
        # 버튼을 누르는 순간 "전쟁 중"으로 상태 변경
        st.session_state.war_ongoing = True
        st.rerun() # 상태를 즉시 저장하고 화면을 전쟁 모드로 전환

# 3. 전쟁 진행 중일 때만 실행되는 블록 (이게 핵심)
if st.session_state.war_ongoing:
    st.warning("🚀 부대가 진격 중입니다. 창을 닫지 마세요!")
    
    prog_bar = st.progress(0)
    status_msg = st.empty()

    # --- 30초 대기 루프 (중간에 안 끊김) ---
    for i in range(30):
        time.sleep(1)
        prog_bar.progress((i + 1) / 30)
        status_msg.text(f"⚔️ 전투 진행 중... ({30-(i+1)}초 남음)")

    # --- 여기서 결과 계산 및 병력 차감 실행 ---
    # (여기에 형이 쓴 승패 로직 넣기)
    st.success("🏁 전투 종료! 결과를 확인하세요.")
    st.balloons()

    # 4. 전쟁 종료 후 상태 초기화 (그래야 다음 전쟁 가능)
    st.session_state.war_ongoing = False
    
    # 결과 확인 버튼을 누르면 다시 초기 화면으로
    if st.button("지휘소로 복귀"):
        st.rerun()
# --- [기존 코드 맨 아래에 이어서 붙여넣으세요] ---

st.divider()

# 1. 전쟁 진행 상태 스위치 (이게 꺼져있으면 게이지가 안 보임)
if 'war_active' not in st.session_state:
    st.session_state.war_active = False

# 2. 전쟁 시작 버튼 (전쟁 중이 아닐 때만 노출)
if not st.session_state.war_active:
    if st.button("🔥 전 면 전 쟁 개 시", use_container_width=True):
        st.session_state.war_active = True
        st.rerun() # 상태를 'True'로 고정하고 화면 새로고침

# 3. [핵심] 전쟁 중일 때만 돌아가는 루프 (상태가 True여야 게이지가 유지됨)
if st.session_state.war_active:
    st.warning("🚀 부대가 적진으로 진격 중입니다! (30초 소요)")
    
    # 게이지랑 메시지 칸 확보
    p_bar = st.progress(0)
    msg_slot = st.empty()

    # 30초 동안 절대로 안 사라지고 버티는 루프
    for i in range(30):
        time.sleep(1)
        # 게이지 업데이트 (1초마다 찔금찔금 차오름)
        p_bar.progress((i + 1) / 30)
        
        # 실시간 상황 중계 (형이 좋아하는 전황 보고)
        war_msgs = ["📡 적진 정찰 중...", "🚜 전차 부대 돌파!", "⚔️ 시가지 교전 중!", "💣 지휘부 타격!"]
        msg_slot.markdown(f"**[전황]** {war_msgs[i//8]} ({30-(i+1)}초 남음)")

    # --- 루프가 끝나면 결과 계산 (여기서 병력 깎고 돈 벌기) ---
    # (예시: 승패 로직)
    my_p = my_c['mil'] * random.uniform(0.8, 1.2)
    en_p = en_c['mil'] * random.uniform(0.8, 1.2)
    
    if my_p > en_p:
        st.balloons()
        st.success("🎊 대승리! 적 제국을 함락했습니다!")
        # [병력 소모 추가]
        loss = int(my_c['mil'] * 0.2)
        my_c['mil'] -= loss
        st.write(f"📉 피해 보고: 아군 **{loss:,}명** 전사")
    else:
        st.error("💀 패배... 부대가 전멸했습니다.")
        my_c['mil'] = int(my_c['mil'] * 0.1)

    # 4. 전쟁 종료 후 상태 초기화 (그래야 다음 전쟁 버튼이 다시 뜸)
    st.session_state.war_active = False
    
    if st.button("🏁 결과 확인 및 기지 복귀"):
        st.rerun()

# --- [수정 완료] ---
# --- [기존 코드 맨 아래에 이어서 붙여넣으세요] ---

st.divider()
st.subheader("⚔️ 제국 전면 전쟁 지휘소")

# 1. 전쟁 상태 변수 초기화 (없으면 생성)
if 'war_active' not in st.session_state:
    st.session_state.war_active = False

# 2. 전쟁 시작 전: 타겟 설정 및 버튼 노출
if not st.session_state.war_active:
    my_cn = user.get('clan')
    if not my_cn or my_cn not in db['clans']:
        st.info("💡 클랜에 가입해야 전쟁이 가능합니다.")
    else:
        my_c = db['clans'][my_cn]
        # [권한 강제 부여]
        if uid not in my_c['donated']: my_c['donated'][uid] = 0
        
        targets = [c for c in db['clans'].keys() if c != my_cn]
        if targets:
            target_sel = st.selectbox("🎯 침공할 제국 선택", targets)
            
            if st.button("🔥 전 면 전 쟁 개 시", use_container_width=True):
                if my_c['mil'] < 1000:
                    st.error("❌ 병력이 부족합니다! (최소 1,000명 필요)")
                else:
                    # 전쟁 시작! 상태를 True로 바꾸고 화면을 새로고침함
                    st.session_state.war_active = True
                    st.session_state.target_name = target_sel # 타겟 이름 저장
                    st.rerun()
        else:
            st.warning("⚠️ 공격할 적국이 없습니다.")

# 3. [핵심] 전쟁 진행 중: 게이지가 절대로 안 사라지는 구간
if st.session_state.war_active:
    target_name = st.session_state.target_name
    en_c = db['clans'][target_name]
    my_c = db['clans'][user['clan']]

    st.warning(f"🚀 {target_name} 제국으로 침공 부대가 진격 중입니다! (30초 소요)")
    
    # 화면에 박제할 공간 만들기
    p_bar = st.progress(0)
    msg_slot = st.empty()

    # 30초 동안 코드를 여기서 붙잡아둠 (루프 돌리는 중엔 화면 안 바뀜)
    for i in range(30):
        time.sleep(1)
        p_bar.progress((i + 1) / 30)
        
        # 전황 메시지 실시간 교체
        war_msgs = ["📡 적진 방어망 분석 중...", "🚜 전차 부대 국경 돌파!", "⚔️ 시가지 근접 교전 중!", "💣 적 지휘부 최종 정밀 타격!"]
        msg_slot.markdown(f"**[현장 중계]** {war_msgs[i//8]} ({30-(i+1)}초 남음)")

    # --- 30초 종료 후 결과 계산 및 병력 소모 ---
    my_title = user.get('title', '시민')
    # 칭호 버프 (전쟁의 신 등) 적용 로직
    atk_val = TITLES.get(my_title, {"atk": 1.0})['atk']
    
    my_p = (my_c['mil'] * my_c.get('atk', 1.0) * atk_val) * random.uniform(0.8, 1.2)
    en_p = (en_c['mil'] * en_c.get('def', 1.0)) * random.uniform(0.8, 1.2)

    if my_p > en_p:
        loot = int(sum(en_c['donated'].values()) * 0.4)
        user['bal'] += loot
        user['win_streak'] = user.get('win_streak', 0) + 1
        
        # 10연승 시 전쟁의 신 등극
        if user['win_streak'] >= 10: user['title'] = "전쟁의 신"
        
        # 병력 소모 (승리 시 20%)
        loss = int(my_c['mil'] * 0.2)
        my_c['mil'] -= loss
        en_c['mil'] = int(en_c['mil'] * 0.2)
        
        st.balloons()
        st.success(f"🎊 대승리! ${loot:,.0f} 약탈 성공! (현재 {user['win_streak']}연승)")
        st.write(f"📉 아군 병력 **{loss:,}명**이 명예롭게 전사했습니다.")
    else:
        # 패배 시 (연승 초기화, 병력 90% 소멸)
        user['win_streak'] = 0
        user['title'] = "시민"
        loss = int(my_c['mil'] * 0.9)
        my_c['mil'] -= loss
        st.error(f"💀 참패... {target_name}의 반격에 부대가 궤멸되었습니다.")
        st.write(f"📉 아군 병력 **{loss:,}명**이 전사했습니다.")

    # 전쟁 종료: 상태 초기화
    st.session_state.war_active = False
    if st.button("🏁 결과 확인 및 지휘소 복귀"):
        st.rerun()

# --- [수정 완료] ---
# --- [기존 코드 맨 아래에 이어서 붙여넣으세요] ---

st.divider()

# [1. 통합 순위표 (자산 & 전투력)]
st.subheader("🏆 제국 통합 서열 (TOP 10)")
rank_list = []
for u_id, u_info in db['users'].items():
    # 총 자산 계산
    total_asset = u_info['bal']
    for t, v in u_info.get('port', {}).items():
        if t in db['history'] and v[0] > 0:
            total_asset += (v[0] * db['history'][t][-1][4])
    
    # 전투력 계산 (칭호 버프 포함)
    c_name = u_info.get('clan')
    mil_count = db['clans'][c_name]['mil'] if c_name and c_name in db['clans'] else 0
    # 칭호 데이터 (TITLES 딕셔너리가 상단에 없다면 아래 주석 해제해서 사용)
    # TITLES = {"시민":1.0, "용병":1.1, "기사":1.2, "정복자":1.5, "전쟁의 신":2.5}
    atk_buff = 1.0
    if u_info.get('title') == "전쟁의 신": atk_buff = 2.5
    elif u_info.get('title') == "정복자": atk_buff = 1.5
    
    rank_list.append({
        "시민": f"[{u_info.get('title', '시민')}] {u_id}",
        "총 자산": total_asset,
        "전투력": int(mil_count * atk_buff),
        "연승": f"{u_info.get('win_streak', 0)}회"
    })

if rank_list:
    r_df = pd.DataFrame(rank_list).sort_values(by="전투력", ascending=False).reset_index(drop=True)
    r_df.index += 1
    r_df["총 자산"] = r_df["총 자산"].apply(lambda x: f"${x:,.0f}")
    st.table(r_df.head(10))


# [2. 즉시 결전 전쟁 지휘소]
st.divider()
st.subheader("⚔️ 즉시 결전 지휘소")

my_cn = user.get('clan')
if not my_cn or my_cn not in db['clans']:
    st.info("💡 클랜에 가입해야 전쟁이 가능합니다.")
else:
    my_c = db['clans'][my_cn]
    # [권한 강제 부여] 방장이면 무조건 멤버 인정
    if uid not in my_c['donated']: my_c['donated'][uid] = 0
    
    st.write(f"현재 칭호: **{user.get('title', '시민')}** | 연승 기록: **{user.get('win_streak', 0)}**")
    
    targets = [c for c in db['clans'].keys() if c != my_cn]
    if targets:
        target_sel = st.selectbox("🎯 침공할 제국 선택", targets)
        en_c = db['clans'][target_sel]
        
        # 🔥 [핵심] 버튼 누르면 0.1초 만에 결과 나옴
        if st.button("🔥 즉 시 침 공 (결전)", use_container_width=True):
            if my_c['mil'] < 1000:
                st.error("❌ 병력이 부족합니다! (최소 1,000명 필요)")
            else:
                # --- 결과 계산 ---
                # 내 전투력 (칭호 버프 반영)
                my_atk = my_c.get('atk', 1.0)
                if user.get('title') == "전쟁의 신": my_atk *= 2.5
                elif user.get('title') == "정복자": my_atk *= 1.5
                
                my_p = (my_c['mil'] * my_atk) * random.uniform(0.8, 1.2)
                en_p = (en_c['mil'] * en_c.get('def', 1.0)) * random.uniform(0.8, 1.2)

                if my_p > en_p:
                    # [승리]
                    loot = int(sum(en_c['donated'].values()) * 0.4)
                    user['bal'] += loot
                    user['win_streak'] = user.get('win_streak', 0) + 1
                    
                    # 10연승 시 전쟁의 신 등극
                    if user['win_streak'] >= 10: user['title'] = "전쟁의 신"
                    elif user['win_streak'] >= 5: user['title'] = "정복자"
                    
                    # 병력 소모 (승리 시 15%~25% 전사)
                    loss = int(my_c['mil'] * random.uniform(0.15, 0.25))
                    my_c['mil'] -= loss
                    en_c['mil'] = int(en_c['mil'] * 0.2) # 적 80% 궤멸
                    
                    st.balloons()
                    st.success(f"🎊 대승리! ${loot:,.0f} 약탈! (현재 {user['win_streak']}연승)")
                    st.write(f"📉 아군 피해: **{loss:,}명** 전사")
                else:
                    # [패배]
                    user['win_streak'] = 0
                    user['title'] = "시민"
                    loss = int(my_c['mil'] * 0.9)
                    my_c['mil'] -= loss
                    st.error(f"💀 참패... {target_sel}의 반격에 부대가 궤멸되었습니다.")
                    st.write(f"📉 아군 피해: **{loss:,}명** 전사 (연승/칭호 초기화)")
                
                # 결과 반영을 위해 새로고침
                st.button("결과 확인 완료") 
    else:
        st.warning("⚠️ 공격할 적국이 없습니다.")

# --- [수정 완료] ---
