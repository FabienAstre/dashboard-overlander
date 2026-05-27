import streamlit as st
from datetime import datetime
from components.widgets import section_title, metric_tile, alert_row

MAINT_ITEMS = [
    {"system":"Engine Oil",        "interval_km":8000,  "last_km":210000,"critical":True},
    {"system":"Oil Filter",         "interval_km":8000,  "last_km":210000,"critical":True},
    {"system":"Fuel Filter",        "interval_km":20000, "last_km":198000,"critical":True},
    {"system":"Air Filter",         "interval_km":30000, "last_km":195000,"critical":False},
    {"system":"Glow Plugs",         "interval_km":60000, "last_km":160000,"critical":True},
    {"system":"Serpentine Belt",    "interval_km":80000, "last_km":140000,"critical":True},
    {"system":"Coolant Flush",      "interval_km":50000, "last_km":175000,"critical":False},
    {"system":"Transmission Fluid", "interval_km":60000, "last_km":165000,"critical":False},
    {"system":"Brake Fluid",        "interval_km":40000, "last_km":195000,"critical":True},
    {"system":"Brake Pads (F)",     "interval_km":40000, "last_km":200000,"critical":True},
    {"system":"Tires — Rotation",   "interval_km":10000, "last_km":210000,"critical":False},
    {"system":"Wheel Bearings",     "interval_km":80000, "last_km":160000,"critical":True},
]

def render_vehicle():
    s = st.session_state
    st.markdown(f"### 🚗 Vehicle Panel")
    st.markdown(f'<p style="color:var(--text-secondary);margin-top:-0.5rem;margin-bottom:1rem;">{s.vehicle_name}</p>', unsafe_allow_html=True)

    with st.expander("⚙️ Vehicle Settings"):
        c1,c2,c3 = st.columns(3)
        with c1: s.vehicle_name   = st.text_input("Name",s.vehicle_name,key="vn")
        with c2: s.odometer_km    = st.number_input("Odometer (km)",0,999999,s.odometer_km,key="vo")
        with c3: s.tank_capacity_l= st.number_input("Tank (L)",50,400,s.tank_capacity_l,key="vt")

    overdue  = sum(1 for i in MAINT_ITEMS if s.odometer_km>=i["last_km"]+i["interval_km"])
    due_soon = sum(1 for i in MAINT_ITEMS if 0<(i["last_km"]+i["interval_km"]-s.odometer_km)<=1500)
    readiness= max(0,100-overdue*12-due_soon*4)

    m1,m2,m3,m4,m5 = st.columns(5)
    with m1: metric_tile(f"{s.odometer_km:,}","ODOMETER","km")
    with m2: metric_tile(str(overdue),"OVERDUE","critical items","var(--accent-red)" if overdue>0 else "var(--accent-green)")
    with m3: metric_tile(str(due_soon),"DUE SOON","within 1,500 km","var(--accent-amber)" if due_soon>0 else "var(--accent-cyan)")
    with m4: metric_tile(f"{readiness}%","READINESS","expedition score","var(--accent-green)" if readiness>=80 else "var(--accent-amber)")
    with m5:
        nxt=max(0,s.last_service_km+s.service_interval_km-s.odometer_km)
        metric_tile(f"{nxt:,}","NEXT SVC","km until service","var(--accent-red)" if nxt<500 else "var(--accent-cyan)")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    left,right = st.columns([2,1],gap="medium")

    with left:
        section_title("🔧 Maintenance Schedule")
        st.markdown('<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:0.5rem;padding:0.4rem 0;border-bottom:2px solid var(--border);font-size:0.68rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em;"><span>System</span><span>Last km</span><span>Interval</span><span>Next Due</span><span>Status</span></div>',
                    unsafe_allow_html=True)
        for item in MAINT_ITEMS:
            next_due  = item["last_km"]+item["interval_km"]
            remaining = next_due-s.odometer_km
            if remaining<=0:    status,color="🔴 OVERDUE","var(--accent-red)"
            elif remaining<=1500:status,color="🟡 DUE SOON","var(--accent-amber)"
            else:               status,color="✅ OK","var(--accent-green)"
            crit = "★ " if item["critical"] else ""
            st.markdown(f'<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:0.5rem;padding:0.45rem 0;border-bottom:1px solid var(--border);font-size:0.78rem;align-items:center;"><span style="color:var(--text-primary);">{crit}{item["system"]}</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:var(--text-muted);">{item["last_km"]:,}</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:var(--text-muted);">{item["interval_km"]:,}</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:var(--text-muted);">{next_due:,}</span><span style="color:{color};font-size:0.72rem;">{status}</span></div>',
                        unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section_title("📝 Service Notes")
        with st.form("maint_form"):
            note = st.text_area("Note",placeholder="e.g. Changed oil at 214,380 km — Rotella T6 5W-40",
                                 label_visibility="collapsed",key="note_inp")
            if st.form_submit_button("➕ Log Note") and note.strip():
                s.maint_notes.append({"ts":datetime.now().strftime("%Y-%m-%d %H:%M"),"note":note.strip()})
                st.rerun()
        for n in reversed(s.maint_notes[-8:]):
            st.markdown(f'<div style="display:flex;gap:0.6rem;padding:0.4rem 0;border-bottom:1px solid var(--border);font-size:0.78rem;"><span style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:var(--text-muted);">{n["ts"]}</span><span style="color:var(--text-primary);">{n["note"]}</span></div>',
                        unsafe_allow_html=True)

    with right:
        section_title("🛡 Readiness Score")
        bar_color="var(--accent-green)" if readiness>=80 else ("var(--accent-amber)" if readiness>=60 else "var(--accent-red)")
        st.markdown(f'<div style="text-align:center;padding:1rem 0;"><svg width="110" height="110" viewBox="0 0 110 110"><circle cx="55" cy="55" r="44" fill="none" stroke="var(--bg-card-alt)" stroke-width="10"/><circle cx="55" cy="55" r="44" fill="none" stroke="{bar_color}" stroke-width="10" stroke-dasharray="{readiness*2.764:.1f} {(100-readiness)*2.764:.1f}" stroke-dashoffset="69.1" stroke-linecap="round"/><text x="55" y="50" text-anchor="middle" font-family="Rajdhani" font-size="22" font-weight="700" fill="{bar_color}">{readiness}%</text><text x="55" y="66" text-anchor="middle" font-family="Share Tech Mono" font-size="7" fill="var(--text-muted)">READINESS</text></svg></div>',
                    unsafe_allow_html=True)

        if overdue>0: alert_row("🚨",f"{overdue} items overdue — fix before departing.","danger")
        if due_soon>0: alert_row("⚠️",f"{due_soon} items due within 1,500 km.","warn")
        if overdue==0 and due_soon==0: alert_row("✅","All systems within service intervals.","ok")

        section_title("🏕 Pre-Departure Checklist")
        for check in ["Oil & filter changed","Fuel filter checked","Battery >12.5V","Tires pressured cold",
                       "Spare tire present","Coolant level OK","Fire extinguisher","Offline maps downloaded",
                       "Sat communicator charged","Water — 20L minimum"]:
            st.checkbox(check, key=f"chk_{check}")
