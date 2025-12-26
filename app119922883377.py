import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# 1. 시스템 설정 (자동 새로고침)
try:
    from streamlit_autorefresh import st_autorefresh
except:
    st.error("pip install streamlit-autorefresh 가 필요합니다.")
    st.stop()

st.set_page_config(page_title="STOCK WAR: OMEGA GENESIS", layout="wide")
st_autorefresh(interval=1000, key="omega_genesis_absolute_v7")

# 2. [중앙 DB] 모든 유저와 시세가 공유되는 금고 (가장 중요)
@st.cache_resource
def get_global_db():
    stocks = [f"K-Corp_{i:02d}" for i in range(1, 81)]
    vips = ["🥇GOLD_FUND", "🏰ROYAL_ESTATE", "☢️PLUTONIUM"]
    coins = ["₿_BITCOIN", "💎_ETHEREUM", "🐕_DOGE"]
    all_t = stocks + vips + coins
    now = datetime.now()
    history = {n: [[now - timedelta(seconds=i*2), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20, 0, -1)] for n in all_t}
    return {
        "history": history, "users": {}, "chat_log": [], "banned": set(), 
        "market_frozen": False, "last_sync": now,
        "news": {"title": "서버 정상 작동 중", "impact": 0, "target": None, "time": now}
    }

db = get_global_db()

# 3. [시세 엔진] 변동성 강화 (초당 최대 50%)
def run_market_engine():
    now = datetime.now()
    if (now - db['last_sync']).total_seconds() >= 1:
        for n in db['history']:
            data = db['history'][n]
            last_p = data[-1][4]
            # 변동폭: 코인 0.5, 일반주 0.2
            vol = 0.5 if any(c in n for c in ["₿", "💎", "🐕"]) else 0.2
            change = np.random.uniform(-vol, vol)
            
            # 뉴스 영향
            if n == db['news']['target']:
                change += db['news']['impact']
                db['news']['impact'] *= 0.8
                
            new_p = max(last_p * (1 + change), 1.0)
            data.append([now, last_p, max(last_p, new_p)*1.02, min(last_p, new_p)*0.98, new_p])
            db['history'][n] = data[-30:]
        db['last_sync'] = now

run_market_engine()

# 4. [보안] 로그인 및 세션 관리
if 'user_id' not in st.session_state:
    st.title("🔐 OMEGA GENESIS - 시스템 접속")
    col_log, col_reg = st.columns(2)
    with col_reg:
        r_id = st.text_input("새 ID")
        r_pw = st.text_input("새 PW", type="password")
        if st.button("계정 생성"):
            if r_id not in db['users']:
                db['users'][r_id] = {"pw": r_pw, "balance": 100000.0, "portfolio": {}, "title": "🌱 우주 먼지"}
                st.success("가입 완료!")
    with col_log:
        l_id = st.text_input("ID")
        l_pw = st.text_input("PW", type="password")
        if st.button("로그인"):
            if l_id in db['users'] and db['users'][l_id]['pw'] == l_pw:
                st.session_state.user_id = l_id
                st.rerun()
    st.stop()

user_id = st.session_state.user_id
user_data = db['users'][user_id]

# 5. [제작자 권능] 사이드바 (돈 지급 기능 핵심)
with st.sidebar:
    st.title("👑 MASTER PANEL")
    m_pw = st.text_input("ADMIN PASSWORD", type="password")
    if m_pw == "190844119947201110328":
        st.session_state.is_admin = True
        user_data['title'] = "🔥 SYSTEM MASTER"
        st.success("권능 활성화됨")
        
        st.divider()
        st.subheader("💰 자산 강제 주입")
        target_u = st.selectbox("지급 대상", list(db['users'].keys()))
        cash_amt = st.number_input("금액($)", min_value=0, value=1000000000)
        if st.button("즉시 지급"):
            db['users'][target_u]['balance'] += cash_amt
            st.balloons()
            st.success(f"{target_u}님께 ${cash_amt:,} 지급 완료!")

        if st.button("🔥 시장 1000% 폭등"):
            for k in db['history']: db['history'][k][-1][4] *= 11
        
        db['market_frozen'] = st.toggle("🚫 전 서버 거래 동결", value=db['market_frozen'])

