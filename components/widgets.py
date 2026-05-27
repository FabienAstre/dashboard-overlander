import streamlit as st

def section_title(text):
    st.markdown(f'<div class="os-section-title">{text}</div>', unsafe_allow_html=True)

def metric_tile(value, label, sub="", color="var(--accent-cyan)"):
    st.markdown(f"""
    <div class="os-metric">
      <div class="os-metric-value" style="color:{color};">{value}</div>
      <div class="os-metric-label">{label}</div>
      {'<div class="os-metric-sub">'+sub+'</div>' if sub else ''}
    </div>""", unsafe_allow_html=True)

def alert_row(icon, text, level="info"):
    st.markdown(f'<div class="os-alert os-alert-{level}"><span>{icon}</span><span>{text}</span></div>',
                unsafe_allow_html=True)

def safety_score_widget(score):
    color = "var(--accent-green)" if score>=80 else ("var(--accent-amber)" if score>=60 else "var(--accent-red)")
    label = "GOOD" if score>=80 else ("MODERATE" if score>=60 else "HIGH RISK")
    c = 2*3.14159*36
    dash = (score/100)*c
    st.markdown(f"""
    <div style="text-align:center;padding:0.5rem 0;">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="36" fill="none" stroke="var(--bg-card-alt)" stroke-width="8"/>
        <circle cx="50" cy="50" r="36" fill="none" stroke="{color}" stroke-width="8"
                stroke-dasharray="{dash:.1f} {c-dash:.1f}"
                stroke-dashoffset="{c/4:.1f}" stroke-linecap="round"/>
        <text x="50" y="45" text-anchor="middle" font-family="Rajdhani" font-size="18"
              font-weight="700" fill="{color}">{score}</text>
        <text x="50" y="60" text-anchor="middle" font-family="Share Tech Mono"
              font-size="7" fill="var(--text-muted)">SAFETY</text>
      </svg>
      <div style="font-family:'Rajdhani';font-size:0.75rem;letter-spacing:0.1em;color:{color};margin-top:-0.3rem;">{label}</div>
    </div>""", unsafe_allow_html=True)

def route_score_bar(label, value, color="var(--accent-cyan)"):
    st.markdown(f"""
    <div style="margin-bottom:0.6rem;">
      <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-secondary);margin-bottom:0.2rem;">
        <span>{label}</span><span style="color:{color};">{value}/100</span>
      </div>
      <div class="fuel-bar-track">
        <div style="height:100%;width:{value}%;border-radius:4px;background:{color};"></div>
      </div>
    </div>""", unsafe_allow_html=True)

def waypoint_list(waypoints, origin, destination):
    st.markdown(f"""
    <div class="os-waypoint"><span class="os-waypoint-dot"></span>
      <span style="color:var(--text-primary);font-size:0.83rem;">{origin}</span>
      <span class="os-badge os-badge-cyan" style="margin-left:auto;">START</span>
    </div>""", unsafe_allow_html=True)
    for wp in waypoints:
        st.markdown(f'<div class="os-waypoint"><span class="os-waypoint-dot mid"></span><span style="font-size:0.8rem;">{wp}</span></div>',
                    unsafe_allow_html=True)
    st.markdown(f"""
    <div class="os-waypoint" style="border-bottom:none;"><span class="os-waypoint-dot end"></span>
      <span style="color:var(--text-primary);font-size:0.83rem;">{destination}</span>
      <span class="os-badge os-badge-green" style="margin-left:auto;">END</span>
    </div>""", unsafe_allow_html=True)

def fuel_stop_card(stop, idx):
    s = st.session_state
    tank_range = int(s.tank_capacity_l / s.consumption_l100 * 100)
    prev_km = st.session_state.fuel_stops[idx-1]["dist_km"] if idx > 0 else 0
    gap = stop["dist_km"] - prev_km
    status = "⚠️ Critical gap" if gap > tank_range*0.85 else "✅ In range"
    price_str = f"${stop['price']:.2f}/L" if stop['price'] < 5 else f"${stop['price']:.1f} MXN/L"
    st.markdown(f"""
    <div class="os-card" style="padding:0.7rem 1rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-family:'Rajdhani',sans-serif;font-size:0.95rem;font-weight:700;color:var(--text-primary);">⛽ {stop['name']}</div>
          <div style="font-size:0.72rem;color:var(--text-muted);">km {stop['dist_km']:,} · {price_str}</div>
        </div>
        <div style="font-size:0.72rem;color:var(--text-secondary);">{status}</div>
      </div>
    </div>""", unsafe_allow_html=True)

def campsite_card(camp):
    score = camp["score"]
    color = "var(--accent-green)" if score>=90 else ("var(--accent-amber)" if score>=80 else "var(--text-muted)")
    badges = {"Free/BLM":("os-badge-green","FREE"),"Beach Camp":("os-badge-cyan","BEACH"),
              "Provincial":("os-badge-amber","PROV"),"National F":("os-badge-amber","NAT F"),
              "State Park":("os-badge-amber","STATE"),"Palapa Camp":("os-badge-cyan","PALAPA"),
              "Remote Bay":("os-badge-cyan","REMOTE")}
    bc, bl = badges.get(camp["type"], ("","?"))
    st.markdown(f"""
    <div class="os-card" style="padding:0.65rem 1rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-family:'Rajdhani',sans-serif;font-size:0.92rem;font-weight:700;color:var(--text-primary);">🏕 {camp['name']}</div>
          <div style="font-size:0.7rem;color:var(--text-muted);">{camp['lat']:.2f}°N, {abs(camp['lon']):.2f}°W</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.2rem;">
          <span class="os-badge {bc}">{bl}</span>
          <span style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;color:{color};">{score}</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
