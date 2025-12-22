import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 라이브러리 체크 및 자동 새로고침 설정
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("requirements.txt에 streamlit-autorefresh를 추가하고 Reboot 해주세요.")
    st.stop()

st.set_page_config(page_title="익스트림 3단 변동 거래소", layout="wide")
# 1초마다 시세 갱신
st_autorefresh(interval=1000, key="datarefresh")

# --- 1. 종목 리스트 (해외/국내 총 100개) ---
if 'stock_list' not in st.session_state:
    us_names = ["Apple", "Nvidia", "Tesla", "Microsoft", "Amazon", "Google", "Meta", "Netflix", "AMD", "Intel", 
                "Adobe", "Salesforce", "Oracle", "Cisco", "Broadcom", "Qualcomm", "Texas Inst.", "Micron", "PayPal", "Starbucks",
                "Disney", "Nike", "Boeing", "Coca-Cola", "Pepsi", "Visa", "Mastercard", "Goldman Sachs", "JPMorgan", "Morgan Stanley",
                "ExxonMobil", "Chevron", "Pfizer", "Moderna", "Johnson&Johnson", "Walmart", "Costco", "Home Depot", "McDonalds", "Uber",
                "Airbnb", "Snapchat", "Spotify", "Palantir", "Coinbase", "Roblox", "Unity", "Zoom", "Shopify", "Square"]
    
    kr_names = ["삼성전자", "SK하이닉스", "LG엔솔", "삼성바이오", "현대차", "기아", "셀트리온", "POSCO홀딩스", "NAVER", "LG화학",
                "삼성SDI", "카카오", "KB금융", "신한지주", "현대모비스", "포스코퓨처엠", "삼성물산", "에코프로", "에코프로비엠", "카카오뱅크",
                "메리츠금융", "HMM", "삼성화재", "KT&G", "고려아연", "SK이노베이션", "한화에어로", "두산에너빌리티", "LG전자", "카카오페이",
                "삼성전기", "크래프톤", "엔씨소프트", "넷마블", "하이브", "S-Oil", "대한항공", "아모레퍼시픽", "KT", "SK텔레콤",
                "LG유플러스", "한국전력", "우리금융", "하나금융", "기업은행", "삼성중공업", "HD현대중공업", "한화솔루션", "현대건설", "금호석유"]

    st.session_state.US_STOCKS = {f"US_{i+1:02d}": name for i, name in enumerate(us_names)}
    st.session_state.KR_STOCKS = {f"KR_{i+1:02d}": name for i, name in enumerate(kr_names)}

# --- 2. 세션 상태 초기화 ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'price_history' not in st.session_state: st.session_state.price_history = {}

# --- 3. 가격 생성기 (1초/30초/1분 하이브리드 변동) ---
def get_extreme_price_data(ticker):
    now = datetime.now()
    if ticker not in st.session_state.price_history:
        base_price = 100.0 if "US" in ticker else 50000.0
        df = pd.DataFrame([[now - timedelta(seconds=1), base_price, base_price*1.02, base_price*0.98, base_price]], 
                          columns=['Date', 'Open', 'High', 'Low', 'Close'])
        st.session_state.price_history[ticker] = df

    df = st.session_state.price_history[ticker]
    last_price = float(df['Close'].iloc[-1])
    
    # 변동 주사위 굴리기
    dice = np.random.random()
    
    # 1. [1분 주기] 대변동 (확률 1.5%) - ±50% ~ 120%
    if dice < 0.015:
        volatility = np.random.uniform(0.5, 1.2) * (1 if np.random.random() > 0.5 else -1)
        st.toast(f"⚡ [1분 변동] {ticker} 초거대 해일 발생!!", icon="💥")
    
    # 2. [30초 주기] 중간 변동 (확률 3.5%) - ±10% ~ 30%
    elif dice < 0.05:
        volatility = np.random.uniform(0.1, 0.3) * (1 if np.random.random() > 0.5 else -1)
        st.toast(f"🌊 [30초 변동] {ticker} 강한 파도 진입", icon="🌊")
        
    # 3. [1초 주기] 일반 변동 - ±0.5%
    else:
        volatility = np.random.uniform(-0.005, 0.005)

    new_open = last_price
    new_close = max(last_price * (1 + volatility), 0.1)
    
    # 캔들 시각화 보정 (몸통이 잘 보이게 High/Low 간격 확보)
    body_size = abs(new_open - new_close)
    new_high = max(new_open, new_close) + (body_size * 0.2 + new_open * 0.002)
    new_low = min(new_open, new_close) - (body_size * 0.2 + new_open * 0.002)
    
    new_row = pd.DataFrame([[now, new_open, new_high, new_low, new_close]], 
                           columns=['Date', 'Open', 'High', 'Low', 'Close'])
    
    df = pd.concat([df, new_row], ignore_index=True).iloc[-50:]
    st.session_state.price_history[ticker] = df
    return df

