import streamlit as st
from core.config import setup_page_config
from core.session import init_session_state
from components.topbar import render_topbar
from components.sidebar import render_sidebar
from views.dashboard import render_dashboard
from views.route_planner import render_route_planner
from views.map_intelligence import render_map_intelligence
from views.fuel_planner import render_fuel_planner
from views.camping import render_camping
from views.vehicle import render_vehicle
from views.ai_assistant import render_ai_assistant
from views.border_alerts import render_border_alerts

setup_page_config()
init_session_state()
render_topbar()
page = render_sidebar()

PAGE_MAP = {
    "🗺️ Mission Control":  render_dashboard,
    "📍 Route Planner":    render_route_planner,
    "🌍 Map Intelligence": render_map_intelligence,
    "⛽ Fuel Planner":     render_fuel_planner,
    "🏕️ Camp Intel":       render_camping,
    "🚗 Vehicle Panel":    render_vehicle,
    "🛂 Border Alerts":    render_border_alerts,
    "🤖 AI Assistant":     render_ai_assistant,
}

PAGE_MAP.get(page, render_dashboard)()
