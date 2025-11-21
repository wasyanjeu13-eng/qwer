import streamlit as st
import random
import re

# --- 1. 상수 및 데이터 정의 ---

INITIAL_MONEY = 300000  # 시작 소지금
INITIAL_LEVEL = 0
SECRET_DEBUG_CODE = "DEVMODE" # ⭐ 제작자 전용 비밀 코드
DEBUG_GOLD_AMOUNT = 1000000000 # 10억
DEBUG_MAT_QTY = 100
SWORD_SELL_MULTIPLIER = 1.20 # ⭐ 수정됨: 업그레이드 가격의 120% 이익을 보고 판매
MAX_LEVEL_SELL_PRICE = 10000000000 # +29 화염에 달군 검의 고정 판매가 (100억 Gold)

SWORD_NAMES = {
    0: '낡은 단검', 1: '쓸만한 단검', 2: '견고한 단검', 3: '바이킹 소드', 4: '불타는 검', 5: '냉기의 소드',
    6: '양날 검', 7: '심판자의 대검', 8: '마력의 검', 9: '타우 스워드', 10: '형광검', 11: '피묻은 검',
    12: '화염의 쌍검', 13: '불꽃 마검', 14: '마검 아포피스', 15: '데몬 배틀 엑스', 16: '투명 검', 
    17: '날렵한 용검', 18: '샤이니 소드', 19: '왕푸야샤[보관필요]', 20: '다색검', 21: '템페스트 골드[보관필요]', 
    22: '샤프 워커[보관필요]', 23: '피에로의 쌍검', 24: '도룡도', 25: '안 강해보이는 검[하드버그]', 
    26: '메두사', 27: '오딧세이 소드', 28: '모자이칼', 29: '화염에 달군 검'
}

