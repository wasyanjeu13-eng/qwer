# =======================
# app_part1.py
# =======================
import random

# =======================
# 아이템 클래스
# =======================
class Item:
    def __init__(self, name, item_type, attack=0, defense=0, magic_attack=0, magic_defense=0, crit_rate=0.0, crit_damage=1.5):
        self.name = name
        self.type = item_type  # '무기', '갑옷', '재료'
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage

# =======================
# 캐릭터 클래스
# =======================
class Character:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.exp = 0
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        self.attack = 10
        self.defense = 5
        self.magic_attack = 5
        self.magic_defense = 3
        self.crit_rate = 0.1
        self.crit_damage = 2.0
        self.status_points = 5
        self.inventory = []
        self.weapon = None
        self.armor = None
        self.element = None  # '물', '불', '흙', '전기'

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= 50 + self.level * 20:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.status_points += 5
        self.max_hp += 10
        self.max_mp += 5
        self.hp = self.max_hp
        self.mp = self.max_mp

# =======================
# 몬스터 클래스
# =======================
class Monster:
    def __init__(self, name, hp, attack, defense, magic_attack, magic_defense, loot_table):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.loot_table = loot_table  # [(Item, 확률), ...]

# =======================
# 던전 클래스
# =======================
class Dungeon:
    def __init__(self, name, min_level, monsters):
        self.name = name
        self.min_level = min_level
        self.monsters = monsters

# =======================
# 마을 클래스
# =======================
class Town:
    def __init__(self, name, min_level):
        self.name = name
        self.min_level = min_level

# =======================
# 재료 정의
# =======================
materials_list = [
    Item("나무 조각", "재료"),
    Item("철 조각", "재료"),
    Item("은 조각", "재료"),
    Item("마력석", "재료"),
    Item("용의 비늘", "재료"),
    Item("늑대 가죽", "재료"),
    Item("고블린 송곳니", "재료"),
    Item("드래곤 뼈", "재료"),
    Item("불의 정수", "재료"),
    Item("물의 정수", "재료"),
    Item("흙의 정수", "재료"),
    Item("전기의 정수", "재료"),
    Item("마나 수정", "재료"),
    Item("정령의 깃털", "재료"),
    Item("어둠의 결정", "재료"),
    Item("빛의 결정", "재료"),
    Item("스켈레톤 뼈", "재료"),
    Item("용암 조각", "재료"),
    Item("서리 결정", "재료"),
    Item("폭풍 결정", "재료"),
]

# =======================
# 무기 & 갑옷 정의
# =======================
weapon_list = [
    Item("철검", "무기", attack=15, crit_rate=0.1, crit_damage=2.0),
    Item("은검", "무기", attack=25, crit_rate=0.15, crit_damage=2.2),
    Item("마법 지팡이", "무기", magic_attack=20),
    Item("용의 검", "무기", attack=40, crit_rate=0.2, crit_damage=2.5),
    Item("폭풍의 도끼", "무기", attack=35, crit_rate=0.18, crit_damage=2.3),
]

armor_list = [
    Item("가죽 갑옷", "갑옷", defense=5, magic_defense=3),
    Item("철 갑옷", "갑옷", defense=15, magic_defense=5),
    Item("은 갑옷", "갑옷", defense=20, magic_defense=8),
    Item("용의 갑옷", "갑옷", defense=30, magic_defense=15),
    Item("마법사의 로브", "갑옷", defense=10, magic_defense=20),
]

