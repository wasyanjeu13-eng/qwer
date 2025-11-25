import streamlit as st
import random
import re

# --- 1. 상수 및 데이터 정의 ---

INITIAL_MONEY = 300000  # 시작 소지금
INITIAL_LEVEL = 0
SECRET_DEBUG_CODE = "DEVMODE" 
DEBUG_GOLD_AMOUNT = 1000000000 
DEBUG_MAT_QTY = 100

# 상점 아이템 및 가격
STORE_ITEMS = {
    '파괴 방지권': 10000000 
}

# 강화 데이터 (이미지 기반)
# 🚨 주의: 이 데이터는 원본이며, 실제 적용 확률은 st.session_state.custom_rates를 따름.
ENHANCE_DATA = {
    0: {'name': '쓸만한 단검', 'rate': 1.00, 'gold': 500, 'sell': 500, 'prot_qty': 0, 'req_note': None},
    1: {'name': '견고한 단검', 'rate': 0.98, 'gold': 500, 'sell': 200, 'prot_qty': 0, 'req_note': None},
    2: {'name': '바이킹 소드', 'rate': 0.95, 'gold': 1000, 'sell': 500, 'prot_qty': 0, 'req_note': None},
    3: {'name': '불타는 검', 'rate': 0.93, 'gold': 2000, 'sell': 1000, 'prot_qty': 0, 'req_note': None},
    4: {'name': '냉기의 소드', 'rate': 0.90, 'gold': 4000, 'sell': 2000, 'prot_qty': 1, 'req_note': None},
    5: {'name': '양날 검', 'rate': 0.86, 'gold': 7000, 'sell': 6000, 'prot_qty': 1, 'req_note': None},
    6: {'name': '심판자의 대검', 'rate': 0.81, 'gold': 10000, 'sell': 15000, 'prot_qty': 1, 'req_note': '국적불분명 철조각'}, 
    7: {'name': '마력의 검', 'rate': 0.75, 'gold': 15000, 'sell': 25000, 'prot_qty': 1, 'req_note': '국적불분명 철조각'}, 
    8: {'name': '타우 스워드', 'rate': 0.70, 'gold': 22000, 'sell': 50000, 'prot_qty': 1, 'req_note': '국적불분명 철조각'}, 
    9: {'name': '형광검', 'rate': 0.66, 'gold': 30000, 'sell': 90000, 'prot_qty': 1, 'req_note': '타우의 뼈 부스러기'}, 
    10: {'name': '피묻은 검', 'rate': 0.62, 'gold': 30000, 'sell': 180000, 'prot_qty': 1, 'req_note': '빛 바랜 형광물질'}, 
    11: {'name': '화염의 쌍검', 'rate': 0.61, 'gold': 51000, 'sell': 500000, 'prot_qty': 1, 'req_note': '스위스산 철조각'}, 
    12: {'name': '불꽃 마검', 'rate': 0.54, 'gold': 70000, 'sell': 1000000, 'prot_qty': 1, 'req_note': '스위스산 철조각'}, 
    13: {'name': '마검 아포피스', 'rate': 0.50, 'gold': 80000, 'sell': 2000000, 'prot_qty': 2, 'req_note': '불꽃마검 손잡이'}, 
    14: {'name': '데몬 배틀 엑스', 'rate': 0.49, 'gold': 100000, 'sell': 5000000, 'prot_qty': 3, 'req_note': '사악한 영혼'}, 
    15: {'name': '투명 검', 'rate': 0.46, 'gold': 130000, 'sell': 10000000, 'prot_qty': 4, 'req_note': '도끼 가루'}, 
    16: {'name': '날렵한 용검', 'rate': 0.44, 'gold': 170000, 'sell': 20000000, 'prot_qty': 7, 'req_note': '투명 물질'}, 
    17: {'name': '샤이니 소드', 'rate': 0.40, 'gold': 220000, 'sell': 44500000, 'prot_qty': 9, 'req_note': None}, 
    18: {'name': '왕푸야샤[보관필요]', 'rate': 0.38, 'gold': 300000, 'sell': 72000000, 'prot_qty': 10, 'req_note': None}, 
    19: {'name': '다색검', 'rate': 0.35, 'gold': 400000, 'sell': 120000000, 'prot_qty': 12, 'req_note': None}, 
    20: {'name': '템페스트 골드[보관필요]', 'rate': 0.33, 'gold': 650000, 'sell': 240000000, 'prot_qty': 15, 'req_note': None}, 
    21: {'name': '샤프 워커[보관필요]', 'rate': 0.30, 'gold': 300000000, 'sell': 300000000, 'prot_qty': 17, 'req_note': '왕푸야샤 1자루'}, 
    22: {'name': '피에로의 쌍검', 'rate': 0.27, 'gold': 400000000, 'sell': 400000000, 'prot_qty': 20, 'req_note': '템페스트 골드 2자루'}, 
    23: {'name': '도룡도', 'rate': 0.27, 'gold': 550000000, 'sell': 550000000, 'prot_qty': 22, 'req_note': '사악한 영혼 12개'}, 
    24: {'name': '안 강해보이는 검[하드버그]', 'rate': 0.25, 'gold': 750000000, 'sell': 750000000, 'prot_qty': 23, 'req_note': '샤프 워커 1자루'}, 
    25: {'name': '메두사', 'rate': 0.35, 'gold': 400000000, 'sell': 400000000, 'prot_qty': 23, 'req_note': '도끼 가루 15개'}, 
    26: {'name': '오딧세이 소드', 'rate': 0.50, 'gold': 1800000000, 'sell': 5000000, 'prot_qty': '방지권불가', 'req_note': None}, 
    27: {'name': '모자이칼', 'rate': 0.40, 'gold': 2500000000, 'sell': 2500000000, 'prot_qty': '방지권불가', 'req_note': '투명 물질 2개'}, 
    28: {'name': '화염에 달군 검', 'rate': 0.15, 'gold': 0, 'sell': '100000000000000000', 'prot_qty': '방지권불가', 'req_note': None}, 
    29: {'name': '화염에 달군 검', 'rate': 1.00, 'gold': 0, 'sell': 10000000000, 'prot_qty': 0, 'req_note': '최고 레벨 달성'},
}

