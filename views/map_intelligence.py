import streamlit as st
from components.map_view import render_map, TILESETS
from components.widgets import section_title, alert_row

def render_map_intelligence():
    st.markdown("### 🌍 Map Intelligence")
    tc1,tc2,tc3,tc4,tc5 = st.columns(5)
    with tc1: st.session_state.show_fuel    = st.toggle("⛽ Fuel",    value=st.session_state.show_fuel,    key="mi_f")
    with tc2: st.session_state.show_camps   = st.toggle("🏕 Camps",   value=st.session_state.show_camps,   key="mi_c")
    with tc3: st.session_state.show_borders = st.toggle("🛂 Borders", value=st.session_state.show_borders, key="mi_b")
    with tc4: st.session_state.show_safety  = st.toggle("🛡 Safety",  value=st.session_state.show_safety,  key="mi_s")
    with tc5:
        ts = list(TILESETS.keys())
        sel = st.selectbox("Style", ts, index=ts.index(st.session_state.get("selected_tileset","CartoDB Dark Matter")),
                           key="mi_ts", label_visibility="collapsed")
        st.session_state.selected_tileset = sel

    render_map(height=560)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3, gap="small")

    with c1:
        section_title("🛡 Safety Zones")
        for level,loc,note in [("🔴 HIGH","Tijuana border zone","Theft, verify insurance"),
                                ("🟡 MEDIUM","Guerrero Negro stretch","No services 300 km"),
                                ("🔵 LOW","Portland corridor","Traffic congestion")]:
            st.markdown(f'<div class="os-card" style="padding:0.55rem 0.8rem;margin-bottom:0.4rem;"><div style="font-size:0.8rem;font-weight:600;color:var(--text-primary);">{level} · {loc}</div><div style="font-size:0.7rem;color:var(--text-muted);">{note}</div></div>',
                        unsafe_allow_html=True)

    with c2:
        section_title("⛽ Fuel Gap Analysis")
        tank_range = int(st.session_state.tank_capacity_l/st.session_state.consumption_l100*100)
        st.markdown(f'<div class="os-card"><div style="font-size:0.75rem;color:var(--text-muted);">Tank range at full</div><div style="font-family:\'Rajdhani\',sans-serif;font-size:1.3rem;font-weight:700;color:var(--accent-cyan);">{tank_range} km</div></div>',
                    unsafe_allow_html=True)
        for seg,km,ico in [("LA → Ensenada",210,"✅"),("Ensenada → G.Negro",490,"⚠️"),
                            ("G.Negro → Loreto",360,"✅"),("Loreto → La Paz",240,"✅"),("La Paz → Cabo",230,"✅")]:
            color = "var(--accent-red)" if km>tank_range*0.85 else "var(--text-secondary)"
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:0.35rem 0;border-bottom:1px solid var(--border);font-size:0.78rem;"><span>{ico} {seg}</span><span style="color:{color};">{km} km</span></div>',
                        unsafe_allow_html=True)

    with c3:
        section_title("🏕 Camp Density")
        for region,count,score in [("BC / Washington",3,85),("Oregon",2,88),
                                    ("California",4,82),("Baja Norte",3,87),("Baja Sur",4,93)]:
            st.markdown(f'<div style="margin-bottom:0.55rem;"><div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-secondary);"><span>{region} · {count} sites</span><span style="color:var(--accent-green);">{score}/100</span></div><div class="fuel-bar-track" style="margin-top:0.15rem;"><div style="height:100%;width:{int(score*0.9)}%;border-radius:4px;background:var(--accent-green);opacity:0.7;"></div></div></div>',
                        unsafe_allow_html=True)
