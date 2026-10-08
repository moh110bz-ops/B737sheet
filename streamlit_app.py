import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="AirSheet - Sudan Fleet & Load Control", layout="wide")

st.markdown("""
<style>
    .hero-title {
        font-size: 36px;
        font-weight: bold;
        color: #0288d1;
        text-align: center;
        margin-top: 10px;
    }
    .hero-subtitle {
        font-size: 18px;
        color: #b0bec5;
        text-align: center;
        margin-bottom: 30px;
    }
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

# --- SUDAN 5 COMMON AIRCRAFT TYPES PRE-CONFIGURED DATABASE ---
if "fleet_db" not in st.session_state:
    st.session_state.fleet_db = {
        "ST-BDG": {
            "registration": "ST-BDG",
            "airline": "Bader Airlines",
            "type": "B737-800",
            "status": "Operational",
            "dow": 43550,
            "doi": 48.2,
            "is_restricted": False,
            "limits": {
                "MTOW": 79015, "MZFW": 62731, "MLW": 65317,
                "HOLD1_MAX": 2268, "HOLD2_MAX": 3206, "HOLD3_MAX": 4241, "HOLD4_MAX": 2857,
                "MAC_MIN": 8.0, "MAC_MAX": 33.0, "CAP_A": 60, "CAP_B": 60, "CAP_C": 69
            }
        },
        "ST-TRK": {
            "registration": "ST-TRK",
            "airline": "Tarco Aviation",
            "type": "B737-300",
            "status": "Operational",
            "dow": 32800,
            "doi": 42.1,
            "is_restricted": False,
            "limits": {
                "MTOW": 62820, "MZFW": 51710, "MLW": 54885,
                "HOLD1_MAX": 1500, "HOLD2_MAX": 2500, "HOLD3_MAX": 3000, "HOLD4_MAX": 1200,
                "MAC_MIN": 10.0, "MAC_MAX": 30.0, "CAP_A": 40, "CAP_B": 45, "CAP_C": 43
            }
        },
        "ST-AZB": {
            "registration": "ST-AZB",
            "airline": "Sudan Airways",
            "type": "B737-500",
            "status": "Operational",
            "dow": 31500,
            "doi": 39.4,
            "is_restricted": False,
            "limits": {
                "MTOW": 60550, "MZFW": 49895, "MLW": 53070,
                "HOLD1_MAX": 1200, "HOLD2_MAX": 2200, "HOLD3_MAX": 2800, "HOLD4_MAX": 1000,
                "MAC_MIN": 9.0, "MAC_MAX": 31.0, "CAP_A": 35, "CAP_B": 40, "CAP_C": 36
            }
        },
        "ST-ABW": {
            "registration": "ST-ABW",
            "airline": "Abyssinia Flight",
            "type": "A320",
            "status": "Operational",
            "dow": 42600,
            "doi": 45.0,
            "is_restricted": False,
            "limits": {
                "MTOW": 77000, "MZFW": 62500, "MLW": 66000,
                "HOLD1_MAX": 2000, "HOLD2_MAX": 3500, "HOLD3_MAX": 3500, "HOLD4_MAX": 1500,
                "MAC_MIN": 12.0, "MAC_MAX": 38.0, "CAP_A": 50, "CAP_B": 60, "CAP_C": 70
            }
        },
        "ST-ATR": {
            "registration": "ST-ATR",
            "airline": "Domestic Regional",
            "type": "ATR 72",
            "status": "Operational",
            "dow": 13000,
            "doi": 25.0,
            "is_restricted": False,
            "limits": {
                "MTOW": 23000, "MZFW": 21500, "MLW": 22350,
                "HOLD1_MAX": 800, "HOLD2_MAX": 0, "HOLD3_MAX": 1200, "HOLD4_MAX": 0,
                "MAC_MIN": 15.0, "MAC_MAX": 35.0, "CAP_A": 24, "CAP_B": 24, "CAP_C": 24
            }
        }
    }

if "selected_tail" not in st.session_state:
    st.session_state.selected_tail = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# TOP NAVIGATION BAR
nav_col1, nav_col2, nav_col3 = st.columns([2, 1, 1])

with nav_col1:
    if st.button("Home Hub"):
        st.session_state.current_page = "Home"

with nav_col2:
    if st.button("Add New Aircraft"):
        st.session_state.current_page = "Add_Aircraft"

with nav_col3:
    if st.button("Edit Aircraft Profile"):
        st.session_state.current_page = "Edit_Aircraft"

st.markdown("---")

PAX_WEIGHTS = {"ADULT": 84, "CHILD": 35, "INFANT": 10}
ARMS = {
    "DOW_ARM": 16.30, "Zone_A": 9.50, "Zone_B": 15.80, "Zone_C": 22.10,
    "Hold_1": 8.80, "Hold_2": 11.40, "Hold_3": 20.20, "Hold_4": 22.80, "Fuel": 16.20
}
LEMAC = 15.56
MAC_LENGTH = 3.713


# ==============================================================================
# 1. HOME PAGE (WELCOME & SELECTION)
# ==============================================================================
if st.session_state.current_page == "Home":
    st.markdown('<div class="hero-title">AirSheet Flight Dispatch & Load Control Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">'
        'Advanced Fleet Weight & Balance and Operational Load Management System.<br>'
        'Where aviation engineering precision meets the highest standards of flight safety.'
        '</div>', 
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    c_search_1, c_search_2, c_search_3 = st.columns([1, 2, 1])
    with c_search_2:
        st.subheader("Select Aircraft from System Fleet:")
        available_tails = list(st.session_state.fleet_db.keys())
        if available_tails:
            selected_tail_choice = st.selectbox("Select Tail Registration:", available_tails, index=0)
            if selected_tail_choice:
                ac_info = st.session_state.fleet_db[selected_tail_choice]
                st.info(f"**Operator:** {ac_info['airline']} | **Type:** {ac_info['type']} | **Base DOW:** {ac_info['dow']:,} kg")
                if ac_info["is_restricted"]:
                    st.warning(f"⚠️ **Operational Restriction Active:** {ac_info.get('restriction_reason', 'MEL Limits')}")
                if st.button("Launch Loadsheet & Calculations", use_container_width=True):
                    st.session_state.selected_tail = selected_tail_choice
                    st.session_state.current_page = "WNB_Engine"
                    st.rerun()
        else:
            st.info("No aircraft registered in the system yet. Please click 'Add New Aircraft' above to start.")


# ==============================================================================
# 2. PAGE: ADD NEW AIRCRAFT
# ==============================================================================
elif st.session_state.current_page == "Add_Aircraft":
    st.title("Add New Aircraft to Fleet")
    st.caption("Register a new tail profile with specific DOW, DOI, and structural or MEL operational limits.")
    
    new_reg = st.text_input("Registration / Tail Number:", value="", placeholder="ST-SUD").strip().upper()
    new_operator = st.text_input("Airline / Operator:", value="", placeholder="Sudan Airline Operator")
    new_type = st.selectbox("Aircraft Type:", ["B737-800", "B737-500", "B737-300", "A320", "ATR 72"])
    
    new_dow = st.number_input("Dry Operating Weight (DOW kg):", value=0.0, step=100.0, format="%.1f")
    new_doi = st.number_input("Dry Operating Index (DOI):", value=0.0, step=0.1, format="%.1f")
    
    limit_mode = st.radio(
        "Structural Limit Mode:",
        ["Manufacturer Standard Limits", "Custom Operational Limits / MEL Derate"]
    )
    
    if limit_mode == "Manufacturer Standard Limits":
        limits_data = {
            "MTOW": 79015, "MZFW": 62731, "MLW": 65317,
            "HOLD1_MAX": 2268, "HOLD2_MAX": 3206, "HOLD3_MAX": 4241, "HOLD4_MAX": 2857,
            "MAC_MIN": 8.0, "MAC_MAX": 33.0, "CAP_A": 60, "CAP_B": 60, "CAP_C": 69
        }
        is_restr = False
        restr_reason = ""
    else:
        is_restr = True
        restr_reason = st.text_input("Restriction / Defect Reason (MEL):", value="", placeholder="Brake Limitation Penalty")
        c1, c2, c3 = st.columns(3)
        with c1:
            mtow_v = st.number_input("Max Takeoff Weight (MTOW kg):", value=0, step=500)
            h1_v = st.number_input("Hold 1 Max Limit (kg):", value=0, step=100)
            h2_v = st.number_input("Hold 2 Max Limit (kg):", value=0, step=100)
        with c2:
            mzfw_v = st.number_input("Max Zero Fuel Weight (MZFW kg):", value=0, step=500)
            h3_v = st.number_input("Hold 3 Max Limit (kg):", value=0, step=100)
        with c3:
            mlw_v = st.number_input("Max Landing Weight (MLW kg):", value=0, step=500)
            h4_v = st.number_input("Hold 4 Max Limit (kg):", value=0, step=100)
            
        limits_data = {
            "MTOW": mtow_v, "MZFW": mzfw_v, "MLW": mlw_v,
            "HOLD1_MAX": h1_v, "HOLD2_MAX": h2_v, "HOLD3_MAX": h3_v, "HOLD4_MAX": h4_v,
            "MAC_MIN": 8.0, "MAC_MAX": 33.0, "CAP_A": 60, "CAP_B": 60, "CAP_C": 69
        }

    if st.button("Save Aircraft to Database"):
        if new_reg:
            st.session_state.fleet_db[new_reg] = {
                "registration": new_reg,
                "airline": new_operator if new_operator else "Independent Operator",
                "type": new_type,
                "status": "Restricted (MEL/Derated)" if is_restr else "Operational",
                "dow": new_dow,
                "doi": new_doi,
                "is_restricted": is_restr,
                "restriction_reason": restr_reason,
                "limits": limits_data
            }
            st.success(f"Aircraft {new_reg} successfully registered!")
            st.session_state.current_page = "Home"
            st.rerun()
        else:
            st.error("Please enter a valid Tail Registration.")


# ==============================================================================
# 3. PAGE: EDIT EXISTING AIRCRAFT
# ==============================================================================
elif st.session_state.current_page == "Edit_Aircraft":
    st.title("Edit Existing Aircraft Profile")
    st.caption("Update weights and operational limitations in case of maintenance or technical restrictions.")
    
    available_tails = list(st.session_state.fleet_db.keys())
    
    if available_tails:
        target_tail = st.selectbox("Select Aircraft to Edit:", available_tails)
        ac_target = st.session_state.fleet_db[target_tail]
        
        e_dow = st.number_input("Updated DOW (kg):", value=float(ac_target["dow"]), step=100.0)
        e_doi = st.number_input("Updated DOI:", value=float(ac_target["doi"]), step=0.1)
        
        e_restricted = st.checkbox("Apply Operational Restriction / Technical Defect", value=ac_target["is_restricted"])
        
        if e_restricted:
            e_reason = st.text_input("Restriction Reason:", value=ac_target.get("restriction_reason", ""))
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                e_mtow = st.number_input("MTOW Limit (kg):", value=int(ac_target["limits"]["MTOW"]), step=500)
            with ec2:
                e_mzfw = st.number_input("MZFW Limit (kg):", value=int(ac_target["limits"]["MZFW"]), step=500)
            with ec3:
                e_mlw = st.number_input("MLW Limit (kg):", value=int(ac_target["limits"]["MLW"]), step=500)
        else:
            e_reason = ""
            e_mtow, e_mzfw, e_mlw = 79015, 62731, 65317

        if st.button("Update Aircraft Profile"):
            st.session_state.fleet_db[target_tail]["dow"] = e_dow
            st.session_state.fleet_db[target_tail]["doi"] = e_doi
            st.session_state.fleet_db[target_tail]["is_restricted"] = e_restricted
            st.session_state.fleet_db[target_tail]["status"] = "Restricted (MEL/Derated)" if e_restricted else "Operational"
            st.session_state.fleet_db[target_tail]["restriction_reason"] = e_reason
            st.session_state.fleet_db[target_tail]["limits"]["MTOW"] = e_mtow
            st.session_state.fleet_db[target_tail]["limits"]["MZFW"] = e_mzfw
            st.session_state.fleet_db[target_tail]["limits"]["MLW"] = e_mlw
            
            st.success(f"Aircraft {target_tail} successfully updated!")
            st.session_state.current_page = "Home"
            st.rerun()
    else:
        st.warning("No aircraft available in the fleet to edit. Please add an aircraft first.")


# ==============================================================================
# 4. PAGE: AIRSHEET W&B ENGINE (FULL DISPATCH WORKFLOW)
# ==============================================================================
elif st.session_state.current_page == "WNB_Engine":
    active_tail = st.session_state.selected_tail
    
    if not active_tail or active_tail not in st.session_state.fleet_db:
        st.warning("Please select an aircraft first from the Home page.")
        st.stop()

    ac_data = st.session_state.fleet_db[active_tail]
    LIMITS = ac_data["limits"]

    st.title(f"AirSheet Engine - [{active_tail}]")
    st.caption(f"Operator: {ac_data['airline']} | Type: {ac_data['type']} | Status: {ac_data['status']}")
    
    if ac_data["is_restricted"]:
        st.warning(f"⚠️ **Active Operational Limitations:** {ac_data.get('restriction_reason', 'MEL Derated')}")

    col_input, col_visual = st.columns([1, 1])

    with col_input:
        st.subheader("1. Flight & Load Inputs")
        
        st.info(f"**Aircraft Baseline Profile:**\n\n• Dry Operating Weight (DOW): **{ac_data['dow']:,} kg**\n\n• Dry Operating Index (DOI): **{ac_data['doi']}**")
        dow = float(ac_data["dow"])
        doi = float(ac_data["doi"])
        
        st.markdown("---")
        st.write("**Passenger Demographics (From Dispatch Message):**")
        
        c_pax1, c_pax2, c_pax3 = st.columns(3)
        with c_pax1:
            num_adults = st.number_input("Adults (84 kg):", min_value=0, max_value=200, value=0, step=1)
        with c_pax2:
            num_children = st.number_input("Children (35 kg):", min_value=0, max_value=60, value=0, step=1)
        with c_pax3:
            num_infants = st.number_input("Infants (10 kg):", min_value=0, max_value=30, value=0, step=1)
            
        total_pax_seats = num_adults + num_children

        # Defaults for cabin zones based on capacities
        cap_a = LIMITS["CAP_A"]
        cap_b = LIMITS["CAP_B"]
        cap_c = LIMITS["CAP_C"]
        tot_cap = cap_a + cap_b + cap_c if (cap_a + cap_b + cap_c) > 0 else 189

        default_a = min(cap_a, int(total_pax_seats * (cap_a / tot_cap)))
        default_b = min(cap_b, int(total_pax_seats * (cap_b / tot_cap)))
        default_c = max(0, total_pax_seats - (default_a + default_b))

        st.markdown("---")
        st.write("**Cabin Zone Passenger Distribution (Editable):**")
        zc1, zc2, zc3 = st.columns(3)
        with zc1:
            pax_a = st.number_input("Zone A Pax:", min_value=0, max_value=cap_a, value=default_a, step=1)
        with zc2:
            pax_b = st.number_input("Zone B Pax:", min_value=0, max_value=cap_b, value=default_b, step=1)
        with zc3:
            pax_c = st.number_input("Zone C Pax:", min_value=0, max_value=cap_c, value=default_c, step=1)

        st.markdown("---")
        st.write("**Cargo Holds Loading (kg) - Fully Editable:**")
        hc1, hc2 = st.columns(2)
        with hc1:
            c1 = st.number_input("Hold 1 (FWD Upper):", min_value=0, max_value=int(LIMITS["HOLD1_MAX"]), value=0, step=50)
            c2 = st.number_input("Hold 2 (FWD Lower):", min_value=0, max_value=int(LIMITS["HOLD2_MAX"]), value=0, step=50)
        with hc2:
            c3 = st.number_input("Hold 3 (AFT Lower):", min_value=0, max_value=int(LIMITS["HOLD3_MAX"]), value=0, step=50)
            c4 = st.number_input("Hold 4 (AFT Upper):", min_value=0, max_value=int(LIMITS["HOLD4_MAX"]), value=0, step=50)
        
        st.markdown("---")
        st.write("**Fuel Management (kg):**")
        to_fuel = st.number_input("Takeoff Fuel (TBOF):", value=0.0, step=100.0)
        trip_fuel = st.number_input("Trip Fuel:", value=0.0, step=100.0)

    # --- CALCULATIONS ENGINE ---
    total_pax_wt = (num_adults * PAX_WEIGHTS["ADULT"]) + (num_children * PAX_WEIGHTS["CHILD"]) + (num_infants * PAX_WEIGHTS["INFANT"])
    total_cargo_wt = c1 + c2 + c3 + c4

    zfw = dow + total_pax_wt + total_cargo_wt
    tow = zfw + to_fuel
    lw = tow - trip_fuel

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

    cg_meters = total_takeoff_moment / tow if tow > 0 else 0
    mac_percent = ((cg_meters - LEMAC) / MAC_LENGTH) * 100.0 if tow > 0 else 0.0

    with col_visual:
        display_mode = st.radio(
            "Display Mode:",
            ["Standard Dashboard", "3D Hull View"],
            horizontal=True
        )
        
        st.subheader("2. Graphical Load Distribution")
        
        is_zfw_safe = zfw <= LIMITS["MZFW"]
        is_tow_safe = tow <= LIMITS["MTOW"]
        is_lw_safe = lw <= LIMITS["MLW"]
        is_mac_safe = LIMITS["MAC_MIN"] <= mac_percent <= LIMITS["MAC_MAX"]
        
        st.info(f"Total Pax: {total_pax_seats} (Adults: {num_adults} / Children: {num_children} / Infants: {num_infants}) | Total Cargo: {total_cargo_wt:,} kg")
        
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.caption(f"**ZFW (Max: {LIMITS['MZFW']:,} kg)**")
            st.metric(label="Zero Fuel Wt", value=f"{zfw:,} kg", delta="SAFE" if is_zfw_safe else f"EXCEEDED", delta_color="normal" if is_zfw_safe else "inverse")
            
        with m2:
            st.caption(f"**TOW (Max: {LIMITS['MTOW']:,} kg)**")
            st.metric(label="Takeoff Wt", value=f"{tow:,} kg", delta="SAFE" if is_tow_safe else f"EXCEEDED", delta_color="normal" if is_tow_safe else "inverse")
            
        with m3:
            st.caption(f"**LW (Max: {LIMITS['MLW']:,} kg)**")
            st.metric(label="Landing Wt", value=f"{lw:,} kg", delta="SAFE" if is_lw_safe else f"EXCEEDED", delta_color="normal" if is_lw_safe else "inverse")
        
        # --- CENTER OF GRAVITY PLACED DIRECTLY BETWEEN WEIGHTS AND 3D/VISUALS ---
        st.markdown("---")
        st.write("**Takeoff Center of Gravity (%MAC):**")
        st.title(f"{mac_percent:.2f}%")
        
        if is_mac_safe:
            st.markdown('<div class="badge-safe">SAFE (In Envelope)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-danger">OUT OF ENVELOPE</div>', unsafe_allow_html=True)
        st.markdown("---")

        if display_mode == "3D Hull View":
            st.markdown(f"### 3D Aircraft Hull & Internal Compartments [{active_tail}]")
            
            u = np.linspace(0, 2 * np.pi, 24)
            y_fuselage = np.linspace(0, 39.5, 35)
            u_grid, y_grid = np.meshgrid(u, y_fuselage)
            
            r_profile = np.piecewise(y_fuselage, 
                [y_fuselage < 4.5, (y_fuselage >= 4.5) & (y_fuselage <= 32.5), y_fuselage > 32.5],
                [lambda y: 1.88 * np.sin((y / 4.5) * (np.pi / 2)),
                 1.88,
                 lambda y: 1.88 * np.cos(((y - 32.5) / 7.0) * (np.pi / 2))]
            )
            
            r_grid, _ = np.meshgrid(r_profile, u)
            r_grid = r_grid.T
            
            x_hull = r_grid * np.cos(u_grid)
            z_hull = r_grid * np.sin(u_grid)
            
            fig_3d = go.Figure()
            
            fig_3d.add_trace(go.Surface(
                x=x_hull, y=y_grid, z=z_hull,
                opacity=0.15,
                colorscale=[[0, "#29b6f6"], [1, "#0288d1"]],
                showscale=False,
                name="Outer Hull"
            ))
            
            fig_3d.add_trace(go.Scatter3d(
                x=[0, -16.0, -16.0, -16.0, 0, 16.0, 16.0, 16.0, 0],
                y=[15.0, 21.0, 22.5, 22.5, 19.5, 22.5, 22.5, 21.0, 15.0],
                z=[-0.2, 0.5, 0.5, 2.2, -0.2, 2.2, 0.5, 0.5, -0.2],
                mode="lines",
                line=dict(color="#4fc3f7", width=5),
                name="Wings & Winglets"
            ))

            fig_3d.add_trace(go.Scatter3d(
                x=[0, 0, 0, 0],
                y=[32.0, 37.0, 38.5, 35.0],
                z=[1.8, 5.5, 5.5, 1.8],
                mode="lines",
                line=dict(color="#0288d1", width=5),
                name="Tail Fin"
            ))
            
            fuel_color = "#00e676" if (to_fuel <= 20800 and is_tow_safe) else "#ff1744"
            h1_color = "#00e676" if c1 <= LIMITS["HOLD1_MAX"] else "#ff1744"
            h2_color = "#00e676" if c2 <= LIMITS["HOLD2_MAX"] else "#ff1744"
            h3_color = "#00e676" if c3 <= LIMITS["HOLD3_MAX"] else "#ff1744"
            h4_color = "#00e676" if c4 <= LIMITS["HOLD4_MAX"] else "#ff1744"

            fig_3d.add_trace(go.Mesh3d(
                x=[0, -14.0, -14.0, 0, 14.0, 14.0],
                y=[16.0, 19.5, 21.0, 19.5, 21.0, 19.5],
                z=[-0.2, -0.2, -0.2, -0.2, -0.2, -0.2],
                color=fuel_color,
                opacity=0.85,
                name=f"Fuel Tank ({to_fuel:,} kg)"
            ))
            
            fig_3d.add_trace(go.Mesh3d(
                x=[-1, -1, 1, 1, -1, -1, 1, 1],
                y=[7.5, 10.0, 10.0, 7.5, 7.5, 10.0, 10.0, 7.5],
                z=[-1.4, -1.4, -1.4, -1.4, -0.4, -0.4, -0.4, -0.4],
                color=h1_color, opacity=0.75, name=f"Hold 1: {c1}kg"
            ))
            fig_3d.add_trace(go.Mesh3d(
                x=[-1, -1, 1, 1, -1, -1, 1, 1],
                y=[10.2, 12.8, 12.8, 10.2, 10.2, 12.8, 12.8, 10.2],
                z=[-1.4, -1.4, -1.4, -1.4, -0.4, -0.4, -0.4, -0.4],
                color=h2_color, opacity=0.75, name=f"Hold 2: {c2}kg"
            ))
            fig_3d.add_trace(go.Mesh3d(
                x=[-1, -1, 1, 1, -1, -1, 1, 1],
                y=[18.5, 21.8, 21.8, 18.5, 18.5, 21.8, 21.8, 18.5],
                z=[-1.4, -1.4, -1.4, -1.4, -0.4, -0.4, -0.4, -0.4],
                color=h3_color, opacity=0.75, name=f"Hold 3: {c3}kg"
            ))
            fig_3d.add_trace(go.Mesh3d(
                x=[-1, -1, 1, 1, -1, -1, 1, 1],
                y=[22.0, 24.5, 24.5, 22.0, 22.0, 24.5, 24.5, 22.0],
                z=[-1.4, -1.4, -1.4, -1.4, -0.4, -0.4, -0.4, -0.4],
                color=h4_color, opacity=0.75, name=f"Hold 4: {c4}kg"
            ))

            cg_color = "#00e676" if is_mac_safe else "#ff1744"
            fig_3d.add_trace(go.Scatter3d(
                x=[0.0],
                y=[cg_meters],
                z=[0.0],
                mode="markers+text",
                marker=dict(size=13, color=cg_color, symbol="diamond"),
                text=[f"CG: {mac_percent:.2f}% MAC"],
                textposition="top center",
                name="Center of Gravity"
            ))

            fig_3d.update_layout(
                scene=dict(
                    xaxis=dict(range=[-20, 20], visible=False, showgrid=False),
                    yaxis=dict(title="Longitudinal Distance (m)", range=[0, 42], backgroundcolor="#0f172a", showgrid=False),
                    zaxis=dict(range=[-10, 10], visible=False, showgrid=False),
                    aspectmode="manual",
                    aspectratio=dict(x=1.0, y=2.2, z=0.6),
                    camera=dict(eye=dict(x=1.6, y=1.3, z=0.9))
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=380,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False
            )

            st.plotly_chart(fig_3d, use_container_width=True, key="sudan_fleet_3d_v_full")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Cabin Seating & Hold Status:")
        
        st.progress(pax_a / LIMITS["CAP_A"] if LIMITS["CAP_A"] > 0 else 0, text=f"Zone A: {pax_a} Pax")
        st.markdown(f'<div class="pax-breakdown"><b>{a_adult} Adult / {a_child} Child / {a_infant} Infant</b></div>', unsafe_allow_html=True)
        
        st.progress(pax_b / LIMITS["CAP_B"] if LIMITS["CAP_B"] > 0 else 0, text=f"Zone B: {pax_b} Pax")
        st.markdown(f'<div class="pax-breakdown"><b>{b_adult} Adult / {b_child} Child / {b_infant} Infant</b></div>', unsafe_allow_html=True)
        
        st.progress(pax_c / LIMITS["CAP_C"] if LIMITS["CAP_C"] > 0 else 0, text=f"Zone C: {pax_c} Pax")
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
                cap_a_rem = LIMITS["CAP_A"] - pax_a
                cap_b_rem = LIMITS["CAP_B"] - pax_b
                cap_c_rem = LIMITS["CAP_C"] - pax_c
                
                alloc_a, alloc_b, alloc_c = 0, 0, 0
                
                for _ in range(rem_pax):
                    if cap_a_rem >= cap_c_rem and cap_a_rem > 0:
                        alloc_a += 1
                        cap_a_rem -= 1
                    elif cap_c_rem > cap_a_rem and cap_c_rem > 0:
                        alloc_c += 1
                        cap_c_rem -= 1
                    elif cap_b_rem > 0:
                        alloc_b += 1
                        cap_b_rem -= 1
                    else:
                        alloc_a += 1
                        
                if alloc_a > 0: pax_suggestions.append(f"• Add {alloc_a} Pax in Zone A")
                if alloc_b > 0: pax_suggestions.append(f"• Add {alloc_b} Pax in Zone B")
                if alloc_c > 0: pax_suggestions.append(f"• Add {alloc_c} Pax in Zone C")
            elif lmc_pax < 0:
                pax_suggestions.append(f"• Offload {abs(lmc_pax)} Pax from congested area")

            cargo_suggestions = []
            if lmc_cargo > 0:
                if lmc_cargo <= 50:
                    cargo_suggestions.append(f"• Load {lmc_cargo} kg into Hold 4 (AFT Bulk)")
                else:
                    fwd_part = round(lmc_cargo * 0.4)
                    aft_part = lmc_cargo - fwd_part
                    cargo_suggestions.append(f"• Load {fwd_part} kg into Hold 2 (FWD)")
                    cargo_suggestions.append(f"• Load {aft_part} kg into Hold 3 (AFT)")
            elif lmc_cargo < 0:
                cargo_suggestions.append(f"• Offload {abs(lmc_cargo)} kg from Hold 3 or Hold 2")

            st.success("\n".join(pax_suggestions + cargo_suggestions))