# 모든 재료 및 아이템 목록 정의
ALL_MATERIALS_NAMES = ['국적불분명 철조각', '타우의 뼈 부스러기', '빛 바랜 형광물질', '스위스산 철조각', 
                       '불꽃마검 손잡이', '사악한 영혼', '도끼 가루', '투명 물질']
ALL_ITEM_NAMES = ['왕푸야샤', '템페스트 골드', '샤프 워커']
SWORD_NAMES = {i: ENHANCE_DATA[i]['name'] for i in range(1, len(ENHANCE_DATA))}
SWORD_NAMES[0] = '낡은 단검'


# --- 2. Streamlit Session State 및 헬퍼 함수 ---

def initialize_session_state():
    """앱 시작 시 또는 리셋 시 세션 상태를 초기화합니다."""
    if 'money' not in st.session_state: st.session_state.money = INITIAL_MONEY
    if 'level' not in st.session_state: st.session_state.level = INITIAL_LEVEL
    if 'message' not in st.session_state: st.session_state.message = "강화를 시작해보세요! ⚔️ 무기를 팔아 골드를 얻을 수 있습니다."
    if 'is_debug_mode' not in st.session_state: st.session_state.is_debug_mode = False
    if 'inventory' not in st.session_state:
        all_inventory_items = ALL_MATERIALS_NAMES + ALL_ITEM_NAMES + list(STORE_ITEMS.keys())
        st.session_state.inventory = {name: 0 for name in all_inventory_items}
        st.session_state.inventory['낡은 단검'] = 1 
    if 'use_protection_prompt' not in st.session_state: st.session_state.use_protection_prompt = False
    if 'failed_level' not in st.session_state: st.session_state.failed_level = 0 
    
    # 🚨 추가: 커스텀 확률 세션 상태 초기화
    if 'custom_rates' not in st.session_state:
        # ENHANCE_DATA의 원본 확률로 초기화
        st.session_state.custom_rates = {k: v['rate'] for k, v in ENHANCE_DATA.items()}


