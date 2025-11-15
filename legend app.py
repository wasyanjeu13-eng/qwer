import streamlit as st
import random

# 강화 데이터 (기존 데이터 사용)
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

# 무기 강화 함수
def upgrade_weapon():
    current_level = st.session_state.level
    weapon_data = UPGRADE_TABLE[current_level]
    cost = weapon_data["cost"]
    
    # 비용 차감
    if st.session_state.gold < cost:
        st.session_state.message = "돈이 부족합니다!"
        return
    
    # 돈 차감
    st.session_state.gold -= cost
    
    # 실패 확률 계산 (단계가 올라갈수록 실패 확률 증가)
    if current_level < 20:
        fail_rate = 0.05 + (current_level * 0.05)  # 5%부터 시작, 단계가 올라갈수록 실패 확률 증가
        big_fail_rate = 0.01 + (current_level * 0.05)  # 대실패 확률 (작게 시작해 단계가 올라가며 증가)
    else:
        fail_rate = 0.02 + (current_level * 0.01)  # 20단계 이상에서의 실패 확률
        big_fail_rate = 0.8  # 20단계 이상부터 대실패 확률 80%

    # 확률 총합이 100%가 되도록 조정
    success_rate = 1.0 - (fail_rate + big_fail_rate)
    
    # 랜덤 값으로 성공, 실패, 대실패 결정
    rand = random.random()
    
    if rand < big_fail_rate:  # 대실패: 무기가 터짐
        st.session_state.level = 0  # 무기가 터지면 0강으로 초기화
        st.session_state.sword_name = "무기 파괴"
        st.session_state.message = f"{weapon_data['name']} 강화 대실패! 무기가 파괴되었습니다."
    elif rand < fail_rate + big_fail_rate:  # 실패: 강화가 실패, 단계가 그대로
        st.session_state.message = f"{weapon_data['name']} 강화 실패! 강화 단계가 그대로 유지됩니다."
    else:  # 성공: 강화 성공
        st.session_state.level += 1  # 강화 성공 시 레벨 증가
        st.session_state.sword_name = UPGRADE_TABLE[st.session_state.level]["name"]
        st.session_state.message = f"{st.session_state.sword_name} 강화 성공!"

# 무기 팔기
def sell_weapon():
    current_level = st.session_state.level
    weapon_data = UPGRADE_TABLE[current_level]
    sell_price = weapon_data["base_sell_price"]
    st.session_state.gold += sell_price  # 팔고 얻은 돈을 골드에 추가
    st.session_state.level = 0  # 무기를 팔면 0강으로 되돌림
    st.session_state.sword_name = UPGRADE_TABLE[st.session_state.level]["name"]
    st.session_state.message = f"{weapon_data['name']}을(를) 팔았습니다. 0강으로 돌아갔습니다."

# 상점: 방지권 구매
def buy_break_ticket():
    if st.session_state.gold >= 2000000:  # 방지권 가격 설정
        st.session_state.gold -= 2000000
        st.session_state.break_ticket += 1
        st.session_state.message = "방지권을 구입했습니다!"
    else:
        st.session_state.message = "골드가 부족합니다!"
