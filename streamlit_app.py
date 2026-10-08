import streamlit as st

# --- 1. الثوابت والأذرع الهندسية الرسمية لطائرة B737-800 (Datum = Nose) ---
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

# الأذرع الهندسية بالمتر من مقدمة الطائرة (Arms in meters)
ARMS = {
    "DOW_ARM": 16.30,  # الذراع الافتراضي للوزن التشغيلي الفارغ
    "Zone_A": 9.50,    # الصفوف 1-10
    "Zone_B": 15.80,   # الصفوف 11-20
    "Zone_C": 22.10,   # الصفوف 21-33
    "Hold_1": 8.80,    # FWD Upper
    "Hold_2": 11.40,   # FWD Lower
    "Hold_3": 20.20,   # AFT Lower
    "Hold_4": 22.80,   # AFT Upper
    "Fuel": 16.20      # Main & Center Tanks Mean Arm
}

# ثوابت الوتر الوسطي للجناح (Mean Aerodynamic Chord)
LEMAC = 15.56  # Leading Edge of MAC in meters
MAC_LENGTH = 3.713  # Length of MAC in meters

st.set_page_config(page_title="AirSheet - B737-800", layout="wide")

st.title("✈️ AirSheet: B737-800 Weight & Balance Engine")
st.caption("نظام التوزين والتوازن العملياتي لـ Boeing 737-800")

col_input, col_visual = st.columns([1, 1])

with col_input:
    st.subheader("1. مدخلات الرحلة (Flight Inputs)")
    
    dow = st.number_input("الوزن الفارغ العملياتي (DOW kg):", value=43550)
    doi = st.number_input("مؤشر الوزن الفارغ (DOI Index):", value=48.2)
    
    st.markdown("---")
    st.write("**توزيع الركاب (Passenger Distribution):**")
    pax_a = st.slider("Zone A (الصف 1-10):", 0, 60, 38)
    pax_b = st.slider("Zone B (الصف 11-20):", 0, 60, 52)
    pax_c = st.slider("Zone C (الصف 21-33):", 0, 69, 58)
    
    st.markdown("---")
    st.write("**توزيع العنابر الشحن (Cargo Holds kg):**")
    c1 = st.number_input("Hold 1 (FWD Upper):", 0, LIMITS["HOLD1_MAX"], 850)
    c2 = st.number_input("Hold 2 (FWD Lower):", 0, LIMITS["HOLD2_MAX"], 1450)
    c3 = st.number_input("Hold 3 (AFT Lower):", 0, LIMITS["HOLD3_MAX"], 1800)
    c4 = st.number_input("Hold 4 (AFT Upper):", 0, LIMITS["HOLD4_MAX"], 450)
    
    st.markdown("---")
    st.write("**بيانات الوقود (Fuel Data kg):**")
    to_fuel = st.number_input("وقود الإقلاع (Takeoff Fuel):", value=10800)
    trip_fuel = st.number_input("وقود الرحلة (Trip Fuel):", value=7200)

# 2. أوزان الأحمال
pax_a_wt = pax_a * 84
pax_b_wt = pax_b * 84
pax_c_wt = pax_c * 84

total_pax = pax_a + pax_b + pax_c
total_pax_wt = pax_a_wt + pax_b_wt + pax_c_wt
total_cargo_wt = c1 + c2 + c3 + c4

zfw = dow + total_pax_wt + total_cargo_wt
tow = zfw + to_fuel
lw = tow - trip_fuel

# 3. حساب العزوم الكلية (Moments Calculation)
dow_moment = dow * ARMS["DOW_ARM"]
pax_moment = (pax_a_wt * ARMS["Zone_A"]) + (pax_b_wt * ARMS["Zone_B"]) + (pax_c_wt * ARMS["Zone_C"])
cargo_moment = (c1 * ARMS["Hold_1"]) + (c2 * ARMS["Hold_2"]) + (c3 * ARMS["Hold_3"]) + (c4 * ARMS["Hold_4"])
fuel_moment = to_fuel * ARMS["Fuel"]

total_takeoff_moment = dow_moment + pax_moment + cargo_moment + fuel_moment

# 4. حساب موقع مركز الثقل (CG Position & %MAC)
cg_meters = total_takeoff_moment / tow
mac_percent = ((cg_meters - LEMAC) / MAC_LENGTH) * 100.0

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