def get_current_sword_name():
    """현재 레벨에 해당하는 검의 이름을 반환합니다."""
    current_level = st.session_state.level
    
    if current_level == 0:
        return SWORD_NAMES[0]
        
    # ENHANCE_DATA는 0부터 시작하지만, get_current_sword_name은 현재 레벨에 해당하는 (성공한) 검의 정보를 가져옴.
    # ENHANCE_DATA[N]은 N -> N+1 강화의 정보를 담고, 성공 시 N+1 레벨의 검이 됨.
    # 따라서 현재 레벨이 L이면, ENHANCE_DATA[L-1]의 이름을 가져와야 함.
    if current_level > 0 and current_level < len(ENHANCE_DATA):
        return ENHANCE_DATA.get(current_level - 1, {}).get('name', f"미지의 검 (+{current_level})")
    
    # 예외 처리: 혹시라도 레벨이 데이터 범위를 벗어났을 경우 (최대 레벨 이후)
    if current_level == len(ENHANCE_DATA):
        return ENHANCE_DATA.get(len(ENHANCE_DATA) - 1, {}).get('name', f"최고 검 (+{current_level})")
        
    return f"알 수 없는 검 (+{current_level})"


def get_sell_price(current_level):
    """현재 검의 판매 가격을 (하드코딩된) ENHANCE_DATA에서 가져옵니다."""
    if current_level >= len(ENHANCE_DATA):
        current_level = len(ENHANCE_DATA) - 1
        
    # 현재 레벨이 L이면, ENHANCE_DATA[L]이 아니라 ENHANCE_DATA[L-1]을 봐야 함 (0레벨은 ENHANCE_DATA[0])
    target_level = max(0, current_level - 1)
        
    price_data = ENHANCE_DATA.get(target_level, {}).get('sell')
    
    if price_data == '판매 불가':
        return 0
        
    return int(price_data) if isinstance(price_data, (int, str)) and str(price_data).isdigit() else 0

def sell_sword():
    """현재 검을 판매하고 골드를 획득합니다."""
    current_level = st.session_state.level
    current_name = get_current_sword_name()
    
    # +28 모자이칼은 판매 불가 (현재 레벨이 29이므로 28 강화 정보의 이름)
    if current_level == 29:
         # Level 28 -> 29로 강화 성공 시 이름은 '화염에 달군 검'
         # Level 27 -> 28로 강화 성공 시 이름은 '화염에 달군 검' (ENHANCE_DATA[27].name)
         # 하지만 이미지상 +28 검 이름이 '화염에 달군 검' (ENHANCE_DATA[27].name)
         # Level 28의 판매불가는 ENHANCE_DATA[27]을 봐야 함
        if ENHANCE_DATA[27].get('sell') == '판매 불가':
            st.session_state.message = f"🚨 **[판매 실패]** **+{current_level} {current_name}**은(는) 판매할 수 없습니다."
            return

    # 낡은 단검이 마지막 하나 남았는지 확인
    if current_level == 0 and st.session_state.inventory.get(SWORD_NAMES[0], 0) == 1:
        st.session_state.message = "🚨 **[판매 실패]** 낡은 단검은 마지막 하나 남았기 때문에 팔 수 없습니다."
        return
    
    sell_price = get_sell_price(current_level)
    
    # 인벤토리에서 현재 검 소모 및 레벨 하락 처리
    current_name_clean = current_name.replace('[보관필요]', '').replace('[하드버그]', '').strip()
    item_to_consume = current_name_clean if current_name_clean in st.session_state.inventory else current_name
    
    if st.session_state.inventory.get(item_to_consume, 0) > 0:
        st.session_state.inventory[item_to_consume] -= 1
        st.session_state.money += sell_price
        
        # 판매 후 레벨 1 하락 (이전 무기로 돌아감)
        st.session_state.level -= 1 
        if st.session_state.level < 0:
            st.session_state.level = 0
            st.session_state.inventory[SWORD_NAMES[0]] = st.session_state.inventory.get(SWORD_NAMES[0], 0) + 1 # 낡은 단검 획득
        
        st.session_state.message = f"✅ **[판매 성공]** **+{current_level} {current_name}**을(를) **{sell_price:,} Gold**에 판매했습니다."
    else:
        st.session_state.message = "🚨 **[판매 실패]** 인벤토리에 현재 검이 없습니다. (새로 강화하거나 낡은 단검을 다시 획득해야 합니다.)"
        
