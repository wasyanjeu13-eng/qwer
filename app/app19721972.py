import streamlit as st
import random

# 게임 데이터 정의
UPGRADE_TABLE = {
    0: {"name": "낡은 단검", "cost": 500, "succ_rate": 1.0, "base_sell_price": 500},
    1: {"name": "쓸만한 단검", "cost": 500, "succ_rate": 0.98, "base_sell_price": 500},
    2: {"name": "견고한 단검", "cost": 1000, "succ_rate": 0.95, "base_sell_price": 1000},
    3: {"name": "바이킹 소드", "cost": 2000, "succ_rate": 0.93, "base_sell_price": 2000},
    4: {"name": "불타는 검", "cost": 4000, "succ_rate": 0.90, "base_sell_price": 4000},
    5: {"name": "냉기의 소드", "cost": 7000, "succ_rate": 0.86, "base_sell_price": 7000},
    6: {"name": "양날 검", "cost": 10000, "succ_rate": 0.81, "base_sell_price": 10000},
    7: {"name": "심판자의 대검", "cost": 15000, "succ_rate": 0.75, "base_sell_price": 15000},
    8: {"name": "마력의 검", "cost": 22000, "succ_rate": 0.70, "base_sell_price": 22000},
    9: {"name": "타우 스워드", "cost": 30000, "succ_rate": 0.66, "base_sell_price": 30000},
    10: {"name": "형광검", "cost": 30000, "succ_rate": 0.62, "base_sell_price": 45000},
    11: {"name": "피묻은 검", "cost": 51000, "succ_rate": 0.61, "base_sell_price": 76500},
    12: {"name": "화염의 쌍검", "cost": 70000, "succ_rate": 0.54, "base_sell_price": 105000},
    13: {"name": "불꽃 마검", "cost": 80000, "succ_rate": 0.50, "base_sell_price": 120000},
    14: {"name": "마검 아포피스", "cost": 100000, "succ_rate": 0.49, "base_sell_price": 150000},
    15: {"name": "데몬 배틀 엑스", "cost": 130000, "succ_rate": 0.46, "base_sell_price": 195000},
    16: {"name": "투명 검", "cost": 170000, "succ_rate": 0.44, "base_sell_price": 255000},
    17: {"name": "날렵한 용검", "cost": 220000, "succ_rate": 0.40, "base_sell_price": 330000},
    18: {"name": "샤이니 소드", "cost": 300000, "succ_rate": 0.38, "base_sell_price": 450000},
    19: {"name": "왕푸야샤", "cost": 400000, "succ_rate": 0.35, "base_sell_price": 600000},
    20: {"name": "다색검", "cost": 650000, "succ_rate": 0.33, "base_sell_price": 975000},
    21: {"name": "템페스트 골드", "cost": 1000000, "succ_rate": 0.30, "base_sell_price": 1500000},
    22: {"name": "샤프 워커", "cost": 1500000, "succ_rate": 0.27, "base_sell_price": 2250000},
    23: {"name": "피에로의 쌍검", "cost": 2000000, "succ_rate": 0.25, "base_sell_price": 3000000},
    24: {"name": "도룡도", "cost": 2500000, "succ_rate": 0.23, "base_sell_price": 3750000},
    25: {"name": "안 강해보이는 검", "cost": 3000000, "succ_rate": 0.35, "base_sell_price": 4500000},
    26: {"name": "메두사", "cost": 5000000, "succ_rate": 0.50, "base_sell_price": 7500000},
    27: {"name": "오딧세이 소드", "cost": 10000000, "succ_rate": 0.40, "base_sell_price": 15000000},
    28: {"name": "모자이칼", "cost": 0, "succ_rate": 0.15, "base_sell_price": 0},
    29: {"name": "화염에 달군 검", "cost": 0, "succ_rate": 0.0, "base_sell_price": 0}
}

