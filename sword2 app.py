import streamlit as st
import random

# 게임 데이터 정의 (드랍 재료 추가)
UPGRADE_TABLE = {
    0: {"name": "낡은 단검", "cost": 500, "succ_rate": 1.0, "base_sell_price": 500, "required_materials": []},
    1: {"name": "쓸만한 단검", "cost": 500, "succ_rate": 0.98, "base_sell_price": 500, "required_materials": []},
    2: {"name": "견고한 단검", "cost": 1000, "succ_rate": 0.95, "base_sell_price": 1000, "required_materials": []},
    3: {"name": "바이킹 소드", "cost": 2000, "succ_rate": 0.93, "base_sell_price": 2000, "required_materials": []},
    4: {"name": "불타는 검", "cost": 4000, "succ_rate": 0.90, "base_sell_price": 4000, "required_materials": []},
    5: {"name": "냉기의 소드", "cost": 7000, "succ_rate": 0.86, "base_sell_price": 7000, "required_materials": []},
    6: {"name": "양날 검", "cost": 10000, "succ_rate": 0.81, "base_sell_price": 10000, "required_materials": []},
    7: {"name": "심판자의 대검", "cost": 15000, "succ_rate": 0.75, "base_sell_price": 15000, "required_materials": []},
    8: {"name": "마력의 검", "cost": 22000, "succ_rate": 0.70, "base_sell_price": 22000, "required_materials": []},
    9: {"name": "타우 스워드", "cost": 30000, "succ_rate": 0.66, "base_sell_price": 30000, "required_materials": []},
    10: {"name": "형광검", "cost": 30000, "succ_rate": 0.62, "base_sell_price": 45000, "required_materials": []},
    11: {"name": "피묻은 검", "cost": 51000, "succ_rate": 0.61, "base_sell_price": 76500, "required_materials": []},
    12: {"name": "화염의 쌍검", "cost": 70000, "succ_rate": 0.54, "base_sell_price": 105000, "required_materials": []},
    13: {"name": "불꽃 마검", "cost": 80000, "succ_rate": 0.50, "base_sell_price": 120000, "required_materials": []},
    14: {"name": "마검 아포피스", "cost": 100000, "succ_rate": 0.49, "base_sell_price": 150000, "required_materials": []},
    15: {"name": "데몬 배틀 엑스", "cost": 130000, "succ_rate": 0.46, "base_sell_price": 195000, "required_materials": []},
    16: {"name": "투명 검", "cost": 170000, "succ_rate": 0.44, "base_sell_price": 255000, "required_materials": []},
    17: {"name": "날렵한 용검", "cost": 220000, "succ_rate": 0.40, "base_sell_price": 330000, "required_materials": []},
    18: {"name": "샤이니 소드", "cost": 300000, "succ_rate": 0.38, "base_sell_price": 450000, "required_materials": []},
    19: {"name": "왕푸야샤", "cost": 400000, "succ_rate": 0.35, "base_sell_price": 600000, "required_materials": []},
    20: {"name": "다색검", "cost": 650000, "succ_rate": 0.33, "base_sell_price": 975000, "required_materials": [("사악한 영혼", 4)]},
    21: {"name": "템페스트 골드", "cost": 1000000, "succ_rate": 0.30, "base_sell_price": 1500000, "required_materials": [("사악한 영혼", 6)]},
    22: {"name": "샤프 워커", "cost": 1500000, "succ_rate": 0.27, "base_sell_price": 2250000, "required_materials": [("도끼 가루", 6)]},
    23: {"name": "피에로의 쌍검", "cost": 2000000, "succ_rate": 0.25, "base_sell_price": 3000000, "required_materials": [("투명 물질", 4)]},
    24: {"name": "도룡도", "cost": 2500000, "succ_rate": 0.23, "base_sell_price": 3750000, "required_materials": [("사악한 영혼", 8)]},
    25: {"name": "안 강해보이는 검", "cost": 3000000, "succ_rate": 0.35, "base_sell_price": 4500000, "required_materials": [("투명 물질", 6)]},
    26: {"name": "메두사", "cost": 5000000, "succ_rate": 0.50, "base_sell_price": 7500000, "required_materials": [("사악한 영혼", 10)]},
    27: {"name": "오딧세이 소드", "cost": 10000000, "succ_rate": 0.40, "base_sell_price": 15000000, "required_materials": [("불꽃마검 손잡이", 2)]},
    28: {"name": "모자이칼", "cost": 0, "succ_rate": 0.15, "base_sell_price": 0, "required_materials": [("국적불분명 철조각", 12)]},
    29: {"name": "화염에 달군 검", "cost": 0, "succ_rate": 0.0, "base_sell_price": 0, "required_materials": [("타우의 뼈 부스러기", 8)]}
}