def parse_item_requirement(req_str):
    """요구사항 문자열에서 이름과 수량을 파싱합니다."""
    if not req_str: return None
    # 1. '아이템 N자루' 또는 '재료 N개' 형식 파싱
    match = re.search(r'(.+)\s(\d+)자루|(.+)\s(\d+)개', req_str)
    if match:
        name = match.group(1) or match.group(3)
        qty = match.group(2) or match.group(4)
        if name and qty:
            return {'name': name.strip(), 'qty': int(qty)}
            
    # 2. '재료 이름' (단일 요구사항) - Level 6~20의 드랍템 정보를 위한 예외처리
    if req_str.strip() in ALL_MATERIALS_NAMES:
        return {'name': req_str.strip(), 'qty': 1}
        
    return None

def check_materials(req, current_level):
    """강화에 필요한 재료 및 아이템이 충분한지 확인합니다. (파괴 방지권 제외)"""
    
    # 1. 재료/아이템 요구사항 확인 (Level 21 이상만 강화 재료로 간주)
    if current_level >= 20: 
        req_note = req.get('req_note')
        if req_note:
            item_req = parse_item_requirement(req_note)
            if item_req:
                current_qty = st.session_state.inventory.get(item_req['name'], 0)
                if current_qty < item_req['qty']:
                    return False, f"🚨 **[강화 실패]** 요구 아이템/재료 **{item_req['name']}** ({item_req['qty']}개)가 부족합니다. (현재: {current_qty}개)"

    return True, None

def consume_materials(req, current_level):
    """강화 재료와 아이템을 소모합니다. (파괴 방지권 제외)"""
    
    # 1. 재료/아이템 소모 (Level 21 이상만 해당)
    if current_level >= 20: 
        req_note = req.get('req_note')
        if req_note:
            item_req = parse_item_requirement(req_note)
            if item_req:
                st.session_state.inventory[item_req['name']] = max(0, st.session_state.inventory.get(item_req['name'], 0) - item_req['qty'])
    
    # 2. 파괴 방지권은 강화 실패 후 선택 시에만 소모되므로, 여기서는 소모하지 않음


def enhance_sword_core(use_protection=False):
    """강화 실패 후 방지권 사용 여부에 따른 최종 로직을 처리합니다."""
    current_level = st.session_state.failed_level
    
    # 실패 로직 기본 메시지
    fail_message = f"💥 **[강화 실패]** 무기가 파괴될 위험이 있습니다."
    
    # 파괴 방지권 사용 선택 시
    if use_protection:
        prot_qty = ENHANCE_DATA.get(current_level, {}).get('prot_qty', 0)
        
        # 방지권 차감 및 레벨 유지
        if isinstance(prot_qty, int) and prot_qty > 0:
            # 방지권 차감
            st.session_state.inventory['파괴 방지권'] = max(0, st.session_state.inventory.get('파괴 방지권', 0) - prot_qty)
            st.session_state.level = current_level 
            
            # 여기서 get_current_sword_name()을 호출하기 전에 st.session_state.level이 제대로 설정되어 있어야 함
            # -> 이미 바로 위에서 설정했으므로 안전함
            st.session_state.message = f"{fail_message} 🛡️ **파괴 방지권** {prot_qty}개가 소모되어 **레벨이 유지**되었습니다. 현재 레벨: +{current_level} ({get_current_sword_name()})"
            return
        # 방지권 불가 레벨에서 사용 버튼을 누른 경우 (예외 상황)
        else:
            st.session_state.message = f"{fail_message} 🚨 이 레벨에서는 파괴 방지권을 사용할 수 없으므로, 무기 파괴/하락이 진행됩니다."
            use_protection = False # 강제로 미사용 처리하여 아래 로직 실행

    # 방지권 미사용 또는 불가능 레벨: 파괴/하락
    if current_level >= 6: 
        # 레벨 6 이상: 파괴 (Level 0으로 하락)
        
        # 이전 검 이름 가져오기 (인벤토리에서 소모하기 위함)
        st.session_state.level = current_level # 임시로 실패 이전 레벨로 설정하여 이름 가져옴
        prev_name = get_current_sword_name()
        prev_name_clean = prev_name.replace('[보관필요]', '').replace('[하드버그]', '').strip()
        
        # 파괴된 무기 인벤토리에서 제거
        if prev_name_clean in st.session_state.inventory and st.session_state.inventory.get(prev_name_clean, 0) > 0:
             st.session_state.inventory[prev_name_clean] = max(0, st.session_state.inventory[prev_name_clean] - 1)
        
        # 레벨 초기화 및 낡은 단검 획득
        st.session_state.level = INITIAL_LEVEL
        st.session_state.inventory[SWORD_NAMES[INITIAL_LEVEL]] = st.session_state.inventory.get(SWORD_NAMES[INITIAL_LEVEL], 0) + 1 
        
        # 레벨 설정 후 메시지 업데이트
        st.session_state.message = f"{fail_message} 💣 **무기가 터져서** **{SWORD_NAMES[INITIAL_LEVEL]}**({st.session_state.level})로 돌아갔습니다!"
        
    elif current_level >= 2:
        # 레벨 2~5: 레벨 1 하락
        new_level = current_level - 1
        st.session_state.level = new_level
        
        # 레벨 설정 후 메시지 업데이트
        # get_current_sword_name은 새 레벨을 보고 이름을 가져옴
        st.session_state.message = f"{fail_message} ⬇️ 레벨이 1 하락하여 현재 레벨: **+{new_level}** ({get_current_sword_name()})"
    else:
        # 레벨 0~1: 레벨 유지
        st.session_state.level = current_level
        # 레벨 설정 후 메시지 업데이트
        st.session_state.message = f"{fail_message} 🛡️ 다행히 레벨이 유지되었습니다. 현재 레벨: **+{current_level}** ({get_current_sword_name()})"
        

