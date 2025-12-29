import streamlit as st
import random
import time
from datetime import datetime

# --- 1. [핵심] 서버 데이터베이스 (전체 유저 공유 영역) ---
@st.cache_resource
def get_global_server():
    return {
        "chat": [{"user": "시스템", "msg": "온라인 서버가 가동되었습니다!", "time": "00:00"}],
        "market": [],       # [{id, seller, item, price}]
        "guilds": {"운영진": ["Master"]}, # {길드명: [멤버들]}
        "world_events": "평화로움"
    }

server = get_global_server()

# --- 2. [개인] 유저 세션 데이터 초기화 ---
if 'user' not in st.session_state:
    st.session_state.user = {
        "id": f"모험가_{random.randint(1000, 9999)}",
        "lv": 1, "gold": 2000,
        "inv": ["철광석", "강화석", "전설의파편"],
        "guild": None,
        "logs": []
    }

u = st.session_state.user

# --- 3. 핵심 시스템 로직 ---

def send_chat(message):
    if message:
        now = datetime.now().strftime("%H:%M")
        server["chat"].append({"user": u["id"], "msg": message, "time": now})
        if len(server["chat"]) > 30: server["chat"].pop(0)

def register_market(item, price):
    if item in u["inv"]:
        u["inv"].remove(item)
        item_id = random.randint(10000, 99999)
        server["market"].append({"id": item_id, "seller": u["id"], "item": item, "price": price})
        st.toast(f"거래소에 {item} 등록 완료!")

# --- 4. 메인 UI 레이아웃 ---
st.set_page_config(page_title="Streamlit RPG Online", layout="wide")
st.title("🛡️ Saga Online: Infinite World")

# 사이드바: 내 정보
with st.sidebar:
    st.header(f"👤 {u['id']}")
    st.metric("Gold", f"{u['gold']} G")
    st.write(f"소속 길드: **{u['guild'] if u['guild'] else '무소속'}**")
    
    st.divider()
    # 길드 창설/가입
    if not u['guild']:
        new_guild = st.text_input("길드명 입력")
        if st.button("길드 창설/가입"):
            if new_guild not in server["guilds"]:
                server["guilds"][new_guild] = [u['id']]
            else:
                server["guilds"][new_guild].append(u['id'])
            u['guild'] = new_guild
            st.rerun()

# 메인 시스템 탭
tab_chat, tab_market, tab_guild, tab_inv = st.tabs(["💬 실시간 채팅", "⚖️ 유저 거래소", "🛡️ 길드 관리", "🎒 내 가방"])

# 1. 실시간 채팅 탭
with tab_chat:
    st.subheader("🌎 월드 메시지")
    chat_box = st.container(height=400, border=True)
    for c in server["chat"]:
        chat_box.write(f"**[{c['time']}] {c['user']}**: {c['msg']}")
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        msg = col1.text_input("메시지", placeholder="메시지를 입력하세요...", label_visibility="collapsed")
        if col2.form_submit_button("전송"):
            send_chat(msg)
            st.rerun()

# 2. 거래소 탭 (멀티플레이어 경제)
with tab_market:
    st.subheader("⚖️ 유저 간 자유 거래소")
    m_col1, m_col2 = st.columns([1, 2])
    
    with m_col1:
        st.write("📦 **아이템 판매 등록**")
        if u["inv"]:
            s_item = st.selectbox("물건 선택", u["inv"])
            s_price = st.number_input("가격(G)", min_value=10, step=10)
            if st.button("거래소 등록"):
                register_market(s_item, s_price)
                st.rerun()
        else:
            st.write("판매할 아이템이 없습니다.")

    with m_col2:
        st.write("🛒 **현재 매물 목록**")
        for i, entry in enumerate(server["market"]):
            with st.expander(f"{entry['item']} (판매자: {entry['seller']})"):
                st.write(f"가격: {entry['price']} G")
                if entry['seller'] != u['id']:
                    if st.button("구매하기", key=f"buy_{entry['id']}"):
                        if u["gold"] >= entry["price"]:
                            u["gold"] -= entry["price"]
                            u["inv"].append(entry["item"])
                            server["market"].pop(i)
                            st.success("구매 완료!")
                            st.rerun()
                        else:
                            st.error("골드가 부족합니다.")
                else:
                    st.caption("내가 등록한 상품입니다.")

# 3. 길드 관리 탭
with tab_guild:
    if u["guild"]:
        st.subheader(f"🛡️ 길드: {u['guild']}")
        st.write("**길드원 목록:**")
        for member in server["guilds"][u["guild"]]:
            st.write(f"- {member}")
        if st.button("길드 탈퇴"):
            server["guilds"][u["guild"]].remove(u['id'])
            u["guild"] = None
            st.rerun()
    else:
        st.info("길드에 가입하거나 창설하세요.")

# 4. 내 가방
with tab_inv:
    st.subheader("🎒 현재 보유 아이템")
    if u["inv"]:
        for item in u["inv"]:
            st.write(f"- {item}")
    else:
        st.write("가방이 비었습니다.")

# 실시간 갱신용
if st.button("🔄 서버 데이터 새로고침"):
    st.rerun()
