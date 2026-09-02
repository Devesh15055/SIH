"""
Reusable Streamlit UI Styling and Layout Components
"""

import streamlit as st

def apply_custom_theme():
    st.markdown("""
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #1E88E5 0%, #00E676 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .sih-badge {
            background-color: #0E1726;
            color: #00E676;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid #00E676;
            display: inline-block;
            margin-bottom: 1rem;
        }
        .feature-card {
            background: #1A2332;
            padding: 1.2rem;
            border-radius: 10px;
            border: 1px solid #2A364F;
            margin-bottom: 1rem;
        }
        .status-pass { color: #00E676; font-weight: bold; }
        .status-warn { color: #FFB300; font-weight: bold; }
        .status-fail { color: #FF5252; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown('<div class="main-title">🛡️ AI-Based Fake Identity & Document Screening System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sih-badge">SIH26188 • Smart India Hackathon Enterprise Solution</div>', unsafe_allow_html=True)