def enhance_success(new_level, req):
    """강화 성공 시 상태를 업데이트합니다."""
    
    current_level = st.session_state.level
    st.session_state.level = new_level
    
    # 이전 검 소모 및 새 검 획득 로직
    # 주의: get_current_sword_name()은 새로운 레벨(new_level)의 검 이름을 반환하므로,
    # 이전 검 이름을 가져오려면 ENHANCE_DATA[current_level-1]을 직접 참조해야 함
    
    # 인벤토리에서 소모할 이전 검 이름 가져오기 (current_level 상태일 때의 검 이름)
    # Level 0은 '낡은 단검'
    if current_level == 0:
        prev_name = SWORD_NAMES[0]
    else:
        # ENHANCE_DATA[current_level-1]의 이름을 사용해야 함
        prev_name_data = ENHANCE_DATA.get(current_level - 1, {})
        prev_name = prev_name_data.get('name', f"미지의 검 (+{current_level})")
        
    prev_name_clean = prev_name.replace('[보관필요]', '').replace('[하드버그]', '').strip()
    
    # 현재 검 인벤토리에서 소모
    if prev_name_clean in st.session_state.inventory:
        st.session_state.inventory[prev_name_clean] = max(0, st.session_state.inventory.get(prev_name_clean, 0) - 1)
        
    # 새 검 인벤토리에 추가 (req['name']은 강화 성공 후 이름임)
    current_sword_name = req['name'].replace('[보관필요]', '').replace('[하드버그]', '').strip()
    st.session_state.inventory[current_sword_name] = st.session_state.inventory.get(current_sword_name, 0) + 1
    
    # 🚨 수정: 성공 확률을 ENHANCE_DATA가 아닌 세션 상태의 custom_rates에서 가져옴
    success_rate = st.session_state.custom_rates.get(current_level, req['rate'])
    
    st.session_state.message = f"🎉 **[강화 성공!]** 검의 레벨이 **+{new_level}** ({req['name']})이(가) 되었습니다. (확률: {success_rate * 100:.1f}%)"

