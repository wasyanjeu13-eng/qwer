import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Global Real-Time Trading", layout="wide")

# --- 종목 리스트 (해외 25, 한국 25) ---
US_STOCKS = ['NVDA', 'AAPL', 'TSLA', 'MSFT', 'AMZN', 'GOOGL', 'META', 'NFLX', 'AMD', 'PLTR', 
             'AVGO', 'ORCL', 'COST', 'ADBE', 'CRM', 'NFLX', 'WMT', 'JPM', 'V', 'MA', 
             'UNH', 'PG', 'HD', 'JNJ', 'BAC']

KR_STOCKS = ['005930.KS', '000660.KS', '373220.KS', '207940.KS', '005380.KS', '000270.KS', '068270.KS', '005490.KS', '035420.KS', '051910.KS',
             '035720.KS', '006400.KS', '012330.KS', '105560.KS', '028260.KS', '055550.KS', '011200.KS', '032830.KS', '003550.KS', '033780.KS',
             '000810.KS', '086790.KS', '010130.KS', '018260.KS', '009150.KS']

# --- 가상 자산 시스템 (세션 유지) ---
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0  # 초기 자산 $100,000

# --- 데이터 가져오기 함수 ---
@st.cache_data(ttl=30) # 30초마다 데이터 갱신
def get_live_data(ticker):
    # 실시간 느낌을 위해 1분봉 데이터 7일치 로드
    df = yf.download(ticker, period="7d", interval="1m")
    if not df.empty:
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
    return df

# --- 메인 UI ---
st.title("📊 Real-Time Global Trading System")

# 사이드바 설정
st.sidebar.header("💰 가상 지갑")
st.sidebar.metric("가용 잔고", f"${st.session_state.balance:,.2f}")
st.sidebar.divider()

market = st.sidebar.radio("시장 선택", ["해외 주식 (US)", "한국 주식 (KR)"])
selected_list = US_STOCKS if market == "해외 주식 (US)" else KR_STOCKS
ticker = st.sidebar.selectbox("종목 선택", selected_list)

try:
    df = get_live_data(ticker)
    
    if df.empty:
        st.error("데이터를 불러올 수 없습니다. 장 마감 여부나 티커를 확인하세요.")
    else:
        # 실시간 가격 정보 계산
        curr_price = df['Close'].iloc[-1].item()
        prev_close = df['Close'].iloc[-2].item()
        change = curr_price - prev_close
        pct_change = (change / prev_close) * 100
        
        # 상단 현재가 강조 레이아웃
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            color = "#ef5350" if change < 0 else "#26a69a"
            st.markdown(f"<h1 style='color:{color};'>{ticker}: ${curr_price:,.2f}</h1>", unsafe_allow_html=True)
        with col2:
            st.metric("변동폭", f"{change:+.2f}", f"{pct_change:+.2f}%")
        with col3:
            st.metric("거래량", f"{df['Volume'].iloc[-1]:,.0f}")

        # --- 전문가급 차트 생성 ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_width=[0.2, 0.8])

        # 1. 캔들스틱 차트
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="주가", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ), row=1, col=1)

        # 2. 이동평균선
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='yellow', width=1), name='5분선'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange', width=1), name='20분선'), row=1, col=1)

        # 3. ★현재가 가로 점선 추가★
        fig.add_shape(type="line", x0=df.index[0], x1=df.index[-1], y0=curr_price, y1=curr_price,
                      line=dict(color="white", width=1, dash="dash"), row=1, col=1)
        
        # 현재가 라벨 추가
        fig.add_annotation(x=df.index[-1], y=curr_price, text=f" 현재가: {curr_price:,.2f}", 
                           showarrow=False, align="left", bgcolor=color, font=dict(color="white"), row=1, col=1)

        # 4. 거래량 차트
        bar_colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=bar_colors, name="거래량"), row=2, col=1)

        # 차트 스타일링 (TradingView 느낌)
        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=600,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- 매수/매도 하단 섹션 ---
        st.divider()
        order_col1, order_col2 = st.columns(2)
        with order_col1:
            st.subheader("🛒 실시간 주문")
            amount = st.number_input("주문 수량", min_value=1, value=1)
            total = amount * curr_price
            st.write(f"결제 예정 금액: **${total:,.2f}**")
            
            c1, c2 = st.columns(2)
            if c1.button("🔴 즉시 매수", use_container_width=True):
                if st.session_state.balance >= total:
                    st.session_state.balance -= total
                    st.success(f"{ticker} {amount}주 매수 완료!")
                    st.rerun()
                else:
                    st.error("잔액이 부족합니다.")
            
            if c2.button("🔵 즉시 매도", use_container_width=True):
                st.session_state.balance += total
                st.warning(f"{ticker} {amount}주 매도 완료!")
                st.rerun()

except Exception as e:
    st.sidebar.error(f"데이터 연동 오류: {e}")

st.caption("※ 본 시스템은 실제 주가 데이터를 기반으로 한 가상 투자 시뮬레이션입니다.")