# 드랍 재료 리스트
DROP_MATERIALS = [
    ("국적불분명 철조각", 1),
    ("타우의 뼈 부스러기", 1),
    ("사악한 영혼", 1),
    ("도끼 가루", 1),
    ("투명 물질", 1)
]

# 게임 상태 초기화
if 'level' not in st.session_state:
    st.session_state.level = 0
    st.session_state.sword_name = UPGRADE_TABLE[st.session_state.level]["name"]
    st.session_state.gold = 500000  # 초기 골드
    st.session_state.break_ticket = 0
    st.session_state.materials = {"국적불분명 철조각": 10, "타우의 뼈 부스러기": 5, "사악한 영혼": 2, "도끼 가루": 3, "투명 물질": 1, "불꽃마검 손잡이": 0}
    st.session_state.message = ""
    st.session_state.dropped_materials = []

# 강화 실패 시 드랍되는 재료 처리
def handle_upgrade_failure(level):
    if level >= 10 and level <= 15:  # 10강부터 15강까지
        drop_chance = 0.2  # 실패 확률이 20%일 때 재료 드랍
        if random.random() < drop_chance:
            num_items = random.randint(1, 3)  # 드랍되는 재료 수 (1~3개)
            dropped_items = random.sample(DROP_MATERIALS, num_items)
            for item, qty in dropped_items:
                st.session_state.materials[item] += qty
                st.session_state.dropped_materials.append(f"{item} ({qty}개)")
            st.session_state.message += f"\n**강화 실패!** 드랍된 재료: {', '.join([f'{item} ({qty}개)' for item, qty in dropped_items])}"

# 강화 버튼 클릭 시 처리
if st.button("강화"):
    sword_data = UPGRADE_TABLE[st.session_state.level]
    success = random.random() < sword_data["succ_rate"]

    if success:
        st.session_state.level += 1
        st.session_state.sword_name = UPGRADE_TABLE[st.session_state.level]["name"]
        st.session_state.message = f"강화 성공! {st.session_state.sword_name} +{st.session_state.level}으로 업그레이드!"
    else:
        handle_upgrade_failure(st.session_state.level)
        st.session_state.message = f"강화 실패! {st.session_state.sword_name} +{st.session_state.level} 상태 유지."

# 상점에서 방지권 구입
if st.button("상점 열기"):
    if st.session_state.gold >= 1000000:
        st.session_state.gold -= 1000000
        st.session_state.break_ticket += 1
        st.session_state.message = "방지권을 1개 구입했습니다!"

# 팔기 버튼 클릭 처리
if st.button("무기 팔기"):
    sell_price = UPGRADE_TABLE[st.session_state.level]["base_sell_price"]
    st.session_state.gold += sell_price
    st.session_state.message = f"무기를 팔아서 {sell_price:,} 골드를 얻었습니다."

# 메시지 출력
st.markdown(f"**결과 메시지:** {st.session_state.message}")

# 상태 UI
st.markdown(f"**현재 검:** {st.session_state.sword_name} +{st.session_state.level}")
st.markdown(f"**골드:** {st.session_state.gold:,}")
st.markdown(f"**방지권:** {st.session_state.break_ticket}")
st.markdown(f"**재료:** {', '.join([f'{item}: {st.session_state.materials[item]}' for item in st.session_state.materials])}")
st.markdown(f"**드랍된 재료:** {', '.join(st.session_state.dropped_materials)}" if st.session_state.dropped_materials else "드랍된 재료 없음.")
