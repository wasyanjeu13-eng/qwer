import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("requirements.txt에 streamlit-autorefresh를 추가해주세요.")
    st.stop()

st.set_page_config(page_title="익스트림 주식 전쟁: 마스터 에디션", layout="wide")
st_autorefresh(interval=1500, key="v_final_all_in_one")

# --- 1. 전역 서버 메모리 DB (계정, 시세, 채팅, 뉴스, 강퇴) ---
@st.cache_resource
def init_master_server():
    # 100개 종목 생성
    us_names = ["GigaTesla", "PearPhone", "MacroSoft", "NvidiaX", "AmaZone", "SpaceNext", "MetaVerse", "OpenAI_Stock", "BankOfAmerica", "DisneyPlus"] + [f"US_Corp_{i}" for i in range(11, 51)]
    kr_names = ["삼성전기차", "하이닉스닉스", "네이버버", "카카오오오", "현대플라잉카", "셀트리온X", "LG에너지", "크래프톤톤", "에코프로플러스", "하이브이"] + [f"KR_Corp_{i}" for i in range(11, 51)]
    all_names = us_names + kr_names
    now = datetime.now()
    return {
        "history": {n: [[now - timedelta(seconds=20-i), 1000.0, 1010.0, 990.0, 1000.0] for i in range(20)] for n in all_names},
        "delisted": set(),
        "users": {},      # {id: {"pw": pw, "nick": nick, "balance": 100000.0, "portfolio": {}}}
        "chat_log": [{"user": "SYSTEM", "msg": "거래소에 오신 것을 환영합니다.", "time": now}],
        "banned": set(),  # 강퇴 유저 ID
        "news": {"title": "시장이 안정적입니다.", "impact": 0, "target": None, "time": now},
        "last_sync": now
    }

server = init_master_server()

# --- 2. 회원 시스템 (로그인/가입) ---
if 'user_id' not in st.session_state:
    st.title("🔐 익스트림 주식 거래소")
    t_log, t_reg = st.tabs(["로그인", "계정 생성"])
    with t_reg:
        r_id = st.text_input("아이디", key="r_id")
        r_pw = st.text_input("비밀번호", type="password", key="r_pw")
        r_nick = st.text_input("닉네임", key="r_nick")
        if st.button("가입하기"):
            if r_id and r_pw and r_nick and r_id not in server['users']:
                server['users'][r_id] = {"pw": r_pw, "nick": r_nick, "balance": 100000.0, "portfolio": {}}
                st.success("가입 성공! 로그인 하세요.")
            else: st.error("이미 있거나 잘못된 정보입니다.")
    with t_log:
        l_id = st.text_input("아이디", key="l_id")
        l_pw = st.text_input("비밀번호", type="password", key="l_pw")
        if st.button("로그인"):
            if l_id in server['banned']: st.error("🚫 추방된 계정입니다.")
            elif l_id in server['users'] and server['users'][l_id]['pw'] == l_pw:
                st.session_state.user_id = l_id
                st.rerun()
            else: st.error("정보가 일치하지 않습니다.")
    st.stop()

# 강퇴 즉시 체크
if st.session_state.user_id in server['banned']:
    st.error("🚨 관리자에 의해 서버에서 추방되었습니다."); st.stop()

# 세션 상태 초기화
u_id = st.session_state.user_id
my_data = server['users'][u_id]
if 'is_bm' not in st.session_state: st.session_state.is_bm = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- 3. 시세 및 뉴스 엔진 ---
def run_engine():
    now = datetime.now()
    diff = int((now - server['last_sync']).total_seconds())
    if diff < 1: return

    # 자동 뉴스 발생 (45초 주기)
    if (now - server['news']['time']).total_seconds() > 45:
        is_good = random.random() > 0.5
        server['news'] = {
            "title": random.choice(["혁신 기술 발표", "역대급 실적"] if is_good else ["기밀 유출 사태", "법정 분쟁"]),
            "impact": random.uniform(0.7, 1.5) if is_good else random.uniform(-0.9, -0.4),
            "target": random.choice(list(server['history'].keys())),
            "time": now
        }

    for name, h_data in server['history'].items():
        if name in server['delisted']: continue
        last_val = h_data[-1][4]
        for i in range(min(diff, 5)):
            st_time = server['last_sync'] + timedelta(seconds=i+1)
            vol = np.random.uniform(-0.05, 0.05)
            # 뉴스 반응 및 잔상 하락 로직
            if name == server['news']['target']:
                passed = (st_time - server['news']['time']).total_seconds()
                vol += server['news']['impact'] if passed < 6 else -0.03 # 초기 폭등락 후 서서히 하락
            # 30초 대쇼크
            if st_time.second % 30 == 0: vol += np.random.uniform(-0.4, 0.4)
            # 암시장 전용 로직
            if name == "US_Corp_50": vol = abs(vol) if vol != 0 else 0.1
            
            new_v = max(last_val * (1 + vol), 1.0)
            h_data.append([st_time, last_val, last_val*1.02, last_val*0.98, new_v])
            last_val = new_v
        server['history'][name] = h_data[-40:]
    server['last_sync'] = now

