import streamlit as st

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg-base:      #0a0c10;
    --bg-panel:     #0f1117;
    --bg-card:      #141820;
    --bg-card-alt:  #1a1f2e;
    --border:       #1e2535;
    --border-glow:  #2a3a5c;
    --accent-cyan:  #00d4ff;
    --accent-amber: #f59e0b;
    --accent-green: #10b981;
    --accent-red:   #ef4444;
    --accent-violet:#7c3aed;
    --text-primary: #e2e8f0;
    --text-secondary:#94a3b8;
    --text-muted:   #475569;
    --text-accent:  #00d4ff;
}
.stApp { background-color: var(--bg-base); font-family: 'Inter', sans-serif; }
.main .block-container { padding-top: 0.5rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
section[data-testid="stSidebar"] { background-color: var(--bg-panel) !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.os-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; position: relative; overflow: hidden; }
.os-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--accent-cyan), transparent); opacity: 0.6; }
.os-card-red::before   { background: linear-gradient(90deg, var(--accent-red), transparent); }
.os-card-amber::before { background: linear-gradient(90deg, var(--accent-amber), transparent); }
.os-card-green::before { background: linear-gradient(90deg, var(--accent-green), transparent); }
.os-card-violet::before{ background: linear-gradient(90deg, var(--accent-violet), transparent); }

.os-topbar { background: var(--bg-panel); border-bottom: 1px solid var(--border); padding: 0.5rem 1.5rem; display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.os-topbar-title { font-family: 'Rajdhani', sans-serif; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.12em; color: var(--accent-cyan); text-transform: uppercase; }
.os-badge { display: inline-flex; align-items: center; gap: 0.3rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 20px; padding: 0.2rem 0.7rem; font-size: 0.72rem; font-family: 'Share Tech Mono', monospace; color: var(--text-secondary); }
.os-badge-green { border-color: var(--accent-green); color: var(--accent-green); }
.os-badge-amber { border-color: var(--accent-amber); color: var(--accent-amber); }
.os-badge-red   { border-color: var(--accent-red);   color: var(--accent-red); }
.os-badge-cyan  { border-color: var(--accent-cyan);  color: var(--accent-cyan); }

.os-metric { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 0.9rem 1rem; text-align: center; }
.os-metric-value { font-family: 'Rajdhani', sans-serif; font-size: 1.9rem; font-weight: 700; color: var(--accent-cyan); line-height: 1; }
.os-metric-label { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.25rem; }
.os-metric-sub { font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.2rem; }

.os-section-title { font-family: 'Rajdhani', sans-serif; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 0.75rem; }

.os-alert { display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.6rem 0.8rem; border-radius: 6px; margin-bottom: 0.4rem; font-size: 0.8rem; }
.os-alert-warn   { background: rgba(245,158,11,0.1);  border-left: 3px solid var(--accent-amber); }
.os-alert-danger { background: rgba(239,68,68,0.1);   border-left: 3px solid var(--accent-red); }
.os-alert-info   { background: rgba(0,212,255,0.08);  border-left: 3px solid var(--accent-cyan); }
.os-alert-ok     { background: rgba(16,185,129,0.1);  border-left: 3px solid var(--accent-green); }

.fuel-bar-track { background: var(--bg-card-alt); border-radius: 4px; height: 8px; overflow: hidden; margin: 0.4rem 0; }
.fuel-bar-fill  { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green)); }
.fuel-bar-fill.low { background: linear-gradient(90deg, var(--accent-red), var(--accent-amber)); }

.os-waypoint { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 1px solid var(--border); font-size: 0.82rem; }
.os-waypoint-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--accent-cyan); flex-shrink: 0; }
.os-waypoint-dot.end { background: var(--accent-green); }
.os-waypoint-dot.mid { background: var(--accent-amber); width: 7px; height: 7px; }

.mono     { font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: var(--text-accent); }
.mono-dim { font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--text-muted); }

.stSelectbox > div > div, .stTextInput > div > div > input, .stTextArea textarea { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 6px !important; }
.stButton > button { background: var(--bg-card-alt) !important; border: 1px solid var(--border-glow) !important; color: var(--text-primary) !important; border-radius: 6px !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; letter-spacing: 0.05em !important; }
.stButton > button:hover { border-color: var(--accent-cyan) !important; color: var(--accent-cyan) !important; }
div[data-testid="stMetricValue"] { font-family: 'Rajdhani', sans-serif !important; font-size: 1.8rem !important; font-weight: 700 !important; color: var(--accent-cyan) !important; }
div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; color: var(--text-muted) !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
.stTabs [data-baseweb="tab-list"] { background-color: var(--bg-card) !important; border-radius: 8px !important; padding: 0.2rem !important; }
.stTabs [data-baseweb="tab"] { background-color: transparent !important; color: var(--text-secondary) !important; border-radius: 6px !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background-color: var(--bg-card-alt) !important; color: var(--accent-cyan) !important; }
h1, h2, h3 { font-family: 'Rajdhani', sans-serif !important; font-weight: 700 !important; color: var(--text-primary) !important; }
p, li, span, label { color: var(--text-secondary) !important; }
</style>
"""

def setup_page_config():
    st.set_page_config(page_title="Overlander OS", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")
    st.markdown(DARK_CSS, unsafe_allow_html=True)