# --- 4. 메인 UI 및 차트 ---
st.title("📈 3단 계층 변동 가상 거래소")

market = st.sidebar.radio("시장 선택", ["해외 마켓", "국내 마켓"])
stock_dict = st.session_state.US_STOCKS if "해외" in market else st.session_state.KR_STOCKS
ticker = st.sidebar.selectbox("종목 선택", options=list(stock_dict.keys()), 
                             format_func=lambda x: f"{stock_dict[x]} ({x})")

df = get_extreme_price_data(ticker)
curr_p = df['Close'].iloc[-1]
diff = curr_p - df['Close'].iloc[-2]
pct = (diff / df['Close'].iloc[-2]) * 100

color = "#ef5350" if diff < 0 else "#26a69a"
st.markdown(f"### {stock_dict[ticker]} ({ticker})")
st.markdown(f"<h1 style='color:{color};'>${curr_p:,.2f} ({pct:+.2f}%)</h1>", unsafe_allow_html=True)


fig = go.Figure(data=[go.Candlestick(
    x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    increasing_line_color='#26a69a', increasing_fillcolor='#26a69a',
    decreasing_line_color='#ef5350', decreasing_fillcolor='#ef5350'
)])
fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# --- 5. 거래 및 포트폴리오 ---
st.sidebar.metric("💰 나의 잔고", f"${st.session_state.balance:,.2f}")
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    qty = st.number_input("거래 수량", min_value=1, value=1)
with c2:
    if st.button("🔴 매수", use_container_width=True):
        if st.session_state.balance >= qty * curr_p:
            st.session_state.balance -= qty * curr_p
            p = st.session_state.portfolio.get(ticker, {'수량': 0, '평단가': 0})
            p['평단가'] = ((p['평단가'] * p['수량']) + (qty * curr_p)) / (p['수량'] + qty)
            p['수량'] += qty
            st.session_state.portfolio[ticker] = p
            st.rerun()
with c3:
    hold = st.session_state.portfolio.get(ticker, {'수량': 0})['수량']
    if st.button(f"🔵 전량 매도 ({hold}주)", use_container_width=True):
        if hold > 0:
            st.session_state.balance += hold * curr_p
            st.session_state.portfolio[ticker]['수량'] = 0
            st.rerun()

st.subheader("📋 실시간 나의 포트폴리오")
pf = []
for t, info in st.session_state.portfolio.items():
    if info['수량'] > 0:
        lp = st.session_state.price_history[t]['Close'].iloc[-1]
        pf.append({"종목": st.session_state.US_STOCKS.get(t, st.session_state.KR_STOCKS.get(t, t)), 
                   "수량": info['수량'], "평단가": f"${info['평단가']:,.2f}", 
                   "현재가": f"${lp:,.2f}", "수익률": f"{(lp/info['평단가']-1)*100:+.2f}%"})
if pf: st.table(pd.DataFrame(pf))
else: st.caption("보유 주식 없음")
