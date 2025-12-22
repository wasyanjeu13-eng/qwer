import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Global Real-Time Trading", layout="wide")

# --- 종목 리스트 ---
US_STOCKS = {'NVDA': '엔비디아', 'AAPL': '애플', 'TSLA': '테슬라', 'MSFT': 'MS', 'AMZN': '아마존'}
KR_STOCKS = {'005930.KS': '삼성전자', '000660.KS': 'SK하이닉스', '373220.KS': 'LG엔솔', '005380.KS': '현대차'}

# --- 세션 상태 초기화 (자산 및 포트폴리오) ---
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0  # 초기 자산 $100,000
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # {티커: {'수량': 0, '평균단가': 0}}

# --- 데이터 가져오기 ---
@st.cache_data(ttl=30)
def get_live_data(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="15m")
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- UI 레이아웃 ---
st.title("📊 실시간 주식 거래 시스템")

# 1. 사이드바: 내 자산 현황
st.sidebar.header("💰 내 지갑")
st.sidebar.metric("가용 잔고", f"${st.session_state.balance:,.2f}")

market = st.sidebar.radio("시장 선택", ["해외 주식 (US)", "한국 주식 (KR)"])
stock_dict = US_STOCKS if market == "해외 주식 (US)" else KR_STOCKS
ticker = st.sidebar.selectbox("종목 선택", options=list(stock_dict.keys()), format_func=lambda x: f"{stock_dict[x]} ({x})")

# 2. 메인: 차트 및 현재가
df = get_live_data(ticker)
if df is not None:
    curr_price = float(df['Close'].iloc[-1])
    st.subheader(f"{stock_dict[ticker]} ({ticker}) - 현재가: ${curr_price:,.2f}")
    
    # 캔들스틱 차트
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # 3. 매수/매도 버튼 섹션 (에러가 나도 실행되도록 분리)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        qty = st.number_input("거래 수량", min_value=1, value=1, key="order_qty")
        total_price = qty * curr_price
        if st.button("🔴 즉시 매수", use_container_width=True):
            if st.session_state.balance >= total_price:
                st.session_state.balance -= total_price
                # 포트폴리오 업데이트
                p = st.session_state.portfolio.get(ticker, {'수량': 0, '평균단가': 0})
                new_qty = p['수량'] + qty
                p['평균단가'] = ((p['평균단가'] * p['수량']) + total_price) / new_qty
                p['수량'] = new_qty
                st.session_state.portfolio[ticker] = p
                st.success(f"{stock_dict[ticker]} 매수 완료!")
                st.rerun()
            else: st.error("잔액이 부족합니다.")
    
    with col2:
        st.write(f"예정 금액: ${total_price:,.2f}")
        if st.button("🔵 즉시 매도", use_container_width=True):
            p = st.session_state.portfolio.get(ticker, {'수량': 0})
            if p['수량'] >= qty:
                st.session_state.balance += total_price
                p['수량'] -= qty
                st.session_state.portfolio[ticker] = p
                st.warning(f"{stock_dict[ticker]} 매도 완료!")
                st.rerun()
            else: st.error("보유 수량이 부족합니다.")

# 4. 실시간 포트폴리오 현황 (내가 산 주식 목록)
st.divider()
st.header("📋 내 투자 포트폴리오")
if not st.session_state.portfolio or all(v['수량'] == 0 for v in st.session_state.portfolio.values()):
    st.info("보유 중인 주식이 없습니다.")
else:
    # 데이터프레임으로 변환하여 수익률 계산
    rows = []
    for t, info in st.session_state.portfolio.items():
        if info['수량'] > 0:
            current_df = get_live_data(t)
            live_p = float(current_df['Close'].iloc[-1]) if current_df is not None else 0
            profit = (live_p - info['평균단가']) * info['수량']
            profit_rate = ((live_p / info['평균단가']) - 1) * 100 if info['평균단가'] > 0 else 0
            
            rows.append({
                "종목명": US_STOCKS.get(t, KR_STOCKS.get(t, t)),
                "보유수량": info['수량'],
                "평균단가": f"${info['평균단가']:,.2f}",
                "현재가": f"${live_p:,.2f}",
                "수익금": f"${profit:,.2f}",
                "수익률": f"{profit_rate:+.2f}%"
            })
    st.table(pd.DataFrame(rows))
