# =======================
# full_rpg_game.py
# =======================
import streamlit as st
import random

# =======================
# ==== 캐릭터 / 아이템 ====
# =======================
class Item:
    def __init__(self, name, type_, attack=0, defense=0, magic_attack=0, magic_defense=0, crit_rate=0, crit_damage=1.5):
        self.name = name
        self.type = type_
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage

class Character:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.exp = 0
        self.max_hp = 100
        self.hp = 100
        self.attack = 10
        self.defense = 5
        self.magic_attack = 5
        self.magic_defense = 3
        self.crit_rate = 0.1
        self.crit_damage = 1.5
        self.status_points = 0
        self.inventory = []
        self.weapon = None
        self.armor = None
        self.element = None  # 물, 불, 흙, 전기

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.level * 20:
            self.exp -= self.level * 20
            self.level += 1
            self.status_points += 5
            self.max_hp += 10
            self.hp = self.max_hp
            st.success(f"레벨업! 현재 레벨: {self.level}")

class Monster:
    def __init__(self, name, hp, attack, defense, magic_attack, magic_defense, loot_table=[]):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.loot_table = loot_table

class Dungeon:
    def __init__(self, name, monsters):
        self.name = name
        self.monsters = monsters

class Town:
    def __init__(self, name, level_required):
        self.name = name
        self.level_required = level_required

# =======================
# ==== 아이템 / 몹 / 던전 초기화 ====
# =======================
weapon_list = [
    Item("목검", "무기", attack=5, crit_rate=0.05),
    Item("철검", "무기", attack=10, crit_rate=0.1),
    Item("마법봉", "무기", magic_attack=12, crit_rate=0.1),
    Item("전설의 검", "무기", attack=20, crit_rate=0.15)
]

armor_list = [
    Item("가죽갑옷", "갑옷", defense=5, magic_defense=2),
    Item("철갑옷", "갑옷", defense=10, magic_defense=5),
    Item("마법로브", "갑옷", defense=3, magic_defense=12),
    Item("전설의 갑옷", "갑옷", defense=20, magic_defense=15)
]

materials_list = [
    Item("나무", "재료"),
    Item("철", "재료"),
    Item("마나석", "재료"),
    Item("용의 비늘", "재료"),
    Item("불꽃 결정", "재료"),
    Item("물의 정수", "재료"),
    Item("흙의 결정", "재료"),
    Item("전기 에너지", "재료"),
    Item("드래곤 심장", "재료"),
    Item("마법 수정", "재료")
]

monster_list = [
    Monster("슬라임", 20, 5, 1, 0, 0, [(weapon_list[0], 0.1), (armor_list[0], 0.1)]),
    Monster("고블린", 30, 8, 2, 0, 0, [(weapon_list[1], 0.05), (armor_list[1], 0.05)]),
    Monster("늑대", 40, 12, 3, 0, 0, [(weapon_list[1], 0.05), (armor_list[1], 0.05)]),
    Monster("마법사", 25, 5, 2, 10, 5, [(weapon_list[2], 0.05), (armor_list[2], 0.05)]),
    Monster("오크", 50, 15, 5, 0, 0, [(weapon_list[1], 0.05), (armor_list[1], 0.05)]),
    Monster("거인", 80, 20, 10, 0, 5, [(weapon_list[3], 0.02), (armor_list[3], 0.02)]),
    Monster("마법정령", 60, 8, 5, 15, 10, [(weapon_list[2], 0.05), (armor_list[2], 0.05)]),
    Monster("해골병사", 45, 10, 5, 0, 0, [(weapon_list[1], 0.05)]),
    Monster("유령", 35, 8, 2, 12, 8, [(armor_list[2], 0.05)]),
    Monster("드래곤", 200, 30, 10, 20, 15, [(weapon_list[3], 0.05), (armor_list[3], 0.05)])
]

dungeon_list = [
    Dungeon("초보 던전", monster_list[:3]),
    Dungeon("중급 던전", monster_list[3:7]),
    Dungeon("상급 던전", monster_list[7:10])
]

town_list = [
    Town("시작 마을", 1),
    Town("중간 마을", 3),
    Town("고급 마을", 5)
]

# =======================
# ==== 전투 / 강화 / 인첸트 ====
# =======================
def attack_target(attacker, target):
    crit = random.random() < attacker.crit_rate
    if crit:
        damage = (attacker.attack - target.defense) * attacker.crit_damage
    else:
        damage = attacker.attack - target.defense
    damage = max(1, int(damage))
    target.hp -= damage
    return damage, crit

def magic_attack_target(attacker, target):
    damage = attacker.magic_attack - target.magic_defense
    damage = max(1, int(damage))
    target.hp -= damage
    return damage

def get_drops(monster):
    drops = []
    for item, prob in monster.loot_table:
        if random.random() < prob:
            drops.append(item)
    return drops

def enhance_item(item, success_rate=0.8):
    if random.random() < success_rate:
        if item.type == '무기':
            item.attack = int(item.attack * 1.1)
            item.crit_rate = min(1.0, item.crit_rate * 1.05)
        elif item.type == '갑옷':
            item.defense = int(item.defense * 1.1)
            item.magic_defense = int(item.magic_defense * 1.1)
        st.success(f"{item.name} 강화 성공!")
        return True
    else:
        st.warning(f"{item.name} 강화 실패...")
        return False

