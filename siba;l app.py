import streamlit as st
import random

# 세션 상태 초기화
if 'gold' not in st.session_state:
    st.session_state.gold = 1000000  # 초기 금액
if 'level' not in st.session_state:
    st.session_state.level = 0  # 처음에는 0강
if 'sword_name' not in st.session_state:
    st.session_state.sword_name = "낡은 단검"
if 'message' not in st.session_state:
    st.session_state.message = ""
if 'break_protection' not in st.session_state:
    st.session_state.break_protection = 0  # 방지권 수 초기화
if 'used_codes' not in st.session_state:
    st.session_state.used_codes = []

# 사용된 코드들
st.title("강화 시스템")
st.write(f"현재 금액: {st.session_state.gold}원")
st.write(f"현재 무기: {st.session_state.sword_name}")
st.write(f"현재 단계: {st.session_state.level + 1}강")
st.write(f"방지권 수: {st.session_state.break_protection}")
st.write(f"메시지: {st.session_state.message}")

# 코드 입력 창
code_input = st.text_input("코드를 입력하세요 (1회용):")

# 코드 검증 함수
def check_code(code):
    valid_codes = {
        "CODE100": 100000,  # 코드가 맞으면 이만큼 금액 지급
        "BONUS500": 500000,
        "EXTRA1000": 1000000,
        "FREE200": 200000,
        "MAXBOOST": 5000000,
        "GIFT300": 300000,
        "STRENGTHBOOST": 1500000,
        "LUCKY700": 700000,
        "SURPRISE250": 250000,
        "SECRET400": 400000
    }
    
    if code in valid_codes and code not in st.session_state.used_codes:
        st.session_state.gold += valid_codes[code]  # 코드에 해당하는 금액 지급
        st.session_state.used_codes.append(code)  # 사용된 코드 목록에 추가
        st.session_state.message = f"코드 사용 성공! {valid_codes[code]}원이 지급되었습니다."
        return True
    else:
        st.session_state.message = "유효하지 않거나 이미 사용된 코드입니다."
        return False

# 코드 입력 후 처리
if code_input:
    check_code(code_input)  # 코드 검사하고 처리

# 강화 시스템 구현
UPGRADE_TABLE = {
    0: {"name": "낡은 단검", "cost": 500, "succ_rate": 1.0, "base_sell_price": 100},
    1: {"name": "쓸만한 단검", "cost": 500, "succ_rate": 0.98, "base_sell_price": 200},
    2: {"name": "견고한 단검", "cost": 1000, "succ_rate": 0.95, "base_sell_price": 500},
    3: {"name": "바이킹 소드", "cost": 2000, "succ_rate": 0.93, "base_sell_price": 1000},
    4: {"name": "불타는 검", "cost": 4000, "succ_rate": 0.90, "base_sell_price": 2000},
    5: {"name": "냉기의 소드", "cost": 7000, "succ_rate": 0.86, "base_sell_price": 6000},
    6: {"name": "양날 검", "cost": 10000, "succ_rate": 0.81, "base_sell_price": 15000},
    7: {"name": "심판자의 대검", "cost": 15000, "succ_rate": 0.75, "base_sell_price": 25000},
    8: {"name": "마력의 검", "cost": 22000, "succ_rate": 0.70, "base_sell_price": 50000},
    9: {"name": "타우 스워드", "cost": 30000, "succ_rate": 0.66, "base_sell_price": 90000},
    10: {"name": "형광검", "cost": 30000, "succ_rate": 0.62, "base_sell_price": 180000},
    11: {"name": "피묻은 검", "cost": 51000, "succ_rate": 0.61, "base_sell_price": 500000},
    12: {"name": "화염의 쌍검", "cost": 70000, "succ_rate": 0.54, "base_sell_price": 1000000},
    13: {"name": "불꽃 마검", "cost": 80000, "succ_rate": 0.50, "base_sell_price": 2000000},
    14: {"name": "마검 아포피스", "cost": 100000, "succ_rate": 0.49, "base_sell_price": 5000000},
    15: {"name": "데몬 배틀 엑스", "cost": 130000, "succ_rate": 0.46, "base_sell_price": 10000000},
    16: {"name": "투명 검", "cost": 170000, "succ_rate": 0.44, "base_sell_price": 20000000},
    17: {"name": "날렵한 용검", "cost": 220000, "succ_rate": 0.40, "base_sell_price": 44500000},
    18: {"name": "샤이니 소드", "cost": 300000, "succ_rate": 0.38, "base_sell_price": 72000000},
    19: {"name": "왕푸야샤", "cost": 400000, "succ_rate": 0.35, "base_sell_price": 120000000},
    20: {"name": "다색검", "cost": 650000, "succ_rate": 0.33, "base_sell_price": 240000000},
    21: {"name": "템페스트 골드", "cost": 1000000, "succ_rate": 0.30, "base_sell_price": 300000000},
    22: {"name": "샤프 워커", "cost": 1500000, "succ_rate": 0.27, "base_sell_price": 400000000},
    23: {"name": "피에로의 쌍검", "cost": 2000000, "succ_rate": 0.27, "base_sell_price": 550000000},
    24: {"name": "도룡도", "cost": 2500000, "succ_rate": 0.25, "base_sell_price": 750000000},
    25: {"name": "안 강해보이는 검", "cost": 3000000, "succ_rate": 0.35, "base_sell_price": 400000000},
    26: {"name": "메두사", "cost": 5000000, "succ_rate": 0.50, "base_sell_price": 1800000000},
    27: {"name": "오딧세이 소드", "cost": 10000000, "succ_rate": 0.40, "base_sell_price": 2500000000},
    28: {"name": "모자이칼", "cost": 0, "succ_rate": 0.15, "base_sell_price": 0},
    29: {"name": "화염에 달군 검", "cost": 0, "succ_rate": 0.0, "base_sell_price": 0}
}

