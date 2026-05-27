import streamlit as st
from components.widgets import section_title, metric_tile, alert_row, fuel_stop_card

def render_fuel_planner():
    s = st.session_state
    st.markdown("### ⛽ Fuel Planner")
    left, right = st.columns([2,1], gap="medium")

    with left:
        section_title("Vehicle Fuel Parameters")
        c1,c2,c3 = st.columns(3)
        with c1: s.tank_capacity_l  = st.number_input("Tank (L)",    50,400,s.tank_capacity_l,5,  key="tc")
        with c2: s.consumption_l100 = st.number_input("L/100km",     5.0,40.0,s.consumption_l100,0.5,key="cl")
        with c3: s.fuel_level_pct   = st.slider("Fuel %", 0,100,s.fuel_level_pct, key="fp")

        tank_range    = int(s.tank_capacity_l/s.consumption_l100*100)
        current_range = int(s.tank_capacity_l*s.fuel_level_pct/100/s.consumption_l100*100)
        total_fuel_l  = int(3850/100*s.consumption_l100)
        est_cost      = round(total_fuel_l*1.55,0)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        m1,m2,m3,m4 = st.columns(4)
        with m1: metric_tile(str(tank_range),"MAX RANGE",f"{s.tank_capacity_l}L full")
        with m2: metric_tile(str(current_range),"CURRENT RANGE",f"{s.fuel_level_pct}% fuel",
                              "var(--accent-red)" if current_range<300 else "var(--accent-cyan)")
        with m3: metric_tile(f"{total_fuel_l}L","TRIP TOTAL","3,850 km route")
        with m4: metric_tile(f"${est_cost:,.0f}","EST. COST","CAD approx")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section_title("⛽ Fuel Stop Sequence")
        prev_km = 0
        for i,fs in enumerate(s.fuel_stops):
            seg_km = fs["dist_km"] - prev_km
            gap_pct = seg_km/tank_range*100
            if gap_pct>90:   alert_row("🚨",f"Critical gap before {fs['name']}: {seg_km} km ({gap_pct:.0f}%)","danger")
            elif gap_pct>70: alert_row("⚠️",f"Long gap before {fs['name']}: {seg_km} km ({gap_pct:.0f}%)","warn")
            fuel_stop_card(fs,i)
            prev_km = fs["dist_km"]

    with right:
        section_title("🧮 Aux Tank Calculator")
        extra = st.number_input("Aux tank (L)",0,200,0,10,key="aux")
        ext_range = int((s.tank_capacity_l+extra)/s.consumption_l100*100)
        st.markdown(f'<div class="os-card"><div style="font-size:0.75rem;color:var(--text-muted);">Extended range</div><div style="font-family:\'Rajdhani\',sans-serif;font-size:1.5rem;font-weight:700;color:var(--accent-cyan);">{ext_range} km</div><div style="font-size:0.72rem;color:var(--text-muted);">{s.tank_capacity_l+extra}L total</div></div>',
                    unsafe_allow_html=True)

        section_title("💰 Price by Region")
        for region,cur,price in [("BC, Canada","CAD",1.82),("Washington","USD",1.19),
                                   ("Oregon","USD",1.29),("California","USD",1.45),
                                   ("Baja Norte","MXN",23.8),("Baja Sur","MXN",22.9)]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:0.35rem 0;border-bottom:1px solid var(--border);font-size:0.78rem;"><span style="color:var(--text-secondary);">{region}</span><span style="font-family:\'Share Tech Mono\',monospace;color:var(--accent-amber);">{cur} {price:.2f}/L</span></div>',
                        unsafe_allow_html=True)

        section_title("⚡ Fuel Alerts")
        tank_r = int((s.tank_capacity_l+extra)/s.consumption_l100*100)
        prev=0; max_gap=0; max_seg=""
        for fs in s.fuel_stops:
            g=fs["dist_km"]-prev
            if g>max_gap: max_gap=g; max_seg=fs["name"]
            prev=fs["dist_km"]
        if max_gap>tank_r*0.85: alert_row("🚨",f"Largest gap: {max_gap} km before {max_seg}. Carry jerrycans.","danger")
        else:                    alert_row("✅",f"Largest gap: {max_gap} km — within range.","ok")
        if extra==0: alert_row("⚠️","Consider 20–40L aux can for Baja remote sections.","warn")
        else:        alert_row("✅",f"{extra}L aux added — {ext_range} km range.","ok")