run_engine()

# --- 4. 메인 UI 및 상단바 ---
st.warning(f"📢 뉴스 속보 [{server['news']['target']}]: {server['news']['title']}")

c1, c2, c3 = st.columns([5, 2, 2])
with c2:
    if st.button("🌑 암시장 모드" if not st.session_state.is_bm else "🚪 일반 시장"):
        if not st.session_state.is_bm: st.session_state.ask_bm = True
        else: st.session_state.is_bm = False; st.rerun()
with c3:
    if st.button("🛠️ 제작자 제어" if not st.session_state.is_admin else "🔒 제어 종료"):
        if not st.session_state.is_admin: st.session_state.ask_ad = True
        else: st.session_state.is_admin = False; st.rerun()

# 비밀번호 검증창 (입력 시에만 활성화)
if st.session_state.get('ask_bm'):
    if st.text_input("암시장 비밀번호", type="password") == "0328":
        st.session_state.is_bm, st.session_state.ask_bm = True, False; st.rerun()
if st.session_state.get('ask_ad'):
    if st.text_input("제작자 비밀번호", type="password") == "1908441199470328":
        st.session_state.is_admin, st.session_state.ask_ad = True, False; st.rerun()

# --- 5. 제작자 마스터 컨트롤 패널 ---
if st.session_state.is_admin:
    with st.expander("👑 마스터 권한 제어판", expanded=True):
        t1, t2, t3 = st.tabs(["시세 조작", "특종 발행", "유저 제재"])
        with t1:
            if st.button("💥 전 서버 시장 폭락 (-90%)"):
                for n in server['history']: server['history'][n][-1][4] *= 0.1
            if st.button("🚀 전 서버 시장 폭등 (+500%)"):
                for n in server['history']: server['history'][n][-1][4] *= 6.0
        with t2:
            n_t = st.selectbox("대상 종목", list(server['history'].keys()))
            n_h = st.text_input("헤드라인", "정부로부터 독점 판매권 획득!")
            n_i = st.select_slider("영향력", options=[-1, 1], value=1, format_func=lambda x: "폭락" if x==-1 else "폭등")
            if st.button("📢 뉴스 강제 살포"):
                server['news'] = {"title": n_h, "impact": n_i * 1.5, "target": n_t, "time": datetime.now()}
        with t3:
            target_u = st.selectbox("유저 ID", list(server['users'].keys()))
            if st.button("🚨 해당 유저 강퇴 및 차단"):
                server['banned'].add(target_u); st.rerun()
            if st.button("💰 유저 자산 몰수"):
                server['users'][target_u]['balance'] = 0; st.rerun()

# --- 6. 실시간 채팅창 (사이드바) ---
st.sidebar.title(f"👤 {my_data['nick']}")
st.sidebar.metric("내 자산", f"${my_data['balance']:,.0f}")
st.sidebar.divider()
st.sidebar.subheader("💬 월드 채팅")
chat_box = st.sidebar.container(height=300)
for c in server['chat_log'][-20:]: chat_box.write(f"**{c['user']}**: {c['msg']}")
msg = st.sidebar.text_input("채팅 입력", key="msg_input")
if st.sidebar.button("전송"):
    if msg:
        server['chat_log'].append({"user": my_data['nick'], "msg": msg, "time": datetime.now()})
        st.rerun()

# --- 7. 거래소 메인 화면 ---
ticker = "US_Corp_50" if st.session_state.is_bm else st.selectbox("종목 선택", [n for n in server['history'].keys() if n not in server['delisted'] and n != "US_Corp_50"])
df = pd.DataFrame(server['history'][ticker], columns=['Date', 'Open', 'High', 'Low', 'Close'])
curr = df.iloc[-1]

st.subheader(f"📈 {ticker} 실시간 시세 {'(암시장)' if st.session_state.is_bm else ''}")
fig = go.Figure(data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

col_tr1, col_tr2 = st.columns(2)
with col_tr1:
    trade_qty = st.number_input("수량", min_value=1, value=1)
    if st.button("🔴 매수", use_container_width=True):
        if my_data['balance'] >= trade_qty * curr['Close']:
            my_data['balance'] -= trade_qty * curr['Close']
            p = my_data['portfolio'].get(ticker, 0)
            my_data['portfolio'][ticker] = p + trade_qty
            st.rerun()
with col_tr2:
    my_qty = my_data['portfolio'].get(ticker, 0)
    if st.button(f"🔵 전량 매도 (보유: {my_qty})", use_container_width=True):
        if my_qty > 0:
            my_data['balance'] += my_qty * curr['Close']
            my_data['portfolio'][ticker] = 0
            st.rerun()

# 랭킹 시스템
st.divider()
st.subheader("🏆 부자 랭킹 TOP 5")
rank_data = [{"ID": id, "닉네임": d['nick'], "자산": d['balance']} for id, d in server['users'].items()]
st.table(pd.DataFrame(rank_data).sort_values("자산", ascending=False).head(5))