def enchant_item(item, attribute, value):
    if attribute == 'attack' and item.type == '무기':
        item.attack += value
    elif attribute == 'defense' and item.type == '갑옷':
        item.defense += value
    elif attribute == 'magic_attack' and item.type == '무기':
        item.magic_attack += value
    elif attribute == 'magic_defense' and item.type == '갑옷':
        item.magic_defense += value
    elif attribute == 'crit_rate' and item.type == '무기':
        item.crit_rate = min(1.0, item.crit_rate + value)
    elif attribute == 'crit_damage' and item.type == '무기':
        item.crit_damage += value
    st.success(f"{item.name}에 {attribute}+{value} 인첸트 완료!")

# =======================
# ==== Streamlit UI ====
# =======================
if 'player' not in st.session_state:
    st.session_state.player = Character("용사")
player = st.session_state.player

st.title("🛡️ Streamlit RPG 게임")

# --- 캐릭터 상태 ---
st.subheader("👤 캐릭터 상태")
st.write(f"이름: {player.name}")
st.write(f"레벨: {player.level}  HP: {player.hp}/{player.max_hp}")
st.write(f"공격:{player.attack} 방어:{player.defense} 마법공격:{player.magic_attack} 마법방어:{player.magic_defense}")
st.write(f"치명타 확률:{player.crit_rate*100:.1f}% 치명타 배율:{player.crit_damage}")
st.write(f"스탯 포인트: {player.status_points}")

# --- 스탯 포인트 분배 ---
if player.status_points > 0:
    st.subheader("📈 스탯 포인트 분배")
    attack_inc = st.number_input("공격력 증가", min_value=0, max_value=player.status_points, step=1)
    defense_inc = st.number_input("방어력 증가", min_value=0, max_value=player.status_points-attack_inc, step=1)
    magic_attack_inc = st.number_input("마법 공격력 증가", min_value=0, max_value=player.status_points-attack_inc-defense_inc, step=1)
    magic_defense_inc = st.number_input("마법 방어력 증가", min_value=0, max_value=player.status_points-attack_inc-defense_inc-magic_attack_inc, step=1)
    crit_rate_inc = st.number_input("치명타 확률 증가 (0~0.5)", min_value=0.0, max_value=0.5, step=0.01)
    if st.button("포인트 적용"):
        player.attack += attack_inc
        player.defense += defense_inc
        player.magic_attack += magic_attack_inc
        player.magic_defense += magic_defense_inc
        player.crit_rate = min(1.0, player.crit_rate + crit_rate_inc)
        player.status_points -= (attack_inc + defense_inc + magic_attack_inc + magic_defense_inc)
        st.success("스탯 포인트 적용 완료!")

# --- 마법 선택 ---
if player.level >= 5 and not player.element:
    st.subheader("🪄 마법 선택")
    element_choice = st.selectbox("원소 선택", ["물","불","흙","전기"])
    if st.button("선택 확정"):
        player.element = element_choice
        st.success(f"{element_choice} 원소 선택 완료! 변경 불가")

# --- 코드 입력 보상 ---
st.subheader("🎁 코드 입력 보상")
reward_code = st.text_input("코드 입력")
if st.button("보상 받기"):
    code_dict = {
        "GOLD100": (materials_list[0], 10),
        "SWORDUP": (weapon_list[0], 1),
        "ARMORUP": (armor_list[0], 1)
    }
    if reward_code in code_dict:
        item, qty = code_dict[reward_code]
        for _ in range(qty):
            player.inventory.append(item)
        st.success(f"{item.name} x{qty} 획득!")
    else:
        st.warning("유효하지 않은 코드입니다.")

# --- 장비 강화/인첸트 ---
st.subheader("🛠️ 장비 강화 / 인첸트")
if player.weapon:
    st.write(f"무기: {player.weapon.name} 공격:{player.weapon.attack}")
    if st.button("강화 무기"):
        enhance_item(player.weapon)
    attr = st.selectbox("인첸트 속성", ["attack","crit_rate","crit_damage","magic_attack"])
    val = st.number_input("인첸트 값", value=1)
    if st.button("인첸트 무기"):
        enchant_item(player.weapon, attr, val)
if player.armor:
    st.write(f"갑옷: {player.armor.name} 방어:{player.armor.defense}")
    if st.button("강화 갑옷"):
        enhance_item(player.armor)
    attr2 = st.selectbox("인첸트 속성 (갑옷)", ["defense","magic_defense"])
    val2 = st.number_input("인첸트 값 (갑옷)", value=1)
    if st.button("인첸트 갑옷"):
        enchant_item(player.armor, attr2, val2)

# --- 던전 전투 ---
st.subheader("⚔️ 던전 전투")
dungeon_choice = st.selectbox("던전 선택", [d.name for d in dungeon_list])
if st.button("던전 입장"):
    dungeon = next(d for d in dungeon_list if d.name==dungeon_choice)
    monster = random.choice(dungeon.monsters)
    st.write(f"{monster.name} 등장!")
    dmg, crit = attack_target(player, monster)
    st.write(f"플레이어 공격! {dmg} 피해 {'치명타!' if crit else ''}")
    if monster.hp <= 0:
        st.write(f"{monster.name} 처치 성공!")
        drops = get_drops(monster)
        player.inventory.extend(drops)
        st.write("획득 아이템:", [i.name for i in drops])
