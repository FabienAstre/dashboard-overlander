import streamlit as st

NAV_ITEMS = [
    "🗺️ Mission Control",
    "📍 Route Planner",
    "🌍 Map Intelligence",
    "⛽ Fuel Planner",
    "🏕️ Camp Intel",
    "🔭 Discoveries",
    "🚗 Vehicle Panel",
    "🛂 Border Alerts",
    "🤖 AI Assistant",
]

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("""
        <div style="padding:0.5rem 0 1rem;border-bottom:1px solid var(--border);margin-bottom:1rem;">
          <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;color:var(--accent-cyan);letter-spacing:0.12em;">⬡ OVERLANDER OS</div>
          <div style="font-size:0.7rem;color:var(--text-muted);letter-spacing:0.08em;">EXPEDITION OPERATING SYSTEM</div>
        </div>
        """, unsafe_allow_html=True)

        s = st.session_state
        st.markdown(f"""
        <div class="os-card" style="margin-bottom:1rem;">
          <div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.1em;">Active Mission</div>
          <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;color:var(--text-primary);">{s.trip_name}</div>
          <div style="font-size:0.72rem;color:var(--text-secondary);margin-top:0.2rem;">{s.origin.split(',')[0]} → {s.destination.split(',')[0]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="os-section-title">Navigation</div>', unsafe_allow_html=True)
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = NAV_ITEMS[0]

        for item in NAV_ITEMS:
            is_active = st.session_state["current_page"] == item
            if st.button(f"{'▶ ' if is_active else ''}{item}", key=f"nav_{item}", use_container_width=True):
                st.session_state["current_page"] = item
                st.rerun()

        st.markdown("---")
        st.markdown('<div class="os-section-title">Map Overlays</div>', unsafe_allow_html=True)
        st.session_state.show_fuel    = st.toggle("⛽ Fuel Stops",   value=st.session_state.show_fuel)
        st.session_state.show_camps   = st.toggle("🏕 Campsites",    value=st.session_state.show_camps)
        st.session_state.show_borders = st.toggle("🛂 Border Posts", value=st.session_state.show_borders)
        st.session_state.show_safety  = st.toggle("🛡 Safety Zones", value=st.session_state.show_safety)

        st.markdown("---")
        st.markdown('<div class="os-section-title">Quick AI Prompts</div>', unsafe_allow_html=True)
        for p in ["🛡 Safest route to destination", "🏖 Find ocean camping spots",
                  "⛽ Fuel before next mountain", "🌙 Night driving hazards", "🛂 Border crossing tips"]:
            if st.button(p, key=f"qp_{p}", use_container_width=True):
                st.session_state.ai_messages.append({"role": "user", "content": p})
                st.session_state["current_page"] = "🤖 AI Assistant"
                st.rerun()

        st.markdown("---")
        fl = st.session_state.fuel_level_pct
        color = "var(--accent-red)" if fl < 30 else ("var(--accent-amber)" if fl < 50 else "var(--accent-cyan)")
        st.markdown(f"""
        <div class="os-section-title">Fuel Status</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:{color};margin-bottom:0.3rem;">{fl}% — {int(st.session_state.tank_capacity_l * fl / 100)}L / {st.session_state.tank_capacity_l}L</div>
        <div class="fuel-bar-track"><div class="fuel-bar-fill {'low' if fl < 30 else ''}" style="width:{fl}%"></div></div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div style="font-size:0.65rem;color:var(--text-muted);text-align:center;">OVERLANDER OS v1.0</div>', unsafe_allow_html=True)

    return st.session_state["current_page"]
