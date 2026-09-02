"""Results Page Module with Enhanced Risk Gauge & Visualizer"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from PIL import Image
from frontend.components.ui import render_header
from reports import generate_pdf_report, get_pdf_bytes

def render_results():
    render_header()
    st.subheader("📊 Detailed Screening & Forensic Results")

    result = st.session_state.get("last_result")
    if not result:
        st.info("No active screening results found. Please upload a document on the Verification page.")
        if st.button("Go to Verification Page"):
            st.session_state["nav_page"] = "Verification"
            st.rerun()
        return

    screening_id = result.get("screening_id", "N/A")
    risk_score = result.get("overall_risk_score", 0.0)
    decision = result.get("decision", "REVIEW")
    risk_scoring = result.get("risk_scoring_result", {})
    risk_class = risk_scoring.get("risk_classification", "MEDIUM RISK")
    ocr = result.get("ocr_result", {})
    doc_class = ocr.get("classification", {}).get("document_label", "Identity Document")

    # Document Type Badge
    st.markdown(f"🏷️ **Detected Document Type:** `{doc_class}`")

    # Top Metrics Bar
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Screening Session ID", screening_id)
    with col2:
        st.metric("Overall Fraud Risk Score", f"{risk_score:.1f} / 100", delta=risk_class, delta_color="inverse")
    with col3:
        if decision == "APPROVED":
            st.success(f"Verdict: {decision} ({risk_class})")
        elif decision == "MANUAL REVIEW":
            st.warning(f"Verdict: {decision} ({risk_class})")
        else:
            st.error(f"Verdict: {decision} ({risk_class})")

    # PDF Download Trigger Button
    pdf_path = result.get("pdf_report_path")
    if not pdf_path or not os.path.exists(pdf_path):
        try:
            pdf_path = generate_pdf_report(result)
            result["pdf_report_path"] = pdf_path
        except Exception:
            pdf_path = None

    if pdf_path and os.path.exists(pdf_path):
        pdf_bytes = get_pdf_bytes(pdf_path)
        st.download_button(
            label="📥 Download Official PDF Audit Report",
            data=pdf_bytes,
            file_name=f"SIH2_Report_{screening_id}.pdf",
            mime="application/pdf",
            type="primary"
        )

    st.markdown("---")

    # Tabs for breakdown
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "⚖️ Explainable Risk Scoring",
        "🔄 Data Consistency",
        "📄 OCR Extracted Fields",
        "🌐 MRZ Checksum Status",
        "🔬 Document Forensics",
        "👤 Face & Selfie Verification",
        "🔍 Pipeline Log & Raw JSON"
    ])

    mrz = result.get("mrz_result", {})
    forensics = result.get("forensics_result", {})
    face = result.get("face_verification_result", {})
    deepfake = result.get("selfie_authenticity_result", {})
    consistency = result.get("consistency_result", {})

    with tab1:
        st.markdown("#### ⚖️ Explainable Risk Assessment & Drivers")
        st.subheader(f"Risk Classification: `{risk_class}` (Score: {risk_score:.1f}/100)")
        
        st.markdown("##### 📌 Human-Readable Risk Drivers:")
        for exp in risk_scoring.get("human_explanation", []):
            st.markdown(f"- 🔸 {exp}")

        st.markdown("---")
        st.markdown("##### 📊 Configured Weighted Risk Breakdown:")
        breakdown = risk_scoring.get("risk_breakdown", {})
        if breakdown:
            b_list = []
            for module_name, data in breakdown.items():
                b_list.append({
                    "Module Engine": module_name.replace("_", " ").title(),
                    "Component Risk Score": f"{data['component_risk_score']:.1f} / 100",
                    "Configured Weight": f"{data['configured_weight'] * 100:.0f}%",
                    "Weighted Contribution": f"+{data['weighted_contribution']:.2f} pts"
                })
            st.table(b_list)

    with tab2:
        st.markdown("#### 🔄 Cross-Document Data Consistency")
        c_score = consistency.get("consistency_score", 100.0)
        st.metric("Data Consistency Score", f"{c_score:.1f} / 100")
        st.info(consistency.get("summary_message", ""))

        if consistency.get("mismatched_fields"):
            st.error("⚠️ Field Mismatches Detected:")
            for m in consistency["mismatched_fields"]:
                st.markdown(f"- **{m['field']}**: {m['reason']}")

        if consistency.get("matching_fields"):
            st.success("✅ Matching Fields:")
            for match in consistency["matching_fields"]:
                st.markdown(f"- **{match['field']}**: `{match['value']}` (Sources: {', '.join(match['sources'])})")

    with tab3:
        st.markdown("#### Extracted Identity Data")
        fields = ocr.get("fields", {})
        col_a, col_b = st.columns(2)
        with col_a:
            st.text_input("Full Name", value=fields.get("full_name") or "Not Extracted", disabled=True)
            st.text_input("Date of Birth", value=fields.get("date_of_birth") or "Not Extracted", disabled=True)
            st.text_input("Gender", value=fields.get("gender") or "Not Extracted", disabled=True)
        with col_b:
            st.text_input("Document Number", value=fields.get("document_number") or "Not Extracted", disabled=True)
            st.text_input("Nationality", value=fields.get("nationality") or "Not Extracted", disabled=True)
            st.text_input("Expiry Date", value=fields.get("expiry_date") or "Not Extracted", disabled=True)

    with tab4:
        st.markdown("#### MRZ Checksum & ICAO 9303 Verification")
        st.info(f"Status: {mrz.get('status_message', 'N/A')}")
        if mrz.get("mrz_detected"):
            st.json(mrz.get("checksum_status", {}))

    with tab5:
        st.markdown("#### Visual Forensics & Error Level Analysis (ELA)")
        if forensics:
            st.metric("Tampering Risk Level", forensics.get("risk_level", "LOW"))
            ela_path = forensics.get("ela_image_path")
            if ela_path and os.path.exists(ela_path):
                st.image(Image.open(ela_path), caption="Error Level Analysis (ELA) Visual Heatmap")

    with tab6:
        st.markdown("#### Biometric Face & Selfie Authenticity")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Face Match Verdict", face.get("status", "N/A"))
            st.metric("Similarity Score", f"{face.get('similarity_score', 0.0):.1f}%")
        with c2:
            st.metric("Selfie Authenticity", f"{deepfake.get('authenticity_score', 0.0):.1f}%")
            st.caption(deepfake.get("disclaimer", ""))

    with tab7:
        st.markdown("#### 7-Stage Pipeline Execution Log")
        for step in result.get("pipeline_steps", []):
            st.write(f"• **{step['step_name']}**: Status = `{step['status']}` (Score: {step['score']:.1f})")

        st.markdown("#### Full Raw Payload JSON")
        st.json(result)
