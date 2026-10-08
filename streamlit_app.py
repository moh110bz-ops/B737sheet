import streamlit as st

# --- 1. الثوابت والأذرع الهندسية الرسمية لطائرة B737-800 ---
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
    "DOW_ARM": 16.30,
    "Zone_A": 9.50,
    "Zone_B": 15.80,
    "Zone_C": 22.10,
    "Hold_1": 8.80,
    "Hold_2": 11.40,
    "Hold_3": 20.20,
    "Hold_4": 22.80,
    "Fuel": 16.20
}

LEMAC = 15.56
MAC_LENGTH = 3.713

st.set_page_config(page_title="AirSheet - B737-800", layout="wide")

# تخصيص ألوان البطاقات والنصوص (CSS)
st.markdown("""
<style>
    .badge-safe {
        background-color: #1e4620;
        color: #4caf50;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #2e7d32;
        font-size: 16px;
    }
    .badge-danger {
        background-color: #5c1d1d;
        color: #ff5252;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #d32f2f;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.title("AirSheet: B737-800 Weight & Balance Engine")
st.caption("نظام التوزين والتوازن العملياتي لـ Boeing 737-800")

col_input, col_visual = st.columns([1, 1])

with col_input:
    st.subheader("1. مدخلات الرحلة (Flight Inputs)")
    
    dow = st.number_input("الوزن الفارغ العملياتي (DOW kg):", value=43550, step=100)
    doi = st.number_input("مؤشر الوزن الفارغ (DOI Index):", value=48.2, step=0.1)
    
    st.markdown("---")
    st.write("**توزيع الركاب (Passenger Distribution):**")
    pax_a = st.number_input("Zone A (الصف 1-10) [الأقصى: 60]:", min_value=0, max_value=60, value=38, step=1)
    pax_b = st.number_input("Zone B (الصف 11-20) [الأقصى: 60]:", min_value=0, max_value=60, value=52, step=1)
    pax_c = st.number_input("Zone C (الصف 21-33) [الأقصى: 69]:", min_value=0, max_value=69, value=58, step=1)
    
    st.markdown("---")
    st.write("**توزيع عنابر الشحن (Cargo Holds kg):**")
    c1 = st.number_input("Hold 1 (FWD Upper):", min_value=0, max_value=LIMITS["HOLD1_MAX"], value=850, step=50)
    c2 = st.number_input("Hold 2 (FWD Lower):", min_value=0, max_value=LIMITS["HOLD2_MAX"], value=1450, step=50)
    c3 = st.number_input("Hold 3 (AFT Lower):", min_value=0, max_value=LIMITS["HOLD3_MAX"], value=1800, step=50)
    c4 = st.number_input("Hold 4 (AFT Upper):", min_value=0, max_value=LIMITS["HOLD4_MAX"], value=450, step=50)
    
    st.markdown("---")
    st.write("**بيانات الوقود (Fuel Data kg):**")
    to_fuel = st.number_input("وقود الإقلاع (Takeoff Fuel):", value=10800, step=100)
    trip_fuel = st.number_input("وقود الرحلة (Trip Fuel):", value=7200, step=100)

# الحسابات الأساسية
pax_a_wt = pax_a * 84
pax_b_wt = pax_b * 84
pax_c_wt = pax_c * 84

total_pax = pax_a + pax_b + pax_c
total_pax_wt = pax_a_wt + pax_b_wt + pax_c_wt
total_cargo_wt = c1 + c2 + c3 + c4

zfw = dow + total_pax_wt + total_cargo_wt
tow = zfw + to_fuel
lw = tow - trip_fuel

dow_moment = dow * ARMS["DOW_ARM"]
pax_moment = (pax_a_wt * ARMS["Zone_A"]) + (pax_b_wt * ARMS["Zone_B"]) + (pax_c_wt * ARMS["Zone_C"])
cargo_moment = (c1 * ARMS["Hold_1"]) + (c2 * ARMS["Hold_2"]) + (c3 * ARMS["Hold_3"]) + (c4 * ARMS["Hold_4"])
fuel_moment = to_fuel * ARMS["Fuel"]

total_takeoff_moment = dow_moment + pax_moment + cargo_moment + fuel_moment

cg_meters = total_takeoff_moment / tow
mac_percent = ((cg_meters - LEMAC) / MAC_LENGTH) * 100.0

with col_visual:
    st.subheader("2. الشاشة البصرية لتوزيع الأحمال")
    
    # تحديد ألوان حالة الأوزان والـ %MAC
    is_zfw_safe = zfw <= LIMITS["MZFW"]
    is_tow_safe = tow <= LIMITS["MTOW"]
    is_lw_safe = lw <= LIMITS["MLW"]
    is_mac_safe = LIMITS["MAC_MIN"] <= mac_percent <= LIMITS["MAC_MAX"]
    
    st.info(f"إجمالي الركاب: {total_pax} | إجمالي الشحن: {total_cargo_wt} kg")
    
    # عرض الأوزان والحدود الأقصى بصورة واضحة
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.caption(f"**ZFW (Max: {LIMITS['MZFW']:,} kg)**")
        st.metric(label="Zero Fuel Wt", value=f"{zfw:,} kg", delta="آمن" if is_zfw_safe else f"تجاوز (+{zfw - LIMITS['MZFW']} kg)", delta_color="normal" if is_zfw_safe else "inverse")
        
    with m2:
        st.caption(f"**TOW (Max: {LIMITS['MTOW']:,} kg)**")
        st.metric(label="Takeoff Wt", value=f"{tow:,} kg", delta="آمن" if is_tow_safe else f"تجاوز (+{tow - LIMITS['MTOW']} kg)", delta_color="normal" if is_tow_safe else "inverse")
        
    with m3:
        st.caption(f"**LW (Max: {LIMITS['MLW']:,} kg)**")
        st.metric(label="Landing Wt", value=f"{lw:,} kg", delta="آمن" if is_lw_safe else f"تجاوز (+{lw - LIMITS['MLW']} kg)", delta_color="normal" if is_lw_safe else "inverse")
    
    st.markdown("---")
    st.write("**مركز الثقل عند الإقلاع (%MAC):**")
    st.title(f"{mac_percent:.2f}%")
    
    # مربع حالة مركز الثقل الملون
    if is_mac_safe:
        st.markdown('<div class="badge-safe">آمن (داخل نطاق Envelope)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-danger">خارج النطاق</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### توزيع الكابينة بصرياً:")
    st.progress(pax_a / 60, text=f"Zone A: {pax_a} Pax")
    st.progress(pax_b / 60, text=f"Zone B: {pax_b} Pax")
    st.progress(pax_c / 69, text=f"Zone C: {pax_c} Pax")
    
    st.markdown("---")
    st.subheader("محرك التغيرات اللحظية واقتراح التوزيع (LMC Engine)")
    
    lmc_pax = st.number_input("تعديل ركاب لحظي (+/- Pax):", min_value=-50, max_value=50, value=0, step=1)
    lmc_cargo = st.number_input("تعديل أمتعة/شحن لحظي (+/- Cargo kg):", min_value=-2000, max_value=2000, value=0, step=5)
    
    if lmc_pax != 0 or lmc_cargo != 0:
        added_pax_wt = lmc_pax * 84
        new_tow = tow + added_pax_wt + lmc_cargo
        st.warning(f"وزن الإقلاع الجديد بعد الـ LMC: {new_tow:,} kg (التعديل: {added_pax_wt + lmc_cargo:+} kg)")
        
        st.markdown("#### مقترح التوزيع الذكي للـ LMC:")
        
        pax_suggestions = []
        if lmc_pax > 0:
            rem_pax = lmc_pax
            cap_a = 60 - pax_a
            cap_b = 60 - pax_b
            cap_c = 69 - pax_c
            
            alloc_a, alloc_b, alloc_c = 0, 0, 0
            
            for _ in range(rem_pax):
                if cap_a >= cap_c and cap_a > 0:
                    alloc_a += 1
                    cap_a -= 1
                elif cap_c > cap_a and cap_c > 0:
                    alloc_c += 1
                    cap_c -= 1
                elif cap_b > 0:
                    alloc_b += 1
                    cap_b -= 1
                else:
                    alloc_a += 1
                    
            if alloc_a > 0: pax_suggestions.append(f"• ضع {alloc_a}+ راكب في Zone A")
            if alloc_b > 0: pax_suggestions.append(f"• ضع {alloc_b}+ راكب في Zone B")
            if alloc_c > 0: pax_suggestions.append(f"• ضع {alloc_c}+ راكب في Zone C")
        elif lmc_pax < 0:
            pax_suggestions.append(f"• إلغاء {abs(lmc_pax)} راكب من المنطقة الأكثر ازدحاماً (Zone C أو Zone B)")

        cargo_suggestions = []
        if lmc_cargo > 0:
            if lmc_cargo <= 50:
                cargo_suggestions.append(f"• ضع {lmc_cargo}+ kg بالكامل في Hold 4 (AFT Bulk) للتداول السريع")
            else:
                fwd_part = round(lmc_cargo * 0.4)
                aft_part = lmc_cargo - fwd_part
                cargo_suggestions.append(f"• ضع {fwd_part}+ kg في Hold 2 (FWD)")
                cargo_suggestions.append(f"• ضع {aft_part}+ kg في Hold 3 (AFT) للحفاظ على التوازن")
        elif lmc_cargo < 0:
            cargo_suggestions.append(f"• إنقاص {abs(lmc_cargo)} kg من Hold 3 أو Hold 2")

        st.success("\n".join(pax_suggestions + cargo_suggestions))
        st.info("يمكنك الآن الصعود إلى الأعلى لتحديث خانات المدخلات الرئيسية بهذه الأرقام لاعتماد الـ Loadsheet النهائي.")