# 대실패 확률 계산 함수 (1강부터 5%씩 올라가며, 20강 이상은 80%로 고정)
def get_failure_prob(level):
    if level < 1:
        return 0.01  # 1강은 1%
    elif level < 2:
        return 0.06  # 2강은 6%
    elif level < 3:
        return 0.11  # 3강은 11%
    elif level < 4:
        return 0.16  # 4강은 16%
    elif level < 5:
        return 0.21  # 5강은 21%
    elif level < 6:
        return 0.26  # 6강은 26%
    elif level < 7:
        return 0.31  # 7강은 31%
    elif level < 8:
        return 0.36  # 8강은 36%
    elif level < 9:
        return 0.41  # 9강은 41%
    elif level < 10:
        return 0.46  # 10강은 46%
    elif level < 11:
        return 0.51  # 11강은 51%
    elif level < 12:
        return 0.56  # 12강은 56%
    elif level < 13:
        return 0.61  # 13강은 61%
    elif level < 14:
        return 0.66  # 14강은 66%
    elif level < 15:
        return 0.71  # 15강은 71%
    elif level < 16:
        return 0.76  # 16강은 76%
    elif level < 17:
        return 0.81  # 17강은 81%
    elif level < 18:
        return 0.86  # 18강은 86%
    elif level < 19:
        return 0.91  # 19강은 91%
    elif level < 20:
        return 0.96  # 20강은 96%
    else:
        return 0.8  # 20강 이상은 대실패 확률이 80%

# 판매 버튼
def sell_weapon():
    current_level = st.session_state.level
    sell_price = UPGRADE_TABLE[current_level]["base_sell_price"]
    
    st.session_state.gold += sell_price
    st.session_state.sword_name = "낡은 단검"
    st.session_state.level = 0
    st.session_state.message = f"무기가 판매되었습니다. {sell_price}원을 획득하였습니다."

# 강화 함수
def upgrade_weapon():
    current_level = st.session_state.level
    weapon_data = UPGRADE_TABLE[current_level]
    cost = weapon_data["cost"]
    
    # 비용 차감
    if st.session_state.gold < cost:
        st.session_state.message = "금액이 부족합니다."
        return
    
    st.session_state.gold -= cost
    
    # 확률 계산
    success_rate = weapon_data["succ_rate"]
    fail_rate = get_failure_prob(current_level)
    total_rate = success_rate + fail_rate
    
    rand = random.random()
    if rand < success_rate:
        # 성공
        st.session_state.level += 1
        st.session_state.sword_name = weapon_data["name"]
        st.session_state.message = f"강화 성공! {st.session_state.sword_name} {current_level + 1}강!"
    elif rand < total_rate:
        # 실패
        st.session_state.message = f"강화 실패! {st.session_state.sword_name} {current_level + 1}강 유지."
    else:
        # 대실패
        if st.session_state.break_protection > 0:
            st.session_state.message = "대실패! 방지권을 사용하시겠습니까?"
            st.session_state.protection_ui = True  # 방지권 UI 활성화
        else:
            st.session_state.level = 0
            st.session_state.sword_name = "낡은 단검"
            st.session_state.message = "대실패! 무기가 파괴되었습니다. 다시 시작합니다."
            st.session_state.protection_ui = False

# 강화 버튼
if st.button("강화"):
    upgrade_weapon()

# 판매 버튼
if st.button("무기 판매"):
    sell_weapon()

# 방지권 사용 UI
if 'protection_ui' in st.session_state and st.session_state.protection_ui:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("방지권 사용"):
            if st.session_state.break_protection > 0:
                st.session_state.break_protection -= 1
                st.session_state.message = "방지권 사용 성공! 대실패를 방지했습니다."
                st.session_state.protection_ui = False  # UI 사라짐
                st.session_state.level += 1  # 대실패 대신 강화 성공
                st.session_state.sword_name = UPGRADE_TABLE[st.session_state.level]["name"]
            else:
                st.session_state.message = "방지권이 부족합니다."
    
    with col2:
        if st.button("다시 강화"):
            st.session_state.protection_ui = False  # UI 사라짐
            st.session_state.message = "강화를 다시 시도합니다."

# 상점 UI
if st.button("상점"):
    with st.container():
        st.subheader("상점")
        if st.button("방지권 1개 구입 (2,100,000원)"):
            if st.session_state.gold >= 2100000:
                st.session_state.gold -= 2100000
                st.session_state.break_protection += 1
                st.session_state.message = "방지권을 1개 구입했습니다."
            else:
                st.session_state.message = "금액이 부족합니다."

        if st.button("방지권 3개 구입 (6,000,000원)"):
            if st.session_state.gold >= 6000000:
                st.session_state.gold -= 6000000
                st.session_state.break_protection += 3
                st.session_state.message = "방지권을 3개 구입했습니다."
            else:
                st.session_state.message = "금액이 부족합니다."

# 결과 출력
st.write(st.session_state.message)
