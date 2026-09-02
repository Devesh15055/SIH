import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
SIH26188 - Streamlit Frontend Main Router
"""

import streamlit as st
from frontend.components.ui import apply_custom_theme
from frontend.pages.home import render_home
from frontend.pages.verification import render_verification
from frontend.pages.results import render_results
from frontend.pages.history import render_history

st.set_page_config(
    page_title="SIH26188 Identity Screening",
    page_icon="🛡️",
    layout="wide"
)

apply_custom_theme()

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Home"

with st.sidebar:
    st.title("🛡️ SIH26188")
    st.caption("AI Identity Screening System")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["Home", "Verification", "Results", "History"],
        index=["Home", "Verification", "Results", "History"].index(st.session_state["nav_page"])
    )
    st.session_state["nav_page"] = page

    st.markdown("---")
    st.markdown("**System Health:** 🟢 Ready")
    st.markdown("**Problem Statement:** SIH26188")

if page == "Home":
    render_home()
elif page == "Verification":
    render_verification()
elif page == "Results":
    render_results()
elif page == "History":
    render_history()
