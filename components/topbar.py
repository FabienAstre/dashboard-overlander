import streamlit as st

def render_topbar():
    s = st.session_state
    fuel_range_km = int(s.tank_capacity_l * (s.fuel_level_pct / 100) / s.consumption_l100 * 100)
    service_due_km = s.last_service_km + s.service_interval_km - s.odometer_km
    st.markdown(f"""
    <div class="os-topbar">
      <div class="os-topbar-title">⬡ OVERLANDER OS</div>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;">
        <span class="os-badge os-badge-green">🛰 {s.gps_fix}</span>
        <span class="os-badge">🌤 {s.weather_summary}</span>
        <span class="os-badge {'os-badge-green' if s.online else 'os-badge-red'}">{'🟢 ONLINE' if s.online else '🔴 OFFLINE'}</span>
        <span class="os-badge os-badge-cyan">⛽ {fuel_range_km} km range</span>
        <span class="os-badge {'os-badge-amber' if s.route_safety_score < 80 else 'os-badge-green'}">🛡 Safety {s.route_safety_score}/100</span>
        <span class="os-badge {'os-badge-red' if service_due_km < 500 else 'os-badge-amber'}">🔧 Service in {max(0,service_due_km):,} km</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