def enhance_sword_start():
    """강화 전 검사 및 소모를 담당하고, 성공 또는 실패 시 로직을 분기합니다."""
    current_level = st.session_state.level
    
    if current_level >= len(ENHANCE_DATA) - 1:
        st.session_state.message = "🎉 **[강화 달성]** 이미 최고 레벨의 검입니다!"
        return

    req = ENHANCE_DATA.get(current_level)
    cost_gold = req['gold']
    
    # 🚨 추가: 적용할 확률을 세션 상태에서 가져옴 (디버그 모드에서 조정된 값)
    applied_rate = st.session_state.custom_rates.get(current_level, req['rate'])
    
    # 1. 비용 및 재료 확인 (파괴 방지권 제외)
    if st.session_state.money < cost_gold:
        st.session_state.message = f"🚨 **[강화 실패]** 골드({cost_gold:,} Gold)가 부족합니다!"
        return
    
    can_enhance, error_message = check_materials(req, current_level)
    if not can_enhance:
        st.session_state.message = error_message
        return

    # 2. 비용 및 재료 차감 (강화 재료와 골드만 차감)
    st.session_state.money -= cost_gold
    consume_materials(req, current_level)

    # 3. 강화 시도 (성공/실패 판정)
    if random.random() < applied_rate:
        # 성공
        enhance_success(current_level + 1, req)
    else:
        # 실패
        st.session_state.failed_level = current_level
        
        # Level 6 이상 파괴 위험 구간이고, 방지권 사용이 가능하며, 방지권 소지량이 충분할 때 프롬프트 표시
        prot_qty = req['prot_qty']
        can_use_prot = isinstance(prot_qty, int) and prot_qty > 0
        
        if current_level >= 6 and can_use_prot and st.session_state.inventory.get('파괴 방지권', 0) >= prot_qty:
            st.session_state.use_protection_prompt = True
            st.session_state.message = f"💥 **[강화 실패]** 무기가 파괴될 위험이 있습니다! 방지권 {prot_qty}개를 사용하시겠습니까?"
        else:
            # 방지권 조건 미충족 시 즉시 파괴/하락 로직 실행
            enhance_sword_core(use_protection=False)
            
def handle_protection_choice(choice):
    """방지권 사용 여부 선택을 처리합니다."""
    
    # 여기서 st.session_state.failed_level을 사용
    if choice == 'yes':
        enhance_sword_core(use_protection=True)
    else:
        enhance_sword_core(use_protection=False)
    
    st.session_state.use_protection_prompt = False
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
    
# 🚨 추가: 확률을 ENHANCE_DATA의 원본 값으로 리셋하는 함수
def reset_rates():
    st.session_state.custom_rates = {k: v['rate'] for k, v in ENHANCE_DATA.items()}
    st.session_state.message = "✅ **[디버그]** 모든 강화 확률이 원본 값으로 리셋되었습니다."
    st.experimental_rerun()


# --- 3. Streamlit UI 구성 ---