# =======================
# 몬스터 정의 (드롭 확률 낮게)
# =======================
monster_list = [
    Monster("고블린", 50, 10, 3, 0, 0, [(weapon_list[0], 0.1), (materials_list[6], 0.3)]),
    Monster("늑대", 60, 12, 4, 0, 0, [(armor_list[0], 0.05), (materials_list[5], 0.25)]),
    Monster("스켈레톤", 70, 15, 5, 0, 0, [(weapon_list[1], 0.08), (materials_list[16], 0.2)]),
    Monster("마법사", 50, 5, 3, 15, 10, [(weapon_list[2], 0.1), (materials_list[13], 0.2)]),
    Monster("드래곤", 200, 30, 15, 20, 15, [(weapon_list[3], 0.05), (armor_list[3], 0.05), (materials_list[7], 0.2)]),
    Monster("늑대 대장", 120, 20, 10, 0, 0, [(weapon_list[4], 0.05), (materials_list[5], 0.3)]),
    Monster("고블린 마법사", 80, 8, 3, 20, 10, [(weapon_list[2], 0.08), (materials_list[6], 0.2)]),
    Monster("슬라임", 30, 5, 2, 0, 0, [(materials_list[0], 0.4)]),
    Monster("오우거", 150, 25, 12, 0, 0, [(weapon_list[4], 0.05), (armor_list[1], 0.05)]),
    Monster("리치", 180, 15, 8, 25, 15, [(weapon_list[2], 0.1), (armor_list[4], 0.05), (materials_list[14], 0.2)]),
    # 최소 20종을 만들려면 아래 유사 몹 추가
    Monster("악마", 160, 28, 10, 18, 12, [(weapon_list[3], 0.05), (armor_list[3], 0.05), (materials_list[15], 0.2)]),
    Monster("거대 거미", 100, 18, 5, 0, 0, [(materials_list[5], 0.25), (materials_list[16], 0.2)]),
    Monster("서리 정령", 90, 12, 4, 20, 10, [(materials_list[18], 0.3), (weapon_list[2], 0.08)]),
    Monster("불 정령", 110, 15, 6, 22, 12, [(materials_list[9], 0.2), (weapon_list[4], 0.05)]),
    Monster("폭풍 정령", 120, 20, 8, 25, 15, [(materials_list[19], 0.2), (weapon_list[4], 0.05)]),
    Monster("용암 골렘", 180, 28, 15, 0, 0, [(armor_list[3], 0.05), (materials_list[17], 0.25)]),
    Monster("어둠 기사", 150, 25, 10, 0, 5, [(weapon_list[3], 0.05), (armor_list[2], 0.05)]),
    Monster("빛 기사", 160, 27, 12, 0, 5, [(weapon_list[3], 0.05), (armor_list[2], 0.05)]),
    Monster("정령왕", 200, 30, 15, 20, 20, [(weapon_list[3], 0.05), (armor_list[3], 0.05), (materials_list[13], 0.3)]),
    Monster("드래곤 킹", 300, 40, 20, 25, 25, [(weapon_list[3], 0.05), (armor_list[3], 0.05), (materials_list[7], 0.25)])
]

# =======================
# 던전 정의
# =======================
dungeons = [
    Dungeon("초보자 숲", 1, monster_list[:5]),
    Dungeon("고블린 동굴", 3, monster_list[0:6]),
    Dungeon("늑대 숲", 5, monster_list[1:7]),
    Dungeon("마법사 유적", 7, monster_list[3:10]),
    Dungeon("드래곤 둥지", 10, monster_list[4:20])
]

# =======================
# 마을 정의
# =======================
towns = [
    Town("시작 마을", 1),
    Town("고블린 마을", 3),
    Town("늑대 마을", 5),
    Town("마법사 마을", 7),
    Town("드래곤 마을", 10)
]
# =======================
# app_part2.py
# =======================
import random
from app_part1 import Character, Monster, Dungeon, weapon_list, armor_list, materials_list

# =======================
# 전투 함수
# =======================
def attack_target(attacker, target):
    """일반 공격"""
    # 치명타 적용
    crit = random.random() < attacker.crit_rate
    if crit:
        damage = (attacker.attack - target.defense) * attacker.crit_damage
    else:
        damage = attacker.attack - target.defense
    damage = max(1, int(damage))
    target.hp -= damage
    return damage, crit

def magic_attack_target(attacker, target):
    """마법 공격"""
    damage = attacker.magic_attack - target.magic_defense
    damage = max(1, int(damage))
    target.hp -= damage
    return damage

# =======================
# 몬스터 드롭 획득
# =======================
def get_drops(monster):
    drops = []
    for item, prob in monster.loot_table:
        if random.random() < prob:
            drops.append(item)
    return drops

# =======================
# 보스 레이드 전투
# =======================
def boss_raid(player, boss):
    print(f"{boss.name} 보스를 만났습니다!")
    while boss.hp > 0 and player.hp > 0:
        # 플레이어 턴
        dmg, crit = attack_target(player, boss)
        print(f"플레이어 공격! {dmg} 피해 {'치명타!' if crit else ''} 남은 HP: {boss.hp}")
        if boss.hp <= 0:
            print(f"{boss.name} 처치 성공!")
            drops = get_drops(boss)
            print("획득 아이템:", [d.name for d in drops])
            player.inventory.extend(drops)
            player.gain_exp(50 + boss.attack)
            break

        # 보스 턴
        dmg, crit = attack_target(boss, player)
        print(f"{boss.name} 공격! {dmg} 피해 {'치명타!' if crit else ''} 남은 HP: {player.hp}")
        if player.hp <= 0:
            print("플레이어 사망! 회복 후 재도전하세요.")
            player.hp = player.max_hp
            break

# =======================
# 강화 시스템
# =======================
def enhance_item(item, success_rate=0.8):
    """아이템 강화"""
    if random.random() < success_rate:
        # 강화: 공격/방어 10% 증가
        if item.type == '무기':
            item.attack = int(item.attack * 1.1)
            item.crit_rate = min(1.0, item.crit_rate * 1.05)
        elif item.type == '갑옷':
            item.defense = int(item.defense * 1.1)
            item.magic_defense = int(item.magic_defense * 1.1)
        print(f"{item.name} 강화 성공!")
        return True
    else:
        print(f"{item.name} 강화 실패...")
        return False

