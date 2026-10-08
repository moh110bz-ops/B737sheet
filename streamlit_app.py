import streamlit as st

# --- 1. الثوابت والحدود الهيكلية لطائرة B737-800 ---
LIMITS = {
    "MTOW": 79015,  # Max Takeoff Weight (kg)
    "MZFW": 62731,  # Max Zero Fuel Weight (kg)
    "MLW": 65317,   # Max Landing Weight (kg)
    "HOLD1_MAX": 2268,
    "HOLD2_MAX": 3206,
    "HOLD3_MAX": 4241,
    "HOLD4_MAX": 2857,
    "MAC_MIN": 8.0,   # %MAC Safe Limit Low
    "MAC_MAX": 33.0,  # %MAC Safe Limit High
}

ARMS = {
    "Zone_A": -12.5, "Zone_B": 0.0, "Zone_C": 14.2,
    "Hold_1": -14.8, "Hold_2": -8.5, "Hold_3": 9.2, "Hold_4": 15.6,
    "Fuel": 1.2
}

st.set_page_config(page_title="AirSheet - B737-800", layout="wide")

st.title("✈️ AirSheet: B737-800 Weight & Balance Engine")
st.caption("نظام التوزين والتوازن العملياتي لـ Boeing 737-800")

col_input, col_visual = st.columns([1, 1])

with col_input:
    st.subheader("1. مدخلات الرحلة (Flight Inputs)")
    
    dow = st.number_input("الوزن الفارغ العملياتي (DOW kg):", value=43000)
    doi = st.number_input("مؤشر الوزن الفارغ (DOI Index):", value=45.0)
    
    st.markdown("---")
    st.write("**توزيع الركاب (Passenger Distribution):**")
    pax_a = st.slider("Zone A (الصف 1-10):", 0, 60, 45)
    pax_b = st.slider("Zone B (الصف 11-20):", 0, 60, 50)
    pax_c = st.slider("Zone C (الصف 21-33):", 0, 69, 55)
    
    st.markdown("---")
    st.write("**توزيع العنابر الشحن (Cargo Holds kg):**")
    c1 = st.number_input("Hold 1 (FWD Upper):", 0, LIMITS["HOLD1_MAX"], 1200)
    c2 = st.number_input("Hold 2 (FWD Lower):", 0, LIMITS["HOLD2_MAX"], 1500)
    c3 = st.number_input("Hold 3 (AFT Lower):", 0, LIMITS["HOLD3_MAX"], 2000)
    c4 = st.number_input("Hold 4 (AFT Upper):", 0, LIMITS["HOLD4_MAX"], 800)
    
    st.markdown("---")
    st.write("**بيانات الوقود (Fuel Data kg):**")
    to_fuel = st.number_input("وقود الإقلاع (Takeoff Fuel):", value=11000)
    trip_fuel = st.number_input("وقود الرحلة (Trip Fuel):", value=8500)

# الحسابات
total_pax = pax_a + pax_b + pax_c
total_pax_wt = total_pax * 84
total_cargo_wt = c1 + c2 + c3 + c4

zfw = dow + total_pax_wt + total_cargo_wt
tow = zfw + to_fuel
lw = tow - trip_fuel

delta_index = (
    (pax_a * 84 * ARMS["Zone_A"] + pax_b * 84 * ARMS["Zone_B"] + pax_c * 84 * ARMS["Zone_C"]) +
    (c1 * ARMS["Hold_1"] + c2 * ARMS["Hold_2"] + c3 * ARMS["Hold_3"] + c4 * ARMS["Hold_4"]) +
    (to_fuel * ARMS["Fuel"])
) / 1000.0

final_index = doi + delta_index
mac_percent = 18.5 + (delta_index * 100.0 / (tow / 1000.0))

with col_visual:
    st.subheader("2. الشاشة البصرية لتوزيع الأحمال")
    
    zfw_status = "✅ آمن" if zfw <= LIMITS["MZFW"] else f"🚨 إجهاد وزن! (+{zfw - LIMITS['MZFW']}kg)"
    tow_status = "✅ آمن" if tow <= LIMITS["MTOW"] else f"🚨 إجهاد إقلاع! (+{tow - LIMITS['MTOW']}kg)"
    mac_status = "✅ آمن (داخل الـ Envelope)" if LIMITS["MAC_MIN"] <= mac_percent <= LIMITS["MAC_MAX"] else "🚨 خارج النطاق!"
    
    st.info(f"**إجمالي الركاب:** {total_pax} | **إجمالي الشحن:** {total_cargo_wt} kg")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("ZFW (kg)", f"{zfw:,}", zfw_status)
    m2.metric("TOW (kg)", f"{tow:,}", tow_status)
    m3.metric("Landing Wt (kg)", f"{lw:,}", f"Max: {LIMITS['MLW']:,}")
    
    st.markdown("---")
    st.metric("مركز الثقل عند الإقلاع (%MAC)", f"{mac_percent:.2f}%", mac_status)
    
    st.markdown("### ✈️ توزيع الكابينة بصرياً:")
    st.progress(pax_a / 60, text=f"Zone A: {pax_a} Pax")
    st.progress(pax_b / 60, text=f"Zone B: {pax_b} Pax")
    st.progress(pax_c / 69, text=f"Zone C: {pax_c} Pax")
    
    st.markdown("---")
    st.subheader("⚡ محرك التغيرات اللحظية (LMC Engine)")
    lmc_pax = st.number_input("تعديل ركاب لحظي (+/- Pax):", value=0)
    lmc_cargo = st.number_input("تعديل شحن لحظي (+/- Cargo kg):", value=0)
    
    if lmc_pax != 0 or lmc_cargo != 0:
        new_tow = tow + (lmc_pax * 84) + lmc_cargo
        st.warning(f"وزن الإقلاع الجديد بعد الـ LMC: **{new_tow:,} kg**")
