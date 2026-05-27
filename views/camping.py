import streamlit as st
from components.widgets import section_title, metric_tile, campsite_card, alert_row

CAMP_TYPES = ["All","Free/BLM","Beach Camp","Provincial","National F","State Park","Remote Bay","Palapa Camp"]

def render_camping():
    s = st.session_state
    st.markdown("### 🏕️ Camp Intel")
    fc1,fc2,fc3,fc4 = st.columns(4)
    with fc1: camp_type = st.selectbox("Type",CAMP_TYPES,key="ct")
    with fc2: min_score = st.slider("Min Score",0,100,75,key="ms")
    with fc3: truck_ok  = st.checkbox("Truck accessible",True,key="to")
    with fc4: free_only = st.checkbox("Free only",False,key="fo")

    camps = [c for c in s.campsites if (camp_type=="All" or c["type"]==camp_type) and c["score"]>=min_score]
    if free_only: camps=[c for c in camps if "Free" in c["type"] or "BLM" in c["type"]]

    mc1,mc2,mc3,mc4 = st.columns(4)
    with mc1: metric_tile(str(len(camps)),"SITES FOUND","After filters")
    with mc2: metric_tile(str(round(sum(c["score"] for c in camps)/max(len(camps),1))),"AVG SCORE","Quality")
    with mc3: metric_tile(str(sum(1 for c in camps if "Free" in c["type"] or "BLM" in c["type"])),"FREE SITES","No fee")
    with mc4: metric_tile(str(sum(1 for c in camps if "Beach" in c["type"])),"BEACH CAMPS","Coastal")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    c_list, c_detail = st.columns([2,1], gap="medium")

    with c_list:
        section_title(f"📋 Campsites ({len(camps)} results)")
        if not camps: st.info("No campsites match filters.")
        for c in sorted(camps,key=lambda x:x["score"],reverse=True):
            campsite_card(c)

    with c_detail:
        section_title("🗺️ Featured Camp")
        if camps:
            top=max(camps,key=lambda x:x["score"])
            st.markdown(f'<div class="os-card os-card-green" style="padding:1rem;"><div style="font-family:\'Rajdhani\',sans-serif;font-size:1.15rem;font-weight:700;color:var(--text-primary);">{top["name"]}</div><div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:0.5rem;">{top["type"]} · Score {top["score"]}/100</div><div style="font-size:0.8rem;color:var(--text-secondary);">📍 {top["lat"]:.3f}°N, {abs(top["lon"]):.3f}°W</div></div>',
                        unsafe_allow_html=True)
        section_title("💡 Camping Tips")
        for icon,tip in [("🌊","Bahía Concepción is the crown jewel of Baja camping."),
                          ("🏜","Mojave BLM: free, 14-day limit, no facilities."),
                          ("🌲","National Forest dispersed: 200ft from water/roads."),
                          ("🔒","Mexico: camp inside properties or established sites after dark."),
                          ("💧","Carry 10L+ emergency water for remote Baja.")]:
            alert_row(icon,tip,"info")

        section_title("📅 Suggested Schedule")
        for night,site,score in [("Night 1","Manning Park, BC",88),("Night 2","Colville NF, WA",79),
                                   ("Night 3","Mt Hood NF, OR",91),("Night 4","Shasta NF, CA",85),
                                   ("Night 5","Mojave Dispersed, CA",77),("Night 6","El Rosario, Baja",83)]:
            color="var(--accent-green)" if score>=88 else "var(--accent-amber)"
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;border-bottom:1px solid var(--border);font-size:0.78rem;"><div><div style="color:var(--text-muted);font-size:0.68rem;">{night}</div><div style="color:var(--text-primary);">{site}</div></div><span style="font-family:\'Rajdhani\',sans-serif;font-size:1.1rem;font-weight:700;color:{color};">{score}</span></div>',
                        unsafe_allow_html=True)
