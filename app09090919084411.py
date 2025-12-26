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

st.set_page_config(page_title="익스트림 글로벌 뉴스 거래소", layout="wide")
st_autorefresh(interval=1000, key="v13_news_sync")

# --- 1. 전역 서버 데이터 설정 (종목명 포함) ---
@st.cache_resource
def init_server():
    # 종목 이름 정의 (일부 예시, 실제 100개 생성)
    us_names = ["GigaTesla", "PearPhone", "MacroSoft", "NvidiaX", "AmaZone", "SpaceNext", "MetaVerse", "OpenAI_Stock", "BankOfAmerica", "DisneyPlus"] + [f"US_Corp_{i}" for i in range(11, 51)]
    kr_names = ["삼성전기차", "하이닉스닉스", "네이버버", "카카오오오", "현대플라잉카", "셀트리온X", "LG에너지", "크래프톤톤", "에코프로플러스", "하이브이"] + [f"KR_Corp_{i}" for i in range(11, 51)]
    all_names = us_names + kr_names
    
    now = datetime.now()
    history = {}
    for name in all_names:
        base = 2000.0 if "Corp" not in name else 500.0
        history[name] = [[now - timedelta(seconds=20-i), base, base*1.01, base*0.99, base] for i in range(20)]
    
    return {
        "history": history,
        "delisted": set(),
        "rankings": {},
        "news": {"title": "시장이 안정적입니다.", "impact": 0, "target": None, "time": now},
        "last_sync": now
    }

server = init_server()

# --- 2. 뉴스 라이브러리 ---
GOOD_NEWS = ["신제품 세계 최초 공개!", "어닝 서프라이즈 발표", "글로벌 기업과 합병 소식", "정부 대규모 지원금 확정", "미국 시장 진출 성공"]
BAD_NEWS = ["회계 부정 의혹 조사", "대규모 리콜 사태 발생", "CEO 갑질 논란 및 사퇴", "경쟁사 신기술에 밀려 점유율 하락", "공장 가동 중단 사고"]

# --- 3. 닉네임 설정 ---
if 'nickname' not in st.session_state:
    st.title("🚀 글로벌 뉴스 연동 거래소")
    nick = st.text_input("닉네임을 입력하고 시작하세요:")
    if st.button("입장"):
        if nick:
            st.session_state.nickname = nick
            st.session_state.balance = 100000.0
            st.session_state.portfolio = {}
            server['rankings'][nick] = 100000.0
            st.rerun()
    st.stop()

# --- 4. 엔진 (뉴스 발생 및 시세 연동) ---
def engine():
    now = datetime.now()
    diff = int((now - server['last_sync']).total_seconds())
    if diff < 1: return

    # [뉴스 발생 로직] 40초마다 새로운 뉴스
    if (now - server['news']['time']).total_seconds() > 40:
        is_good = random.random() > 0.5
        server['news'] = {
            "title": random.choice(GOOD_NEWS if is_good else BAD_NEWS),
            "impact": random.uniform(0.5, 1.2) if is_good else random.uniform(-0.8, -0.4),
            "target": random.choice(list(server['history'].keys())),
            "time": now
        }

    for name, data in server['history'].items():
        if name in server['delisted']: continue
        
        last_close = data[-1][4]
        for i in range(min(diff, 10)):
            step_time = server['last_sync'] + timedelta(seconds=i+1)
            vol = np.random.uniform(-0.05, 0.05)
            
            # [뉴스 영향 반영]
            if name == server['news']['target']:
                time_passed = (step_time - server['news']['time']).total_seconds()
                if time_passed < 5: # 뉴스 직후 강한 반응
                    vol += server['news']['impact']
                else: # 뉴스 이후 서서히 하락/안정화 (뉴스 피로도)
                    vol -= 0.02 

            # [30초 대쇼크]
            if step_time.second % 30 == 0:
                vol += np.random.uniform(-0.5, 0.5)

            new_open = last_close
            new_close = last_close * (1 + vol)
            
            # 암시장 50번 필승 및 상폐 방어
            if name == "US_Corp_50": new_close = last_close * (1 + abs(vol))
            if new_close < 0.5: new_close = 1.0 # 상폐 방어선
            
            data.append([step_time, new_open, new_open*1.02, new_open*0.98, new_close])
            last_close = new_close
            
        server['history'][name] = data[-40:]

    # 랭킹 갱신
    val = st.session_state.balance
    for n, info in st.session_state.portfolio.items():
        val += info['수량'] * server['history'][n][-1][4]
    server['rankings'][st.session_state.nickname] = val
    server['last_sync'] = now

engine()

# --- 5. UI 및 대시보드 ---
# 상단 뉴스 바
st.warning(f"🔔 실시간 속보: {server['news']['target']} - {server['news']['title']}")

# 랭킹 및 개인 정보
with st.sidebar:
    st.title(f"👤 {st.session_state.nickname}")
    st.metric("총 자산", f"${server['rankings'][st.session_state.nickname]:,.0f}")
    st.divider()
    st.subheader("🏆 TOP 5")
    rdf = pd.DataFrame([{"ID": k, "Asset": v} for k, v in server['rankings'].items()]).sort_values("Asset", ascending=False).head(5)
    st.table(rdf)

# 메인 차트 구역
ticker = st.selectbox("종목 선택 (서버 공통 시세)", list(server['history'].keys()))
df = pd.DataFrame(server['history'][ticker], columns=['Date', 'Open', 'High', 'Low', 'Close'])
curr = df.iloc[-1]

col1, col2 = st.columns([3, 1])
with col1:
    fig = go.Figure(data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write(f"### {ticker}")
    st.title(f"${curr['Close']:,.2f}")
    qty = st.number_input("거래 수량", min_value=1, value=1)
    if st.button("BUY", use_container_width=True):
        if st.session_state.balance >= qty * curr['Close']:
            st.session_state.balance -= qty * curr['Close']
            p = st.session_state.portfolio.get(ticker, {'수량': 0})
            p['수량'] += qty
            st.session_state.portfolio[ticker] = p
            st.rerun()
    
    hold = st.session_state.portfolio.get(ticker, {'수량': 0})['수량']
    if st.button(f"SELL ALL ({hold})", use_container_width=True):
        if hold > 0:
            st.session_state.balance += hold * curr['Close']
            st.session_state.portfolio[ticker]['수량'] = 0
            st.rerun()

# 제작자/암시장 입구 (생략 가능하나 유지)
if st.sidebar.button("관리자/암시장"):
    st.sidebar.info("암시장: 0328 / 제작자: 1908441199470328")
