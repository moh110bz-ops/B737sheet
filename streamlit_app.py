import streamlit as st
import plotly.graph_objects as go

# --- 1. Boeing 737-800 Structural Limits & Constants ---
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
    "CAP_A": 60,
    "CAP_B": 60,
    "CAP_C": 69
}

# Standard ICAO Passenger Weights
PAX_WEIGHTS = {
    "ADULT": 84,   # Adult standard weight (kg)
    "CHILD": 35,   # Child standard weight (kg)
    "INFANT": 10   # Infant standard weight (kg)
}

# Arms in meters from Datum (Nose)
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

# Custom Status Badges & Layout CSS
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
    .pax-breakdown {
        font-size: 13px;
        color: #b0bec5;
        margin-top: -10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("AirSheet: B737-800 Weight & Balance Engine")
st.caption("Operational Load Control & Trim System for Boeing 737-800")

col_input, col_visual = st.columns([1, 1])

with col_input:
    st.subheader("1. Flight & Load Inputs")
    
    dow = st.number_input("Dry Operating Weight (DOW kg):", value=43550, step=100)
    doi = st.number_input("Dry Operating Index (DOI):", value=48.2, step=0.1)
    
    st.markdown("---")
    st.write("**Passenger Demographics:**")
    
    c_pax1, c_pax2, c_pax3 = st.columns(3)
    with c_pax1:
        num_adults = st.number_input("Adults (84 kg):", min_value=0, max_value=170, value=130, step=1)
    with c_pax2:
        num_children = st.number_input("Children (35 kg):", min_value=0, max_value=50, value=10, step=1)
    with c_pax3:
        num_infants = st.number_input("Infants (10 kg):", min_value=0, max_value=20, value=3, step=1)
        
    total_pax_seats = num_adults + num_children
    
    auto_distribute = st.checkbox("Auto Seat Allocation Across Cabin", value=True)
    
    if auto_distribute:
        rem_seats = total_pax_seats
        
        pax_b = min(LIMITS["CAP_B"], int(rem_seats * 0.38))
        rem_seats -= pax_b
        
        pax_a = min(LIMITS["CAP_A"], int(rem_seats * 0.48))
        rem_seats -= pax_a
        
        pax_c = min(LIMITS["CAP_C"], rem_seats)
        
                # Calculate Category Breakdown per Zone
        actual_seated_pax = pax_a + pax_b + pax_c
        if actual_seated_pax > 0:
            ratio_a = pax_a / actual_seated_pax
            ratio_b = pax_b / actual_seated_pax
            ratio_c = pax_c / actual_seated_pax
        else:
            ratio_a = ratio_b = ratio_c = 0.33

        a_adult = round(num_adults * ratio_a)
        b_adult = round(num_adults * ratio_b)
        c_adult = num_adults - (a_adult + b_adult)

        a_child = round(num_children * ratio_a)
        b_child = round(num_children * ratio_b)
        c_child = num_children - (a_child + b_child)

        a_infant = round(num_infants * ratio_a)
        b_infant = round(num_infants * ratio_b)
        c_infant = num_infants - (a_infant + b_infant)

        st.info(
            f"**Auto Allocated:**\n\n"
            f"• **Zone A ({pax_a}):** {a_adult} Adult / {a_child} Child / {a_infant} Infant\n\n"
            f"• **Zone B ({pax_b}):** {b_adult} Adult / {b_child} Child / {b_infant} Infant\n\n"
            f"• **Zone C ({pax_c}):** {c_adult} Adult / {c_child} Child / {c_infant} Infant"
        )

    else:
        st.write("**Manual Cabin Seating:**")
        pax_a = st.number_input("Zone A (Rows 1-10):", min_value=0, max_value=LIMITS["CAP_A"], value=38, step=1)
        pax_b = st.number_input("Zone B (Rows 11-20):", min_value=0, max_value=LIMITS["CAP_B"], value=52, step=1)
        pax_c = st.number_input("Zone C (Rows 21-33):", min_value=0, max_value=LIMITS["CAP_C"], value=50, step=1)

    st.markdown("---")
    st.write("**Cargo Holds Loading (kg):**")
    c1 = st.number_input("Hold 1 (FWD Upper):", min_value=0, max_value=LIMITS["HOLD1_MAX"], value=850, step=50)
    c2 = st.number_input("Hold 2 (FWD Lower):", min_value=0, max_value=LIMITS["HOLD2_MAX"], value=1450, step=50)
    c3 = st.number_input("Hold 3 (AFT Lower):", min_value=0, max_value=LIMITS["HOLD3_MAX"], value=1800, step=50)
    c4 = st.number_input("Hold 4 (AFT Upper):", min_value=0, max_value=LIMITS["HOLD4_MAX"], value=450, step=50)
    
    st.markdown("---")
    st.write("**Fuel Management (kg):**")
    to_fuel = st.number_input("Takeoff Fuel (TBOF):", value=10800, step=100)
    trip_fuel = st.number_input("Trip Fuel:", value=7200, step=100)

# 1. Structural Mass Calculations
total_pax_wt = (num_adults * PAX_WEIGHTS["ADULT"]) + (num_children * PAX_WEIGHTS["CHILD"]) + (num_infants * PAX_WEIGHTS["INFANT"])
total_cargo_wt = c1 + c2 + c3 + c4

zfw = dow + total_pax_wt + total_cargo_wt
tow = zfw + to_fuel
lw = tow - trip_fuel

# 2. Zone Breakdown Calculation
actual_seated_pax = pax_a + pax_b + pax_c
if actual_seated_pax > 0:
    ratio_a = pax_a / actual_seated_pax
    ratio_b = pax_b / actual_seated_pax
    ratio_c = pax_c / actual_seated_pax
else:
    ratio_a = ratio_b = ratio_c = 0.33

a_adult = round(num_adults * ratio_a)
b_adult = round(num_adults * ratio_b)
c_adult = num_adults - (a_adult + b_adult)

a_child = round(num_children * ratio_a)
b_child = round(num_children * ratio_b)
c_child = num_children - (a_child + b_child)

a_infant = round(num_infants * ratio_a)
b_infant = round(num_infants * ratio_b)
c_infant = num_infants - (a_infant + b_infant)

avg_pax_seat_wt = (total_pax_wt / actual_seated_pax) if actual_seated_pax > 0 else 84

pax_a_wt = pax_a * avg_pax_seat_wt
pax_b_wt = pax_b * avg_pax_seat_wt
pax_c_wt = pax_c * avg_pax_seat_wt

dow_moment = dow * ARMS["DOW_ARM"]
pax_moment = (pax_a_wt * ARMS["Zone_A"]) + (pax_b_wt * ARMS["Zone_B"]) + (pax_c_wt * ARMS["Zone_C"])
cargo_moment = (c1 * ARMS["Hold_1"]) + (c2 * ARMS["Hold_2"]) + (c3 * ARMS["Hold_3"]) + (c4 * ARMS["Hold_4"])
fuel_moment = to_fuel * ARMS["Fuel"]

total_takeoff_moment = dow_moment + pax_moment + cargo_moment + fuel_moment

cg_meters = total_takeoff_moment / tow
mac_percent = ((cg_meters - LEMAC) / MAC_LENGTH) * 100.0

with col_visual:
    st.subheader("2. Graphical Load Distribution")
    
    is_zfw_safe = zfw <= LIMITS["MZFW"]
    is_tow_safe = tow <= LIMITS["MTOW"]
    is_lw_safe = lw <= LIMITS["MLW"]
    is_mac_safe = LIMITS["MAC_MIN"] <= mac_percent <= LIMITS["MAC_MAX"]
    
    st.info(f"Total Pax: {total_pax_seats} (Adults: {num_adults} / Children: {num_children} / Infants: {num_infants}) | Total Cargo: {total_cargo_wt} kg")
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.caption(f"**ZFW (Max: {LIMITS['MZFW']:,} kg)**")
        st.metric(label="Zero Fuel Wt", value=f"{zfw:,} kg", delta="SAFE" if is_zfw_safe else f"EXCEEDED (+{zfw - LIMITS['MZFW']} kg)", delta_color="normal" if is_zfw_safe else "inverse")
        
    with m2:
        st.caption(f"**TOW (Max: {LIMITS['MTOW']:,} kg)**")
        st.metric(label="Takeoff Wt", value=f"{tow:,} kg", delta="SAFE" if is_tow_safe else f"EXCEEDED (+{tow - LIMITS['MTOW']} kg)", delta_color="normal" if is_tow_safe else "inverse")
        
    with m3:
        st.caption(f"**LW (Max: {LIMITS['MLW']:,} kg)**")
        st.metric(label="Landing Wt", value=f"{lw:,} kg", delta="SAFE" if is_lw_safe else f"EXCEEDED (+{lw - LIMITS['MLW']} kg)", delta_color="normal" if is_lw_safe else "inverse")
      # --- Interactive Trim Sheet Envelope Graph ---
    st.markdown("---")
    st.markdown("### 📈 CG Trim Sheet Envelope")

    # 1. Precise CG (%MAC) Calculations for ZFW & LW
    zfw_moment = dow_moment + pax_moment + cargo_moment
    zfw_cg_meters = zfw_moment / zfw if zfw > 0 else 0
    zfw_mac = ((zfw_cg_meters - LEMAC) / MAC_LENGTH) * 100.0

    lw_moment = zfw_moment + ((to_fuel - trip_fuel) * ARMS["Fuel"])
    lw_cg_meters = lw_moment / lw if lw > 0 else 0
    lw_mac = ((lw_cg_meters - LEMAC) / MAC_LENGTH) * 100.0

    # 2. B737-800 Envelope Structural Boundaries (%MAC vs Weight kg)
    envelope_mac = [8.0, 8.0, 15.0, 33.0, 33.0, 8.0]
    envelope_weight = [40000, 62731, 79015, 79015, 40000, 40000]

    # 3. Create Graphical Figure & Add Safe Envelope Boundary Line
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=envelope_mac, 
        y=envelope_weight,
        fill="toself",
        fillcolor="rgba(46, 125, 50, 0.2)",
        line=dict(color="#2e7d32", width=2),
        name="Safe Envelope Boundary"
    ))

    # 4. Add Current Flight CG Trajectory Points (ZFW -> TOW -> LW)
    fig.add_trace(go.Scatter(
        x=[zfw_mac, mac_percent, lw_mac],
        y=[zfw, tow, lw],
        mode="lines+markers+text",
        text=["ZFW", "TOW", "LW"],
        textposition="top center",
        marker=dict(size=10, color=["#ab47bc", "#66bb6a", "#29b6f6"]),
        line=dict(color="#ffffff", width=2, dash="dash"),
        name="Flight CG Vector"
    ))

    # 5. Customize Chart Layout & Display in Streamlit
    fig.update_layout(
        title="B737-800 Takeoff & Landing CG Limits",
        xaxis_title="%MAC (Center of Gravity)",
        yaxis_title="Weight (kg)",
        xaxis=dict(range=[0, 40], gridcolor="#333"),
        yaxis=dict(range=[35000, 82000], gridcolor="#333"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(color="#ffffff"),
        height=380,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
      
    st.plotly_chart(fig, use_container_width=True)

    # B737-800 Envelope Structural Boundaries (%MAC vs Weight kg)
    envelope_mac = [8.0, 8.0, 15.0, 33.0, 33.0, 8.0]
    envelope_weight = [40000, 62731, 79015, 79015, 40000, 40000]

    st.markdown("---")
    st.write("**Takeoff Center of Gravity (%MAC):**")
    st.title(f"{mac_percent:.2f}%")
    
    if is_mac_safe:
        st.markdown('<div class="badge-safe">SAFE (In Envelope)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-danger">OUT OF ENVELOPE</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Cabin Seating Visualizer:")
    
    # Zone A
    st.progress(pax_a / LIMITS["CAP_A"], text=f"Zone A: {pax_a} Pax")
    st.markdown(f'<div class="pax-breakdown"><b>{a_adult} Adult / {a_child} Child / {a_infant} Infant</b></div>', unsafe_allow_html=True)
    
    # Zone B
    st.progress(pax_b / LIMITS["CAP_B"], text=f"Zone B: {pax_b} Pax")
    st.markdown(f'<div class="pax-breakdown"><b>{b_adult} Adult / {b_child} Child / {b_infant} Infant</b></div>', unsafe_allow_html=True)
    
    # Zone C
    st.progress(pax_c / LIMITS["CAP_C"], text=f"Zone C: {pax_c} Pax")
    st.markdown(f'<div class="pax-breakdown"><b>{c_adult} Adult / {c_child} Child / {c_infant} Infant</b></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Last Minute Changes (LMC Engine)")
    
    lmc_pax = st.number_input("LMC Pax (+/- Pax):", min_value=-50, max_value=50, value=0, step=1)
    lmc_cargo = st.number_input("LMC Cargo (+/- kg):", min_value=-2000, max_value=2000, value=0, step=5)
    
    if lmc_pax != 0 or lmc_cargo != 0:
        added_pax_wt = lmc_pax * 84
        new_tow = tow + added_pax_wt + lmc_cargo
        st.warning(f"New Takeoff Weight after LMC: {new_tow:,} kg (Delta: {added_pax_wt + lmc_cargo:+} kg)")
        
        st.markdown("#### Smart LMC Re-allocation Recommendation:")
        
        pax_suggestions = []
        if lmc_pax > 0:
            rem_pax = lmc_pax
            cap_a = LIMITS["CAP_A"] - pax_a
            cap_b = LIMITS["CAP_B"] - pax_b
            cap_c = LIMITS["CAP_C"] - pax_c
            
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
                    
            if alloc_a > 0: pax_suggestions.append(f"• Add {alloc_a} Pax in Zone A")
            if alloc_b > 0: pax_suggestions.append(f"• Add {alloc_b} Pax in Zone B")
            if alloc_c > 0: pax_suggestions.append(f"• Add {alloc_c} Pax in Zone C")
        elif lmc_pax < 0:
            pax_suggestions.append(f"• Offload {abs(lmc_pax)} Pax from congested area (Zone C / Zone B)")

        cargo_suggestions = []
        if lmc_cargo > 0:
            if lmc_cargo <= 50:
                cargo_suggestions.append(f"• Load {lmc_cargo} kg into Hold 4 (AFT Bulk) for quick dispatch")
            else:
                fwd_part = round(lmc_cargo * 0.4)
                aft_part = lmc_cargo - fwd_part
                cargo_suggestions.append(f"• Load {fwd_part} kg into Hold 2 (FWD)")
                cargo_suggestions.append(f"• Load {aft_part} kg into Hold 3 (AFT) for CG balance")
        elif lmc_cargo < 0:
            cargo_suggestions.append(f"• Offload {abs(lmc_cargo)} kg from Hold 3 or Hold 2")

        st.success("\n".join(pax_suggestions + cargo_suggestions))
        st.info("You can now update the main flight inputs above with these figures to finalize the Loadsheet.")
