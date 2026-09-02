"""History Page Module displaying SQLite Audit Cases with Interactive Search & Filter"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from frontend.components.ui import render_header
from database import get_all_screening_cases

def render_history():
    render_header()
    st.subheader("📜 Verification Session Audit Log (SQLite Database)")

    st.markdown("""
    Filter and inspect historical identity document screening sessions.  
    *(No raw identity document images are stored for privacy compliance).*
    """)

    cases = get_all_screening_cases()

    if not cases:
        st.info("No previous screening cases found in SQLite database.")
        return

    # Interactive Search & Filter Controls
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Search by Case ID", value="").strip().upper()
    with col_filter:
        filter_risk = st.selectbox("Filter Risk Classification", ["ALL", "LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL RISK"])

    filtered_cases = cases
    if search_query:
        filtered_cases = [c for c in filtered_cases if search_query in c["case_id"].upper()]
    if filter_risk != "ALL":
        filtered_cases = [c for c in filtered_cases if c["final_classification"] == filter_risk]

    table_data = []
    for c in filtered_cases:
        table_data.append({
            "Case ID": c["case_id"],
            "Timestamp": c["timestamp"],
            "Risk Score": f"{c['final_risk_score']:.1f} / 100",
            "Classification": c["final_classification"],
            "Decision Verdict": c["decision"],
            "Processing Status": c["processing_status"]
        })

    st.markdown(f"**Showing {len(table_data)} case records:**")
    st.dataframe(table_data)