# 상태 초기화
if 'level' not in st.session_state:
    st.session_state.level = 0
    st.session_state.sword_name = UPGRADE_TABLE[st.session_state.level]["name"]
    st.session_state.gold = 500000  # 초기 골드
    st.session_state.break_ticket = 0
    st.session_state.materials = {"국적불분명 철조각": 10, "타우의 뼈 부스러기": 5}
    st.session_state.message = ""

# 제작자 코드로 조정할 변수
if 'admin_code' not in st.session_state:
    st.session_state.admin_code = "ADMIN2025"
    st.session_state.is_admin = False

# 관리자의 코드 입력란
admin_code_input = st.text_input("관리자 코드 입력", type="password")

if admin_code_input == st.session_state.admin_code:
    st.session_state.is_admin = True
    st.session_state.message = "관리자 권한 활성화! 설정을 변경할 수 있습니다."

# 상태 UI
st.markdown(f"**현재 검:** {st.session_state.sword_name} +{st.session_state.level}")
st.markdown(f"**골드:** {st.session_state.gold:,}")
st.markdown(f"**방지권:** {st.session_state.break_ticket}")
st.markdown(f"**재료:** {', '.join([f'{item}: {st.session_state.materials[item]}' for item in st.session_state.materials])}")

# 제작자 코드로 강화 확률, 돈, 드랍률 조정
if st.session_state.is_admin:
    st.markdown("### 제작자 설정:")
    prob_change = st.slider("강화 확률 조정(0-100%)", 0, 100, 50)
    st.session_state.gold_multiplier = st.slider("골드 배율", 1, 10, 1)
    drop_rate_change = st.slider("드랍률 배율", 1, 10, 1)

    # 강화 확률 적용
    for i in range(len(UPGRADE_TABLE)):
        UPGRADE_TABLE[i]["succ_rate"] = prob_change / 100

    # 골드 배율 적용
    def get_adjusted_cost(level):
        return UPGRADE_TABLE[level]["cost"] * st.session_state.gold_multiplier

    st.session_state.message = "관리자 설정이 적용되었습니다!"

# 강화 버튼
if st.button("강화하기"):
    if st.session_state.gold >= get_adjusted_cost(st.session_state.level):
        if random.random() <= UPGRADE_TABLE[st.session_state.level]["succ_rate"]:
            st.session_state.level += 1
            st.session_state.sword_name = UPGRADE_TABLE[st.session_state.level]["name"]
            st.session_state.gold -= get_adjusted_cost(st.session_state.level)
            st.session_state.message = f"강화 성공! {st.session_state.sword_name} +{st.session_state.level}로 강화되었습니다."
        else:
            st.session_state.gold -= get_adjusted_cost(st.session_state.level)
            st.session_state.message = f"강화 실패! {UPGRADE_TABLE[st.session_state.level]['name']}의 강화에 실패했습니다."
    else:
        st.session_state.message = "골드가 부족합니다."

# 검 팔기 버튼
if st.button("검 팔기"):
    sell_price = UPGRADE_TABLE[st.session_state.level]["base_sell_price"]
    if st.session_state.level >= 10:
        sell_price *= 1.25  # 10강 이상은 판매 가격 25% 상승
    st.session_state.gold += sell_price
    st.session_state.sword_name = "낡은 단검"
    st.session_state.level = 0
    st.session_state.message = f"검을 팔고 {sell_price:,}골드를 얻었습니다. 다시 시작합니다."

# 상점 버튼: 방지권 구매
if st.button("상점 열기"):
    st.markdown("### 방지권 구매")
    buy_ticket = st.slider("구매할 방지권 수", 1, 10, 1)
    ticket_price = 2100000  # 기본 방지권 가격
    total_cost = buy_ticket * ticket_price

    if st.session_state.gold >= total_cost:
        st.session_state.gold -= total_cost
        st.session_state.break_ticket += buy_ticket
        st.session_state.message = f"{buy_ticket}개의 방지권을 구매했습니다. 총 {total_cost:,}골드를 사용했습니다."
    else:
        st.session_state.message = "골드가 부족합니다."

# 메시지 출력
if st.session_state.message:
    st.markdown(f"**{st.session_state.message}**")