# 6. [메인 UI]
col_dash, col_chat_area = st.columns([3, 1])

with col_dash:
    st.markdown(f"## 🏆 {user_data['title']} | {user_id}")
    st.header(f"현재 자산: ${user_data['balance']:,.2f}")
    
    # 모든 기능 탭 (하나라도 먹통되지 않게 독립 구성)
    t_stock, t_vip, t_deal, t_gamble, t_clan, t_title, t_auction = st.tabs(
        ["📈 거래소", "💎 VIP", "🤝 직거래", "🎰 도박", "🏴‍☠️ 클랜", "🏷️ 칭호", "🔨 경매"]
    )

    with t_stock: # 거래소
        sel_ticker = st.selectbox("종목 선택", list(db['history'].keys()))
        h_df = pd.DataFrame(db['history'][sel_ticker], columns=['time', 'open', 'high', 'low', 'close'])
        fig = go.Figure(data=[go.Candlestick(x=h_df['time'], open=h_df['open'], high=h_df['high'], low=h_df['low'], close=h_df['close'])])
        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        curr_p = h_df['close'].iloc[-1]
        st.metric(sel_ticker, f"${curr_p:,.2f}")
        
        if not db['market_frozen']:
            qty = st.number_input("거래 수량", min_value=1, value=1, key="tr_qty")
            c1, c2 = st.columns(2)
            if c1.button("LONG (매수)"):
                if user_data['balance'] >= curr_p * qty:
                    user_data['balance'] -= curr_p * qty
                    user_data['portfolio'][sel_ticker] = user_data['portfolio'].get(sel_ticker, 0) + qty
                    st.rerun()
            if c2.button("SHORT (공매도)"):
                if user_data['balance'] >= curr_p * qty:
                    user_data['balance'] -= curr_p * qty
                    st.warning("공매도 진입 완료")

    with t_gamble: # 도박 기능 복구
        st.subheader("🎰 인생 역전 카지노")
        bet_amt = st.number_input("배팅액", min_value=1000, max_value=int(user_data['balance']), step=1000)
        if st.button("🔥 4배 챌린지 시작 (확률 20%)"):
            if random.random() < 0.2:
                user_data['balance'] += bet_amt * 3
                st.balloons()
                st.success("🎉 대성공! 4배 획득!")
            else:
                user_data['balance'] -= bet_amt
                st.error("💀 파산... 다음 기회에.")
            st.rerun()

    with t_title: # 칭호 시스템 복구
        st.subheader("🏷️ 계급 및 칭호 변경")
        available_titles = ["🌱 우주 먼지", "🐜 개미 대장", "💰 자산가", "👑 억만장자", "🌌 주권자"]
        if st.session_state.get('is_admin'): available_titles.append("🔥 SYSTEM MASTER")
        
        new_title = st.selectbox("장착할 칭호 선택", available_titles)
        if st.button("칭호 장착"):
            user_data['title'] = new_title
            st.success(f"[{new_title}]로 칭호가 변경되었습니다.")
            st.rerun()

with col_chat_area: # 채팅 및 랭킹 영역
    st.subheader("💬 월드 채팅")
    # 채팅 로그 표시
    chat_container = st.container(height=400)
    for c in db['chat_log'][-20:]:
        chat_container.write(f"**{c['user']}**: {c['msg']}")
    
    # 채팅 입력창
    with st.form("chat_input_form", clear_on_submit=True):
        m = st.text_input("메시지")
        if st.form_submit_button("전송") and m:
            db['chat_log'].append({"user": user_id, "msg": m})
            st.rerun()
    
    st.divider()
    st.subheader("🏆 부자 랭킹")
    top_5 = sorted(db['users'].items(), key=lambda x: x[1]['balance'], reverse=True)[:5]
    for i, (name, d) in enumerate(top_5):
        st.write(f"{i+1}위. {name} (${d['balance']:,.0f})")