# 강화 요구사항 데이터 (Level 21 '템페스트 골드'부터 재료 필요)
ENHANCE_REQUIREMENTS = {
    0: {'name': SWORD_NAMES[1], 'rate': 1.00, 'gold': 0, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    1: {'name': SWORD_NAMES[2], 'rate': 0.98, 'gold': 200, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    2: {'name': SWORD_NAMES[3], 'rate': 0.95, 'gold': 500, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    3: {'name': SWORD_NAMES[4], 'rate': 0.93, 'gold': 1000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    4: {'name': SWORD_NAMES[5], 'rate': 0.90, 'gold': 2000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    5: {'name': SWORD_NAMES[6], 'rate': 0.86, 'gold': 6000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    6: {'name': SWORD_NAMES[7], 'rate': 0.81, 'gold': 15000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    7: {'name': SWORD_NAMES[8], 'rate': 0.75, 'gold': 25000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    8: {'name': SWORD_NAMES[9], 'rate': 0.70, 'gold': 50000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    9: {'name': SWORD_NAMES[10], 'rate': 0.66, 'gold': 90000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    10: {'name': SWORD_NAMES[11], 'rate': 0.62, 'gold': 180000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    11: {'name': SWORD_NAMES[12], 'rate': 0.61, 'gold': 500000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    12: {'name': SWORD_NAMES[13], 'rate': 0.54, 'gold': 1000000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    13: {'name': SWORD_NAMES[14], 'rate': 0.50, 'gold': 2000000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    14: {'name': SWORD_NAMES[15], 'rate': 0.49, 'gold': 5000000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    15: {'name': SWORD_NAMES[16], 'rate': 0.46, 'gold': 10000000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    16: {'name': SWORD_NAMES[17], 'rate': 0.44, 'gold': 20000000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    17: {'name': SWORD_NAMES[18], 'rate': 0.40, 'gold': 44500000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': None},
    18: {'name': SWORD_NAMES[19], 'rate': 0.38, 'gold': 72000000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': '보관필요'},
    19: {'name': SWORD_NAMES[20], 'rate': 0.35, 'gold': 120000000, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': '보관필요'},
    20: {'name': SWORD_NAMES[21], 'rate': 0.33, 'gold': 240000000, 'mat_qty': 15, 'mat_name': '알 수 없는 재료B', 'item_req': None, 'note': None}, # ⭐ 템페스트 골드부터 재료 필요
    21: {'name': SWORD_NAMES[22], 'rate': 0.30, 'gold': 300000000, 'mat_qty': 17, 'mat_name': '알 수 없는 재료B', 'item_req': '왕푸야샤 1자루', 'note': '보관필요'}, 
    22: {'name': SWORD_NAMES[23], 'rate': 0.27, 'gold': 400000000, 'mat_qty': 20, 'mat_name': '알 수 없는 재료B', 'item_req': '템페스트 골드 2자루', 'note': '보관필요'}, 
    23: {'name': SWORD_NAMES[24], 'rate': 0.27, 'gold': 550000000, 'mat_qty': 22, 'mat_name': '알 수 없는 재료B', 'item_req': '사악한 영혼 12개', 'note': None}, 
    24: {'name': SWORD_NAMES[25], 'rate': 0.25, 'gold': 750000000, 'mat_qty': 23, 'mat_name': '알 수 없는 재료B', 'item_req': '샤프 워커 1자루', 'note': None}, 
    25: {'name': SWORD_NAMES[26], 'rate': 0.35, 'gold': 400000000, 'mat_qty': 23, 'mat_name': '알 수 없는 재료B', 'item_req': '도끼 가루 15개', 'note': '하드버그'}, 
    26: {'name': SWORD_NAMES[27], 'rate': 0.50, 'gold': 1800000000, 'mat_qty': 0, 'mat_name': '파괴방지권 불가', 'item_req': None, 'note': None},
    27: {'name': SWORD_NAMES[28], 'rate': 0.40, 'gold': 2500000000, 'mat_qty': 0, 'mat_name': '파괴방지권 불가', 'item_req': '투명 물질 2개', 'note': None},
    28: {'name': SWORD_NAMES[29], 'rate': 0.15, 'gold': 0, 'mat_qty': 0, 'mat_name': '파괴방지권 불가', 'item_req': None, 'note': None},
    29: {'name': SWORD_NAMES[29], 'rate': 1.00, 'gold': 0, 'mat_qty': 0, 'mat_name': None, 'item_req': None, 'note': '최고 레벨 달성'},
}

# 강화에 필요한 모든 재료 및 아이템 목록 정의
ALL_MATERIALS_NAMES = ['국적불분명 철조각', '타우의 뼈 부스러기', '빛 바랜 형광물질', '스위스산 철조각', 
                       '불꽃마검 손잡이', '사악한 영혼', '도끼 가루', '투명 물질', 
                       '알 수 없는 재료A', '알 수 없는 재료B']
ALL_ITEM_NAMES = ['왕푸야샤', '템페스트 골드', '샤프 워커']

# 상점 아이템 및 가격
STORE_ITEMS = {
    '파괴 방지권': 10000000 
}

# --- 2. Streamlit Session State 및 헬퍼 함수 ---

def initialize_session_state():
    """앱 시작 시 또는 리셋 시 세션 상태를 초기화합니다."""
    if 'money' not in st.session_state: st.session_state.money = INITIAL_MONEY
    if 'level' not in st.session_state: st.session_state.level = INITIAL_LEVEL
    if 'message' not in st.session_state: st.session_state.message = "강화를 시작해보세요! ⚔️ 무기를 팔아 골드를 얻을 수 있습니다."
    if 'is_debug_mode' not in st.session_state: st.session_state.is_debug_mode = False
    if 'inventory' not in st.session_state:
        st.session_state.inventory = {name: 0 for name in ALL_MATERIALS_NAMES + ALL_ITEM_NAMES + list(STORE_ITEMS.keys())}
        st.session_state.inventory['낡은 단검'] = 1 
    if 'use_protection_prompt' not in st.session_state: st.session_state.use_protection_prompt = False
    if 'failed_level' not in st.session_state: st.session_state.failed_level = 0 

def get_current_sword_name():
    return SWORD_NAMES.get(st.session_state.level, f"미지의 검 (+{st.session_state.level})")

def get_upgrade_cost(level):
    """특정 레벨에서 다음 레벨로 가는 골드 비용을 반환합니다."""
    # Level 29는 ENHANCE_REQUIREMENTS의 마지막 레벨이므로, Level 28의 다음 강화 비용을 가져옵니다.
    if level >= len(ENHANCE_REQUIREMENTS) - 1:
        return 0 # 최고 레벨은 업그레이드 비용이 없다고 간주

    req = ENHANCE_REQUIREMENTS.get(level)
    return req['gold'] if req else 0

def get_sell_price(current_level):
    """현재 검의 판매 가격을 계산합니다."""
    
    if current_level >= len(ENHANCE_REQUIREMENTS) - 1: # 최고 레벨 (+29 화염에 달군 검)
        return MAX_LEVEL_SELL_PRICE

    # 다음 레벨의 업그레이드 비용을 기준으로 120% 이익을 붙여 판매
    upgrade_cost = get_upgrade_cost(current_level)
    sell_price = upgrade_cost * SWORD_SELL_MULTIPLIER

    # Level 0은 팔지 않거나, 최소 가격 설정
    if current_level == 0:
        return 100 

    return int(sell_price)

def sell_sword():
    """현재 검을 판매하고 골드를 획득합니다."""
    current_level = st.session_state.level
    current_name = get_current_sword_name()
    
    # 낡은 단검이 마지막 하나 남았는지 확인 (SWORD_NAMES[0] == '낡은 단검')
    if current_level == 0 and st.session_state.inventory.get(SWORD_NAMES[0], 0) == 1:
        st.session_state.message = "🚨 **[판매 실패]** 낡은 단검은 마지막 하나 남았기 때문에 팔 수 없습니다."
        return
    
    sell_price = get_sell_price(current_level)
    
    # 인벤토리에서 현재 검 소모 및 레벨 하락 처리
    current_name_clean = current_name.replace('[보관필요]', '').replace('[하드버bug]', '').strip()

    # 인벤토리에서 현재 검을 소모합니다. (주로 낡은 단검, 또는 재료로 쓰이는 검)
    item_to_consume = current_name_clean if current_name_clean in st.session_state.inventory else SWORD_NAMES[current_level]

    if st.session_state.inventory.get(item_to_consume, 0) > 0:
        st.session_state.inventory[item_to_consume] -= 1
        st.session_state.money += sell_price
        
        # 판매 후 레벨 1 하락 (이전 무기로 돌아감)
        st.session_state.level -= 1 
        if st.session_state.level < 0:
            st.session_state.level = 0 # 0 미만 방지
            st.session_state.inventory[SWORD_NAMES[0]] = st.session_state.inventory.get(SWORD_NAMES[0], 0) + 1 # 낡은 단검 획득
        
        st.session_state.message = f"✅ **[판매 성공]** **+{current_level} {current_name}**을(를) **{sell_price:,} Gold**에 판매했습니다."
    else:
        st.session_state.message = "🚨 **[판매 실패]** 인벤토리에 현재 검이 없습니다. (새로 강화하거나 낡은 단검을 다시 획득해야 합니다.)"
        
def parse_item_requirement(req_str):
    if not req_str: return None
    match = re.search(r'(.+)\s(\d+)자루|(.+)\s(\d+)개', req_str)
    if match:
        name = match.group(1) or match.group(3)
        qty = int(match.group(2) or match.group(4))
        return {'name': name.strip(), 'qty': qty}
    return None

def check_materials(req):
    """강화에 필요한 재료가 충분한지 확인합니다."""
    mat_qty, mat_name, item_req_str = req['mat_qty'], req['mat_name'], req['item_req']

    if mat_name and '불가' not in mat_name and st.session_state.inventory.get(mat_name, 0) < mat_qty:
        return False, f"🚨 **[강화 실패]** 재료 **{mat_name}** ({mat_qty}개)가 부족합니다."

    if item_req_str:
        item_req = parse_item_requirement(item_req_str)
        if item_req and st.session_state.inventory.get(item_req['name'], 0) < item_req['qty']:
             return False, f"🚨 **[강화 실패]** 기본 아이템 **{item_req['name']}** ({item_req['qty']}개)가 부족합니다."
    
    return True, None

def consume_materials(req):
    """강화 재료를 소모합니다."""
    mat_qty, mat_name, item_req_str = req['mat_qty'], req['mat_name'], req['item_req']
    
    if mat_name and '불가' not in mat_name:
        st.session_state.inventory[mat_name] -= mat_qty
    
    if item_req_str:
        item_req = parse_item_requirement(item_req_str)
        if item_req and item_req['name'] in st.session_state.inventory:
            st.session_state.inventory[item_req['name']] = max(0, st.session_state.inventory[item_req['name']] - item_req['qty'])

def enhance_sword_core(use_protection=False):
    """강화 실패 후 방지권 사용 여부에 따른 최종 로직을 처리합니다."""
    current_level = st.session_state.level # failed_level이 들어있음
    req = ENHANCE_REQUIREMENTS.get(current_level)
    
    # 실패 로직
    fail_message = f"💥 **[강화 실패]** 레벨이 하락하거나 무기가 파괴됩니다."
    
    # 방지권 사용/미사용 처리
    if use_protection:
        # 방지권 사용 -> 레벨 유지 (파괴 방지권 소모)
        st.session_state.inventory['파괴 방지권'] -= 1
        st.session_state.message = f"{fail_message} 🛡️ **파괴 방지권**이 소모되어 **레벨이 유지**되었습니다. 현재 레벨: +{current_level} ({get_current_sword_name()})"
        return

    # 방지권 미사용 또는 불가능 레벨: 파괴/하락
    if current_level >= 6: 
        # 레벨 6 이상: 파괴 (Level 0으로 하락)
        
        # 파괴된 검 인벤토리에서 제거 (재료로 쓰이는 아이템)
        prev_name_clean = SWORD_NAMES[current_level].replace('[보관필요]', '').replace('[하드버bug]', '').strip()
        if prev_name_clean in ALL_ITEM_NAMES:
             st.session_state.inventory[prev_name_clean] = max(0, st.session_state.inventory[prev_name_clean] - 1)
        
        st.session_state.level = INITIAL_LEVEL
        st.session_state.inventory[SWORD_NAMES[INITIAL_LEVEL]] = st.session_state.inventory.get(SWORD_NAMES[INITIAL_LEVEL], 0) + 1 # 낡은 단검 획득
        st.session_state.message = f"{fail_message} 💣 **무기가 터져서** **{SWORD_NAMES[INITIAL_LEVEL]}**({st.session_state.level})로 돌아갔습니다!"
    elif current_level >= 2:
        # 레벨 2~5: 레벨 1 하락
        new_level = current_level - 1
        st.session_state.level = new_level
        st.session_state.message = f"{fail_message} ⬇️ 레벨이 1 하락하여 현재 레벨: **+{new_level}** ({SWORD_NAMES[new_level]})"
    else:
        # 레벨 0~1: 레벨 유지
        st.session_state.message = f"{fail_message} 🛡️ 다행히 레벨이 유지되었습니다. 현재 레벨: **+{current_level}** ({get_current_sword_name()})"
        

def enhance_success(new_level, req):
    """강화 성공 시 상태를 업데이트합니다."""
    
    current_level = st.session_state.level
    st.session_state.level = new_level
    
    # 이전 검 소모 및 새 검 획득 로직
    prev_name_clean = SWORD_NAMES[current_level].replace('[보관필요]', '').replace('[하드버bug]', '').strip()
    if prev_name_clean not in ALL_ITEM_NAMES and current_level > 0:
        if prev_name_clean in st.session_state.inventory:
            st.session_state.inventory[prev_name_clean] = max(0, st.session_state.inventory[prev_name_clean] - 1)
        
    current_sword_name_clean = req['name'].replace('[보관필요]', '').replace('[하드버bug]', '').strip()
    if current_sword_name_clean in ALL_ITEM_NAMES:
        st.session_state.inventory[current_sword_name_clean] = st.session_state.inventory.get(current_sword_name_clean, 0) + 1

    st.session_state.message = f"🎉 **[강화 성공!]** 검의 레벨이 **+{new_level}** ({req['name']})이(가) 되었습니다. (확률: {req['rate'] * 100:.1f}%)"

def enhance_sword_start():
    """강화 전 검사 및 소모를 담당하고, 성공 또는 실패 시 로직을 분기합니다."""
    current_level = st.session_state.level
    
    if current_level >= len(ENHANCE_REQUIREMENTS) - 1:
        st.session_state.message = "🎉 **[강화 달성]** 이미 최고 레벨의 검입니다!"
        return

    req = ENHANCE_REQUIREMENTS.get(current_level)
    cost_gold = req['gold']
    protection_impossible = '파괴방지권 불가' in (req['mat_name'] or '')
    
    # 1. 비용 및 재료 확인
    if st.session_state.money < cost_gold:
        st.session_state.message = f"🚨 **[강화 실패]** 골드({cost_gold:,} Gold)가 부족합니다!"
        return
    
    can_enhance, error_message = check_materials(req)
    if not can_enhance:
        st.session_state.message = error_message
        return

    # 2. 비용 및 재료 차감 (실패 여부와 관계없이 소모)
    st.session_state.money -= cost_gold
    consume_materials(req)

    # 3. 강화 시도 (성공/실패 판정)
    if random.random() < req['rate']:
        # 성공
        enhance_success(current_level + 1, req)
    else:
        # 실패
        st.session_state.failed_level = current_level
        
        # Level 6 이상에서 파괴 가능하며, 방지권 사용이 가능하고, 방지권을 소지하고 있을 때 프롬프트 표시
        if current_level >= 6 and not protection_impossible and st.session_state.inventory.get('파괴 방지권', 0) > 0:
            st.session_state.use_protection_prompt = True
            st.session_state.message = f"💥 **[강화 실패]** 무기가 파괴될 위험이 있습니다! 방지권을 사용하시겠습니까?"
        else:
            # 방지권 조건 미충족 시 즉시 파괴/하락 로직 실행
            enhance_sword_core(use_protection=False)
            
def handle_protection_choice(choice):
    """방지권 사용 여부 선택을 처리합니다."""
    failed_level = st.session_state.failed_level
    
    # 실패 레벨을 현재 레벨로 설정 (로직 처리를 위해)
    st.session_state.level = failed_level
    
    if choice == 'yes':
        # 방지권 사용 로직 실행
        enhance_sword_core(use_protection=True)
    else:
        # 방지권 미사용 로직 실행 (파괴 또는 레벨 하락)
        enhance_sword_core(use_protection=False)
    
    st.session_state.use_protection_prompt = False # UI 제거

    # 결과 업데이트를 위해 Rerun
    st.experimental_rerun()

def buy_item(item_name, price):
    if st.session_state.money < price:
        st.session_state.message = f"🚨 **[구매 실패]** 돈이 부족합니다. ({price:,} Gold 필요)"
        return

    st.session_state.money -= price
    st.session_state.inventory[item_name] = st.session_state.inventory.get(item_name, 0) + 1
    st.session_state.message = f"✅ **{item_name}** 1개를 {price:,} Gold에 구매했습니다. (재고: {st.session_state.inventory[item_name]}개)"

def reset_game():
    st.session_state.clear()
    initialize_session_state()
    st.experimental_rerun()

def debug_gain_gold():
    st.session_state.money += DEBUG_GOLD_AMOUNT
    st.session_state.message = f"✅ **[디버그]** {DEBUG_GOLD_AMOUNT:,} Gold를 획득했습니다."

def debug_gain_all_items():
    for name in ALL_MATERIALS_NAMES + ALL_ITEM_NAMES + list(STORE_ITEMS.keys()):
        st.session_state.inventory[name] = st.session_state.inventory.get(name, 0) + DEBUG_MAT_QTY
    st.session_state.message = f"✅ **[디버그]** 모든 재료/아이템을 {DEBUG_MAT_QTY}개씩 획득했습니다."

def acquire_material(material_name):
    st.session_state.inventory[material_name] = st.session_state.inventory.get(material_name, 0) + 1
    st.session_state.message = f"✨ **{material_name}** 1개를 획득했습니다!"


# --- 3. Streamlit UI 구성 ---

def main():
    initialize_session_state()

    st.set_page_config(page_title="검 강화하기 시뮬레이터", layout="wide")
    st.title("🔥 검 강화하기 시뮬레이터 (판매 비용 120% 적용)")
    st.markdown("---")
    
    current_level = st.session_state.level
    
    # 1. 제작자 전용 코드 입력 및 디버그 모드 토글
    with st.expander("🛠️ 제작자 전용 메뉴 (DEBUG)", expanded=st.session_state.is_debug_mode):
        input_code = st.text_input("디버그 활성화 코드 입력", type="password", key='debug_code_input')
        
        if input_code == SECRET_DEBUG_CODE:
            st.session_state.is_debug_mode = True
            st.success("✅ 디버그 모드가 활성화되었습니다!")
        elif st.session_state.is_debug_mode and input_code != SECRET_DEBUG_CODE:
             st.session_state.is_debug_mode = False
             st.warning("디버그 모드가 비활성화되었습니다.")

        if st.session_state.is_debug_mode:
            debug_col1, debug_col2 = st.columns(2)
            with debug_col1:
                if st.button(f"⚡ 골드 무한 획득 (+{DEBUG_GOLD_AMOUNT:,} Gold)", use_container_width=True):
                    debug_gain_gold()
            with debug_col2:
                if st.button(f"💎 모든 재료 {DEBUG_MAT_QTY}개 획득", use_container_width=True):
                    debug_gain_all_items()

    # 2. 상단 정보 표시 영역
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric(label="✨ 현재 강화 레벨", value=f"+{current_level}")
        st.caption(f"**{get_current_sword_name()}**")
    
    with col2:
        st.metric(label="💰 소지금 (Gold)", value=f"{st.session_state.money:,}")
        
    st.markdown("---")
    
    # 3. 강화 실패 시 방지권 사용 여부 프롬프트 UI
    if st.session_state.use_protection_prompt:
        st.error("🚨 **[무기 파괴 위험!]** 강화에 실패했습니다. 무기가 파괴될 위험이 있습니다.")
        st.warning(f"🛡️ **파괴 방지권**을 사용하시겠습니까? (보유: {st.session_state.inventory.get('파괴 방지권', 0)}개)")
        
        prompt_col1, prompt_col2 = st.columns(2)
        with prompt_col1:
            if st.button("✅ 네, 방지권을 사용하겠습니다.", key='prompt_yes', use_container_width=True):
                handle_protection_choice('yes')
        with prompt_col2:
            if st.button("❌ 아니요, 그냥 진행하겠습니다.", key='prompt_no', use_container_width=True):
                handle_protection_choice('no')
        
        st.markdown("---")
        return 

    # 4. 강화 정보 및 시도
    if current_level < len(ENHANCE_REQUIREMENTS) - 1:
        req = ENHANCE_REQUIREMENTS[current_level]
        
        st.subheader("🔨 다음 강화 정보")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1: st.metric("다음 검", req['name'])
        with info_col2: st.metric("소모 비용 (Gold)", f"{req['gold']:,}")
        with info_col3: st.metric("성공 확률", f"{req['rate'] * 100:.1f}%")
        
        # 재료/아이템 요구사항 표시
        requirements_list = []
        if req['item_req']:
            item_req = parse_item_requirement(req['item_req'])
            if item_req: requirements_list.append(f"**기본 아이템:** {item_req['name']} {item_req['qty']}개")
        
        if req['mat_name'] and req['mat_qty'] > 0 and '파괴방지권 불가' not in req['mat_name']:
            requirements_list.append(f"**필수 재료:** {req['mat_name']} {req['mat_qty']}개")

        if '파괴방지권 불가' in (req['mat_name'] or ''):
            requirements_list.append("🔴 **파괴 방지권 사용 불가**")

        st.markdown("#### 📜 요구사항")
        if requirements_list:
            st.markdown("\n".join([f"* {r}" for r in requirements_list]))
        else:
            st.markdown("* 추가 재료 요구사항 없음 (Level 21 '템페스트 골드'부터 재료가 필요합니다.)")

        
        # 강화 및 판매 버튼
        st.subheader("➡️ 행동 선택")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("🔥 강화 시작!", use_container_width=True, type="primary"):
                enhance_sword_start()
        
        with action_col2:
            sell_price = get_sell_price(current_level)
            if st.button(f"💰 무기 판매 ({sell_price:,} Gold 획득 - 업글 비용의 120%)", use_container_width=True):
                sell_sword()

            
    else:
        st.success("🎉 **최고 레벨**의 검을 완성했습니다!")
        sell_price = get_sell_price(current_level)
        if st.button(f"💰 무기 판매 ({sell_price:,} Gold 획득 - 고정가)", use_container_width=True, type="secondary"):
            sell_sword()
            
    st.markdown("---")
    
    # 5. 상점 및 리셋
    st.subheader("🛒 상점 및 편의 기능")
    
    shop_col, reset_col = st.columns(2)

    with shop_col:
        st.caption("파괴 방지권 상점")
        
        item_name = '파괴 방지권'
        price = STORE_ITEMS[item_name]
        
        if st.button(f"🛡️ {item_name} 구매 ({price:,} Gold)", use_container_width=True):
            buy_item(item_name, price)
        
    with reset_col:
        if st.button("🔄 게임 리셋", use_container_width=True):
            reset_game()

    st.markdown("---")
    
    # 6. 결과 메시지 출력 및 인벤토리
    st.subheader("📢 현재 상태 및 결과")
    st.markdown(f"**{st.session_state.message}**")

    st.subheader("📦 재료/아이템 인벤토리")
    
    inv_col, acquire_col = st.columns([2, 1])

    with inv_col:
        display_data = []
        all_trackable_items = list(set(ALL_MATERIALS_NAMES + ALL_ITEM_NAMES + list(STORE_ITEMS.keys()) + [SWORD_NAMES[0]]))
        for name in sorted(all_trackable_items):
            qty = st.session_state.inventory.get(name, 0)
            if qty > 0:
                display_data.append([name, qty])
        
        if display_data:
            st.dataframe(
                data=display_data, 
                column_config={0: "아이템/재료 이름", 1: "수량"},
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("현재 인벤토리가 비어있습니다. (낡은 단검 제외)")

    with acquire_col:
        st.caption("재료/아이템 획득 (디버그/편의)")
        
        all_acquirable = ALL_MATERIALS_NAMES + ALL_ITEM_NAMES
        selected_mat = st.selectbox("획득할 재료/아이템 선택", all_acquirable)
        
        if st.button(f"➕ {selected_mat} 1개 획득", use_container_width=True):
            acquire_material(selected_mat)

if __name__ == "__main__":
    main()
