import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
"""Home Page Module"""
import streamlit as st
from frontend.components.ui import render_header

def render_home():
    render_header()
    
    st.markdown("""
    ### 📌 Project Overview
    The **SIH26188 Fake Identity & Document Screening System** provides automated, multi-signal identity fraud detection. 
    It evaluates uploaded identity documents (Passports, Aadhaar, PAN, Visas, Driving Licenses) across **7 distinct AI/ML verification stages**.
    """)

    st.markdown("---")
    st.markdown("### ⚡ Key Capabilities")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 Multi-Engine OCR & Parser</h4>
            <p>Automatically extracts Full Name, DOB, Gender, Doc Number, and Expiry Date with quality confidence scoring.</p>
        </div>
        <div class="feature-card">
            <h4>🌐 ICAO 9303 MRZ Checksum Validator</h4>
            <p>Verifies 7-3-1 weight check digits for passports and official ID cards to detect number tampering.</p>
        </div>
        <div class="feature-card">
            <h4>🔬 Document Forensics</h4>
            <p>Performs Error Level Analysis (ELA), edge discontinuity, and copy-paste splice detection.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>👤 Biometric Face Verification</h4>
            <p>Matches document ID photo against live user selfie with anti-spoofing liveness detection.</p>
        </div>
        <div class="feature-card">
            <h4>⚖️ Explainable Risk Scoring</h4>
            <p>Aggregates multi-signal forensic findings into an overall decision recommendation (CLEAR / REVIEW / REJECT).</p>
        </div>
        <div class="feature-card">
            <h4>📊 Downloadable Audit Reports</h4>
            <p>Generates detailed PDF security reports for compliance and manual auditor verification.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Screening Document Now", type="primary"):
        st.session_state["nav_page"] = "Verification"
        st.rerun()
