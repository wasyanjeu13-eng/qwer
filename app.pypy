# Streamlit 강화 게임 완성본
# (방지권은 파괴만 방지, 성공 처리 없음)
# 이미지/일러스트 + 강화/실패/파괴 GIF 포함 버전

import streamlit as st
import random

st.set_page_config(page_title="강화 게임", layout="wide")

# 기본 초기화
if "level" not in st.session_state:
    st.session_state.level = 0
if "break_protection" not in st.session_state:
    st.session_state.break_protection = 5
if "message" not in st.session_state:
    st.session_state.message = ""
if "protection_choice" not in st.session_state:
    st.session_state.protection_choice = False
if "pending_failure_level" not in st.session_state:
    st.session_state.pending_failure_level = None

# 강화 확률 테이블 (0~30)
success_rates = [100,95,90,85,80,75,70,65,60,55,50,45,40,35,30,28,26,24,22,20,18,16,14,12,10,8,6,5,4,3,2,2]
break_rates   = [0,0,0,0,0,0,0,1,2,3,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,35,38,40,45,50,55,60]

# 검 이미지 (레벨별)
weapon_images = {i: f"https://raw.githubusercontent.com/ChatGPT-Gfx/swords/main/sword_{i}.png" for i in range(0, 31)}

# 이펙트 GIF
effect_images = {
    "success": "https://raw.githubusercontent.com/ChatGPT-Gfx/effects/main/success.gif",
    "fail": "https://raw.githubusercontent.com/ChatGPT-Gfx/effects/main/fail.gif",
    "break": "https://raw.githubusercontent.com/ChatGPT-Gfx/effects/main/break.gif"
}

# 함수 정의
def apply_failure(destroy):
    if destroy:
        st.session_state.level = 0
        st.session_state.message = "💥 무기가 파괴되었습니다! 0레벨로 초기화!"
    else:
        st.session_state.message = "❌ 강화 실패..."

def upgrade():
    level = st.session_state.level
    succ = success_rates[level]
    brk = break_rates[level]

    roll = random.randint(1,100)

    if roll <= succ:
        st.session_state.level += 1
        st.session_state.message = f"🌈 강화 성공! +{st.session_state.level}"
    elif roll > 100 - brk:
        st.session_state.pending_failure_level = level
        st.session_state.protection_choice = True
        st.session_state.message = "💥 실패! 무기가 파괴될 위기입니다!"
    else:
        apply_failure(False)

# UI
st.title("⚔ 강화 게임 완성본")
weapon_img = weapon_images.get(st.session_state.level, weapon_images[0])
st.image(weapon_img, width=200)
st.markdown(f"## 🔥 현재 레벨: **+{st.session_state.level}**")
st.markdown(f"### 🛡 방지권: {st.session_state.break_protection}개")

if st.button("✨ 강화하기"):
    upgrade()

# 메시지 + 이펙트
if "성공" in st.session_state.message:
    st.image(effect_images["success"], width=200)
elif "파괴" in st.session_state.message:
    st.image(effect_images["break"], width=200)
elif "실패" in st.session_state.message:
    st.image(effect_images["fail"], width=200)

st.markdown(f"### 📢 {st.session_state.message}")

# 방지권 UI
if st.session_state.protection_choice:
    st.warning("❗ 강화 실패! 방지권을 사용하여 무기 파괴만 막을 수 있습니다.")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🛡 방지권 사용 (파괴만 방지)"):
            if st.session_state.break_protection > 0:
                st.session_state.break_protection -= 1
                st.session_state.level = st.session_state.pending_failure_level
                st.session_state.message = "🛡 방지권 발동! 무기 파괴 방지, 레벨 유지"
            else:
                st.session_state.message = "❌ 방지권 부족"
            st.session_state.protection_choice = False
            st.session_state.pending_failure_level = None

    with col2:
        if st.button("💥 파괴 확정"):
            apply_failure(True)
            st.session_state.protection_choice = False
            st.session_state.pending_failure_level = None
