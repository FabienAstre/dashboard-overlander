import streamlit as st
from components.widgets import section_title, alert_row, metric_tile

CROSSINGS = {
    "Osoyoos / Oroville (CAN to USA)": {
        "docs": [
            "Passport (mandatory)",
            "NEXUS card (optional, expedited)",
        ],
        "vehicle": [
            "Vehicle registration",
            "Proof of US insurance",
        ],
        "tips": [
            "NEXUS lane saves 20 to 40 min.",
            "Declare all firearms, food, plants.",
            "Open 24h — no overnight wait.",
        ],
        "visa": "Canadian citizens: no visa required for US entry.",
        "customs": "Declare food, weapons, cash over $10,000 USD.",
        "wait": 15,
        "status": "Normal",
        "hours": "24h",
    },
    "Otay Mesa / Tijuana (USA to MEX)": {
        "docs": [
            "Passport (mandatory)",
            "FMM Tourist Card (beyond free zone)",
            "Mexican auto insurance — MANDATORY",
        ],
        "vehicle": [
            "TIP — Temporary Import Permit (for mainland Mexico)",
            "Vehicle title or notarized letter",
            "US registration",
        ],
        "tips": [
            "Get Mexican insurance BEFORE crossing — Baja Bound etc.",
            "TIP at Banjercito office AT the border for mainland.",
            "Free zone is about 25km south — no TIP for Ensenada only.",
            "Avoid Tijuana crossing 19:00 to 22:00 — maximum wait.",
            "Otay Mesa less congested than San Ysidro for trucks.",
        ],
        "visa": "FMM tourist card at border, about $25 USD, free under 7 days in free zone.",
        "customs": "No firearms, fresh produce, or pork into Mexico. Cash limit $10,000 USD.",
        "wait": 55,
        "status": "Moderate wait",
        "hours": "06:00 to 22:00",
    },
}


def render_border_alerts():
    st.markdown("### Border Alerts")

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        metric_tile("2", "CROSSINGS", "On your route")
    with mc2:
        metric_tile("1", "VISA REQ", "Mexican FMM card")
    with mc3:
        metric_tile("1", "TIP NEEDED", "For mainland MX")
    with mc4:
        metric_tile("~70 min", "TOTAL WAIT", "Estimated")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    for name, info in CROSSINGS.items():
        wait_badge = "os-badge-amber" if info["wait"] > 30 else "os-badge-green"
        st.markdown(
            '<div class="os-card os-card-violet">'
            '<div style="font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;'
            'color:var(--text-primary);">Border: ' + name + "</div>"
            '<div style="display:flex;gap:0.5rem;margin-top:0.3rem;flex-wrap:wrap;">'
            '<span class="os-badge">~' + str(info["wait"]) + " min</span>"
            '<span class="os-badge ' + wait_badge + '">' + info["status"] + "</span>"
            '<span class="os-badge">' + info["hours"] + "</span>"
            "</div></div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2, gap="medium")

        with c1:
            section_title("Documents Required")
            for d in info["docs"]:
                alert_row("📋", d, "info")

            section_title("Vehicle Documents")
            for v in info["vehicle"]:
                if "TIP" in v or "insurance" in v.lower():
                    alert_row("🚨", v, "danger")
                else:
                    alert_row("⚠️", v, "warn")

            section_title("Customs")
            alert_row("ℹ️", info["customs"], "info")

            section_title("Visa Status")
            alert_row("✅", info["visa"], "ok")

        with c2:
            section_title("Crossing Tips")
            for tip in info["tips"]:
                alert_row("→", tip, "info")

        st.markdown("---")

    section_title("Mexico Zone Notes")
    alert_row("ℹ️", "Baja peninsula: NO TIP required — entire Baja peninsula is exempt.", "info")
    alert_row("⚠️", "Ferry La Paz to Mazatlan: TIP required for mainland Mexico!", "warn")
    alert_row("🚨", "Driving without Mexican auto insurance is illegal. Get coverage BEFORE crossing.", "danger")
    alert_row("✅", "PEMEX stations accept USD in border towns. Further south — pesos only.", "ok")