def main():
    initialize_session_state()

    st.set_page_config(page_title="검 강화하기 시뮬레이터", layout="wide")
    st.title("🔥 검 강화하기 시뮬레이터 (이미지 데이터 기반 최종본)")
    st.markdown("---")
    
    current_level = st.session_state.level
    
    # 1. 제작자 전용 코드 입력 및 디버그 모드 토글
    with st.expander("🛠️ 제작자 전용 메뉴 (DEBUG)", expanded=st.session_state.is_debug_mode):
        input_code = st.text_input("디버그 활성화 코드 입력", type="password", key='debug_code_input')
        
        if input_code == SECRET_DEBUG_CODE:
            st.session_state.is_debug_mode = True
            st.success("✅ 디버그 모드가 활성화되었습니다!")
        # 🚨 수정: 디버그 모드가 활성화된 상태에서 코드가 지워지거나 바뀌면 비활성화 (기존 로직 유지)
        elif st.session_state.is_debug_mode and input_code != SECRET_DEBUG_CODE:
             st.session_state.is_debug_mode = False
             st.warning("디버그 모드가 비활성화되었습니다.")

        if st.session_state.is_debug_mode:
            # --- 디버그 액션 ---
            debug_col1, debug_col2 = st.columns(2)
            with debug_col1:
                if st.button(f"⚡ 골드 무한 획득 (+{DEBUG_GOLD_AMOUNT:,} Gold)", use_container_width=True):
                    debug_gain_gold()
            with debug_col2:
                if st.button(f"💎 모든 재료 {DEBUG_MAT_QTY}개 획득", use_container_width=True):
                    debug_gain_all_items()
                    
            st.markdown("---")
            st.subheader("📊 강화 확률 조정 (0.0 ~ 1.0)")
            
            # --- 확률 조정 UI ---
            
            # 29레벨(최고 레벨 달성) 강화는 확률 조정에서 제외 (항상 1.00)
            levels_to_adjust = list(ENHANCE_DATA.keys())[:-1] 
            
            # 2개씩 컬럼 분할
            cols = st.columns(2)
            
            for i, level in enumerate(levels_to_adjust):
                req_data = ENHANCE_DATA[level]
                
                # 슬라이더 키: 레벨과 연결
                key = f"rate_slider_{level}"
                
                # 현재 조정된 값 또는 초기 원본 값
                current_rate = st.session_state.custom_rates.get(level, req_data['rate'])
                
                # 레벨 정보 캡션
                label = f"+{level} → +{level+1} ({req_data['name']})"

                with cols[i % 2]:
                    # 슬라이더 값 변경 시 세션 상태 업데이트
                    new_rate = st.slider(
                        label, 
                        min_value=0.0, 
                        max_value=1.0, 
                        value=current_rate, 
                        step=0.001,
                        key=key,
                        format="%.3f"
                    )
                    
                    # 슬라이더가 이동되면 세션 상태에 저장
                    if new_rate != current_rate:
                         st.session_state.custom_rates[level] = new_rate
                    
            if st.button("🔄 확률 원본 값으로 리셋", key='reset_rates_btn'):
                reset_rates()


    # 2. 상단 정보 표시 영역
    st.markdown("---")
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
        prot_qty = ENHANCE_DATA.get(st.session_state.failed_level, {}).get('prot_qty', 0)
        st.warning(f"🛡️ **파괴 방지권** {prot_qty}개를 사용하시겠습니까? (보유: {st.session_state.inventory.get('파괴 방지권', 0)}개)")
        
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
    if current_level < len(ENHANCE_DATA) - 1:
        req = ENHANCE_DATA[current_level]
        
        st.subheader("🔨 다음 강화 정보")
        
        # 🚨 수정: 적용 확률을 세션 상태에서 가져옴
        applied_rate = st.session_state.custom_rates.get(current_level, req['rate'])
        
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1: st.metric("다음 검", req['name'])
        with info_col2: st.metric("소모 비용 (Gold)", f"{req['gold']:,}")
        with info_col3: st.metric("성공 확률", f"{applied_rate * 100:.1f} %") # 수정된 확률 반영
        
        # 재료/아이템 요구사항 표시
        requirements_list = []
        
        # 아이템/재료 요구사항 (Level 21 이상만 강화 재료로 간주)
        if current_level >= 20:
             req_note = req.get('req_note')
             if req_note:
                requirements_list.append(f"**필수 강화 재료/아이템:** {req_note}")
        
        # 파괴 방지권 정보
        prot_qty = req.get('prot_qty')
        if isinstance(prot_qty, int) and prot_qty > 0:
            requirements_list.append(f"🛡️ **실패 시 방지권 소모량:** {prot_qty}개")
        elif prot_qty == '방지권불가':
            requirements_list.append("🔴 **파괴 방지권 사용 불가 레벨**")

        st.markdown("#### 📜 요구사항")
        if requirements_list:
            st.markdown("\n".join([f"* {r}" for r in requirements_list]))
        else:
            st.markdown("* 추가 재료 요구사항 없음")

        
        # 강화 및 판매 버튼
        st.subheader("➡️ 행동 선택")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("🔥 강화 시작!", use_container_width=True, type="primary"):
                enhance_sword_start()
        
        with action_col2:
            sell_price_text = ENHANCE_DATA[current_level]['sell']
            if sell_price_text == '판매 불가':
                 if st.button("🚫 무기 판매 (판매 불가)", use_container_width=True, disabled=True):
                    pass
            else:
                 if st.button(f"💰 무기 판매 ({get_sell_price(current_level):,} Gold 획득)", use_container_width=True):
                    sell_sword()

            
    else:
        st.success("🎉 **최고 레벨**의 검을 완성했습니다!")
        sell_price = get_sell_price(current_level)
        if st.button(f"💰 무기 판매 ({sell_price:,} Gold 획득)", use_container_width=True, type="secondary"):
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
        all_trackable_items = list(set(ALL_MATERIALS_NAMES + ALL_ITEM_NAMES + list(STORE_ITEMS.keys()) + ['낡은 단검']))
        
        # 인벤토리에 현재 검이 1개 포함되어 있다고 가정하고 수량을 계산
        current_name_clean = get_current_sword_name().replace('[보관필요]', '').replace('[하드버그]', '').strip()
        
        for name in sorted(all_trackable_items):
            qty = st.session_state.inventory.get(name, 0)
            
            # 현재 장착 중인 검이 인벤토리 이름과 일치하고, Level 0이 아닐 경우 수량 +1 (장착 중인 것을 포함)
            # 낡은 단검 (Level 0)은 인벤토리에 소지한 수량만 표시
            if name == current_name_clean and st.session_state.level > 0:
                 qty += 1 
            
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
