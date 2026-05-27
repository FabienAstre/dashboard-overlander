import streamlit as st
import requests
from components.widgets import section_title

SYSTEM_PROMPT = (
    "You are the Overlander OS AI Co-Pilot — an expert expedition assistant for overlanding, "
    "vanlife, and remote vehicle travel. You specialize in route planning, Baja California travel, "
    "Ford 7.3L Powerstroke diesel vehicles, campsite selection, border crossings (Canada to USA to Mexico), "
    "and expedition safety. Respond concisely and practically with clear structure."
)

QUICK_PROMPTS = [
    "Dangerous sections Kamloops to Cabo?",
    "Top up fuel before Guerrero Negro?",
    "Best free beach camping in Baja Sur?",
    "TIP process at Otay Mesa border?",
    "Pre-departure checklist for 7.3 Powerstroke?",
    "Night driving safety tips for Baja?",
    "Road conditions on Hwy 1 Transpeninsular?",
    "Water strategy for 3 weeks in Baja?",
]


def call_ai(messages):
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system": SYSTEM_PROMPT,
                "messages": messages,
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception as e:
        return "Connection error: " + str(e)


def render_ai_assistant():
    s = st.session_state
    st.markdown("### AI Expedition Co-Pilot")

    chat_col, suggest_col = st.columns([3, 1], gap="medium")

    with suggest_col:
        section_title("Quick Prompts")
        for p in QUICK_PROMPTS:
            if st.button(p, key="ap_" + p, use_container_width=True):
                s.ai_messages.append({"role": "user", "content": p})
                with st.spinner("Co-pilot thinking..."):
                    reply = call_ai(s.ai_messages)
                s.ai_messages.append({"role": "assistant", "content": reply})
                st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        section_title("Trip Context")
        st.markdown(
            '<div class="os-card" style="font-size:0.75rem;">'
            '<div style="color:var(--text-muted);">Route</div>'
            '<div style="color:var(--text-secondary);">' + s.origin.split(",")[0] + " to " + s.destination.split(",")[0] + "</div>"
            '<div style="color:var(--text-muted);margin-top:0.4rem;">Vehicle</div>'
            '<div style="color:var(--text-secondary);">' + s.vehicle_name + "</div>"
            '<div style="color:var(--text-muted);margin-top:0.4rem;">Fuel</div>'
            '<div style="color:var(--accent-amber);">' + str(s.fuel_level_pct) + "% / " + str(s.tank_capacity_l) + "L</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        if st.button("Clear Chat", use_container_width=True):
            s.ai_messages = []
            st.rerun()

    with chat_col:
        if not s.ai_messages:
            st.markdown(
                '<div style="text-align:center;padding:3rem 1rem;color:var(--text-muted);">'
                '<div style="font-size:2rem;margin-bottom:0.5rem;">🧭</div>'
                '<div style="font-family:Rajdhani,sans-serif;font-size:1rem;letter-spacing:0.1em;">CO-PILOT READY</div>'
                '<div style="font-size:0.78rem;margin-top:0.4rem;">Ask about your route, fuel, camping, borders, or vehicle.</div>'
                "</div>",
                unsafe_allow_html=True,
            )

        for msg in s.ai_messages:
            if msg["role"] == "user":
                st.markdown(
                    '<div style="display:flex;justify-content:flex-end;margin-bottom:0.6rem;">'
                    '<div style="background:var(--bg-card-alt);border:1px solid var(--border-glow);'
                    'border-radius:8px 8px 2px 8px;padding:0.6rem 0.9rem;max-width:85%;'
                    'font-size:0.84rem;color:var(--text-primary);">'
                    + msg["content"]
                    + "</div></div>",
                    unsafe_allow_html=True,
                )
            else:
                content = msg["content"].replace("\n", "<br>")
                st.markdown(
                    '<div style="display:flex;justify-content:flex-start;margin-bottom:0.8rem;">'
                    '<div style="background:var(--bg-card);border:1px solid var(--border);'
                    'border-left:3px solid var(--accent-cyan);border-radius:2px 8px 8px 8px;'
                    'padding:0.7rem 1rem;max-width:90%;font-size:0.82rem;'
                    'color:var(--text-secondary);line-height:1.6;">'
                    '<div style="font-family:Rajdhani,sans-serif;font-size:0.7rem;'
                    'color:var(--accent-cyan);letter-spacing:0.08em;margin-bottom:0.4rem;">CO-PILOT</div>'
                    + content
                    + "</div></div>",
                    unsafe_allow_html=True,
                )

        with st.form("ai_form", clear_on_submit=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                user_input = st.text_input(
                    "Message",
                    placeholder="Ask your co-pilot...",
                    label_visibility="collapsed",
                    key="ai_inp",
                )
            with c2:
                submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted and user_input.strip():
            ctx = (
                "Context: "
                + s.origin + " to " + s.destination
                + ", " + s.vehicle_name
                + ", " + str(s.tank_capacity_l) + "L tank at " + str(s.fuel_level_pct) + "%"
                + ", " + str(s.consumption_l100) + "L/100km"
                + ", odo " + str(s.odometer_km) + " km\n\n"
                + user_input.strip()
            )
            s.ai_messages.append({"role": "user", "content": user_input.strip()})
            with st.spinner("Co-pilot thinking..."):
                api_messages = s.ai_messages[:-1] + [{"role": "user", "content": ctx}]
                reply = call_ai(api_messages)
            s.ai_messages.append({"role": "assistant", "content": reply})
            st.rerun()
