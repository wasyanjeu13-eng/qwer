import streamlit as st
import random

# =======================
# 캐릭터 클래스
# =======================
if 'player' not in st.session_state:
    class Character:
        def __init__(self):
            self.name = "용사"
            self.level = 1
            self.exp = 0
            self.max_hp = 100
            self.hp = 100
            self.max_mp = 50
            self.mp = 50
            self.attack = 10
            self.defense = 5
            self.inventory = []
            self.weapon = None
            self.armor = None
            self.in_town = True  # 마을에 있는지 확인
            self.status_points = 0
    st.session_state.player = Character()

player = st.session_state.player

# =======================
# 아이템 클래스
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

# =======================
# 초기화 아이템
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
    Item("슬라임", "몬스터", attack=5, defense=1),
    Item("고블린", "몬스터", attack=8, defense=2),
    Item("늑대", "몬스터", attack=12, defense=3),
    Item("마법사", "몬스터", attack=5, defense=2),
    Item("오크", "몬스터", attack=15, defense=5),
    Item("거인", "몬스터", attack=20, defense=10),
    Item("마법정령", "몬스터", attack=8, defense=5),
    Item("해골병사", "몬스터", attack=10, defense=5),
    Item("유령", "몬스터", attack=8, defense=2),
    Item("드래곤", "몬스터", attack=30, defense=10)
]

# =======================
# 상태바 (항상 오른쪽)
# =======================
with st.sidebar:
    st.subheader(f"{player.name} 상태")
    st.progress(player.hp / player.max_hp)
    st.progress(player.mp / player.max_mp)
    st.write(f"레벨: {player.level}  HP: {player.hp}/{player.max_hp} MP: {player.mp}/{player.max_mp}")
    st.write(f"공격: {player.attack} 방어: {player.defense}")
    if player.weapon:
        st.write(f"무기: {player.weapon.name}")
    if player.armor:
        st.write(f"갑옷: {player.armor.name}")

# =======================
# 화면 틀
# =======================
st.title("Streamlit RPG 게임")

tab1, tab2 = st.tabs(["🏘️ 마을/던전", "🎒 인벤토리/전투"])

# =======================
# 마을/던전 탭
# =======================
with tab1:
    st.subheader("행선지 선택")
    place = st.radio("현재 위치", ["마을", "던전"])
    if place == "마을":
        st.write("마을에 도착! HP/MP 회복")
        player.hp = player.max_hp
        player.mp = player.max_mp
        player.in_town = True
    else:
        st.write("던전에 입장!")
        player.in_town = False
        # 몬스터 등장
        monster = random.choice(monster_list)
        st.write(f"몬스터 등장! {monster.name} HP: {monster.attack} 공격력 {monster.defense} 방어력")

# =======================
# 인벤토리/전투 탭
# =======================
with tab2:
    st.subheader("인벤토리")
    if player.inventory:
        for i, item in enumerate(player.inventory):
            st.write(f"{i+1}. {item.name} ({item.type})")
    else:
        st.write("인벤토리가 비었습니다.")
    
    # 장비 장착 및 해제
    if player.weapon:
        st.write(f"무기: {player.weapon.name}")
    equip_weapon = st.selectbox("무기 장착", [weapon.name for weapon in weapon_list], index=0)
    if st.button("무기 장착"):
        player.weapon = next((item for item in weapon_list if item.name == equip_weapon), None)
        st.success(f"{equip_weapon} 장착 완료!")
    
    if player.armor:
        st.write(f"갑옷: {player.armor.name}")
    equip_armor = st.selectbox("갑옷 장착", [armor.name for armor in armor_list], index=0)
    if st.button("갑옷 장착"):
        player.armor = next((item for item in armor_list if item.name == equip_armor), None)
        st.success(f"{equip_armor} 장착 완료!")

    # 전투 버튼
    if st.button("전투 시작"):
        if not player.in_town:
            st.write(f"전투 시작! {monster.name} 와 싸우기!")
            # 기본 전투 로직 (단순히 공격력만 비교)
            damage = player.attack - monster.attack
            if damage > 0:
                monster.attack -= damage
                st.write(f"{monster.name}에게 {damage} 데미지!")
            else:
                st.write(f"{monster.name}이(가) 너무 강하다!")

# =======================
# 아이템 코드 추가
# =======================
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
