import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
"""Verification Page Module"""
import streamlit as st
import time
from PIL import Image
from frontend.components.ui import render_header
from frontend.utils.api_client import submit_screening_request, check_backend_health

def render_verification():
    render_header()
    st.subheader("📤 Document & Selfie Verification Portal")

    # Backend Connection Indicator
    api_online = check_backend_health()
    if api_online:
        st.success("🟢 Backend FastAPI Engine Connected (localhost:8000)")
    else:
        st.warning("🟡 Backend API Offline — Using Fallback Engine Mode")

    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 1. Primary Identity Document *")
        primary_file = st.file_uploader("Upload Passport, ID, Aadhaar, or License", type=["jpg", "jpeg", "png", "webp"], key="primary")
        if primary_file:
            st.image(Image.open(primary_file), caption="Primary Document Preview")

    with col2:
        st.markdown("#### 2. Live Selfie Photo")
        selfie_file = st.file_uploader("Upload Live User Selfie", type=["jpg", "jpeg", "png", "webp"], key="selfie")
        if selfie_file:
            st.image(Image.open(selfie_file), caption="Selfie Preview")

    with col3:
        st.markdown("#### 3. Supporting Document (Optional)")
        support_file = st.file_uploader("Upload Address Proof / Utility Bill", type=["jpg", "jpeg", "png", "pdf"], key="support")
        if support_file:
            st.info(f"Attached: {support_file.name}")

    st.markdown("---")
    st.markdown("### 🔄 7-Stage Screening Pipeline Interface")
    
    pipeline_container = st.container()
    
    stages = [
        "1. OCR Text & Field Extraction",
        "2. MRZ Checksum Validation",
        "3. Visual Document Forensics & ELA",
        "4. Biometric Face Match Verification",
        "5. Selfie Authenticity & Anti-Spoofing",
        "6. Cross-Field Data Consistency Check",
        "7. Explainable Risk Assessment"
    ]

    for stage in stages:
        pipeline_container.markdown(f"🔹 **{stage}**: *Pending Upload*")

    if primary_file:
        if st.button("⚡ Run Full Screening Pipeline", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, stage in enumerate(stages):
                status_text.text(f"Executing {stage}...")
                progress_bar.progress(int((idx + 1) / len(stages) * 100))
                time.sleep(0.2)

            # Read file bytes
            primary_bytes = primary_file.getvalue()
            selfie_bytes = selfie_file.getvalue() if selfie_file else None

            if api_online:
                api_res = submit_screening_request(
                    primary_bytes, primary_file.name,
                    selfie_bytes, selfie_file.name if selfie_file else None
                )
                if api_res["success"]:
                    st.session_state["last_result"] = api_res["data"]
                    st.success("Screening Pipeline Completed!")
                    st.session_state["nav_page"] = "Results"
                    st.rerun()
                else:
                    st.error(api_res["error"])
            else:
                # Local fallback execution
                from backend.services.pipeline_service import run_screening_pipeline
                res = run_screening_pipeline(primary_bytes, selfie_bytes)
                st.session_state["last_result"] = res
                st.success("Screening Pipeline Completed (Local Engine)!")
                st.session_state["nav_page"] = "Results"
                st.rerun()