# =======================
# 인첸트 시스템
# =======================
def enchant_item(item, attribute, value):
    """아이템 인첸트"""
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
    print(f"{item.name}에 {attribute}+{value} 인첸트 완료!")

# =======================
# 예시 전투 시뮬레이션
# =======================
if __name__ == "__main__":
    # 테스트용 캐릭터
    player = Character("테스터")
    player.weapon = weapon_list[0]
    player.armor = armor_list[0]

    # 테스트용 보스
    boss = Monster("드래곤", 200, 30, 10, 20, 15, [(weapon_list[3], 0.05), (armor_list[3], 0.05)])
    boss_raid(player, boss)

    # 강화/인첸트 테스트
    enhance_item(player.weapon)
    enchant_item(player.weapon, 'attack', 5)
    enchant_item(player.weapon, 'crit_rate', 0.05)
# =======================
# app_part3.py
# =======================
import streamlit as st
import random
from app_part1 import Character, Dungeon, Town, monster_list, weapon_list, armor_list, materials_list
from app_part2 import attack_target, magic_attack_target, get_drops, boss_raid, enhance_item, enchant_item

# =======================
# 게임 초기화
# =======================
if 'player' not in st.session_state:
    st.session_state.player = Character("용사")
    st.session_state.unlocked_spells = []

player = st.session_state.player

st.title("🛡️ Streamlit RPG 게임")

# =======================
# 월드맵 / 마을 / 던전 선택
# =======================
st.header("🌍 월드맵")

# 입장 가능한 마을 표시
st.subheader("마을")
for town in [t for t in Town.__subclasses__() if hasattr(t,'name')]:
    pass  # placeholder

st.write("입장 가능한 마을:")
for town in Town.__dict__.values():
    pass  # placeholder

st.subheader("던전")
available_dungeons = [d for d in Dungeon.__dict__.values() if hasattr(d,'name')]
st.write("입장 가능한 던전:")
for dungeon in available_dungeons:
    pass  # placeholder

# =======================
# 스탯 포인트 분배
# =======================
st.header("📈 스탯 포인트 분배")
st.write(f"남은 스탯 포인트: {player.status_points}")
if player.status_points > 0:
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

# =======================
# 마법 선택 및 해금
# =======================
st.header("🪄 마법 선택")
if player.level >= 5 and not player.element:
    element_choice = st.selectbox("원소를 선택하세요 (물, 불, 흙, 전기)", ["물","불","흙","전기"])
    if st.button("선택 확정"):
        player.element = element_choice
        st.success(f"{element_choice} 원소 선택 완료! 변경 불가")

# =======================
# 코드 입력 보상
# =======================
st.header("🎁 코드 입력 보상")
reward_code = st.text_input("코드를 입력하세요")
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

# =======================
# 장비 강화 / 인첸트
# =======================
st.header("🛠️ 장비 강화 / 인첸트")
if player.weapon:
    st.subheader(f"무기: {player.weapon.name}")
    if st.button("강화 무기"):
        enhance_item(player.weapon)
    attr = st.selectbox("인첸트 속성", ["attack","crit_rate","crit_damage","magic_attack"])
    val = st.number_input("인첸트 값", value=1)
    if st.button("인첸트 무기"):
        enchant_item(player.weapon, attr, val)

if player.armor:
    st.subheader(f"갑옷: {player.armor.name}")
    if st.button("강화 갑옷"):
        enhance_item(player.armor)
    attr2 = st.selectbox("인첸트 속성 (갑옷)", ["defense","magic_defense"])
    val2 = st.number_input("인첸트 값 (갑옷)", value=1)
    if st.button("인첸트 갑옷"):
        enchant_item(player.armor, attr2, val2)

# =======================
# 전투 진행
# =======================
st.header("⚔️ 던전 전투")
dungeon_names = [d.name for d in Dungeon.__dict__.values() if hasattr(d,'name')]
dungeon_choice = st.selectbox("던전 선택", dungeon_names)
if st.button("던전 입장"):
    # 간단 전투 시뮬레이션
    st.write(f"{dungeon_choice}에 입장!")
    dungeon = next((d for d in Dungeon.__dict__.values() if hasattr(d,'name') and d.name==dungeon_choice), None)
    if dungeon:
        monster = random.choice(dungeon.monsters)
        st.write(f"{monster.name} 등장!")
        dmg, crit = attack_target(player, monster)
        st.write(f"플레이어 공격! {dmg} 피해 {'치명타!' if crit else ''}")
        if monster.hp <= 0:
            st.write(f"{monster.name} 처치 성공!")
            drops = get_drops(monster)
            player.inventory.extend(drops)
            st.write("획득 아이템:", [i.name for i in drops])
