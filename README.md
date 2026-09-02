# 🛡️ AI-Based Fake Identity & Document Screening System (SIH26188)

> **Smart India Hackathon (SIH) Project — Problem Statement ID: SIH26188**  
> An enterprise-grade, modular, and explainable multi-signal AI/ML platform designed to detect fraudulent identity documents, visual forgeries, metadata anomalies, face spoofing/deepfakes, and cross-document data inconsistencies in real-time.

---

## 📌 Project Overview
The **SIH26188 Identity Screening System** provides automated, multi-signal identity verification for modern governance, banking, and security onboarding workflows. It evaluates uploaded identity documents (Passports, Aadhaar, PAN, Visas, Driving Licenses) across **7 distinct AI/ML verification stages**, producing a transparent, human-readable risk score and downloadable PDF security audit report.

---

## ⚡ Key Features
* **Multi-Engine OCR & Field Extractor:** Line-bounded extraction of Full Name, DOB, Gender, Nationality, Document Number, Expiry Date, and Address.
* **ICAO 9303 MRZ Checksum Engine:** TD3 (Passport) and TD1 (ID Card) 7-3-1 weight check digit validator. Non-MRZ documents return a clear status without failing the pipeline.
* **Biometric Face Verification:** ID photo vs selfie facial matching with image quality checks (blur, resolution, exposure).
* **Selfie Authenticity Screening:** Noise residual analysis and digital smoothing detection labeled explicitly as *Prototype AI-assisted screening*.
* **Visual Document Forensics:** Error Level Analysis (ELA) heatmap generation, EXIF software signature inspection (`Photoshop`, `GIMP`, `Canva`), and JPEG 8x8 block grid discontinuity analysis.
* **Cross-Document Data Consistency:** Multi-source field matcher across Primary ID, Supporting Document, and MRZ data.
* **Configurable Explainable Risk Scoring:** Weighted risk aggregation producing `LOW RISK`, `MEDIUM RISK`, `HIGH RISK`, and `CRITICAL RISK` classifications with human-readable score explanations.
* **PDF Audit Report Generator:** Official downloadable PDF report with legal disclaimer and case summary.
* **SQLite Audit History:** Privacy-focused case metadata log (zero raw images stored).

---

## 🏛️ Repository Architecture

```text
SIH2/
├── frontend/                     # Streamlit User Interface
│   ├── app.py                    # Streamlit Entrypoint & Navigation Router
│   ├── pages/                    # Multi-page views (Home, Verification, Results, History)
│   ├── components/               # Custom UI Components & Glassmorphism Styling
│   └── utils/                    # Decoupled HTTP API Client
│
├── backend/                      # FastAPI Microservice Backend
│   ├── main.py                   # FastAPI Application Entrypoint & /health route
│   ├── api/v1/router.py          # REST API Endpoints (/health, /screen, /cases)
│   ├── services/                 # 7-Stage Pipeline Orchestration Service
│   ├── models/schemas.py         # Pydantic Schemas for Requests & Responses
│   └── core/                     # Core configs, security, and temp file cleanup
│
├── ai_modules/                   # Decoupled AI/ML Engines
│   ├── ocr/                      # Multi-Engine OCR & Line-Bounded Field Parser
│   ├── mrz_validation/           # ICAO 9303 MRZ Parser & 7-3-1 Checksum Engine
│   ├── face_verification/        # Biometric Face Quality & Similarity Matcher
│   ├── document_forensics/       # ELA Heatmaps, EXIF Metadata & Compression
│   ├── deepfake_detection/       # Selfie Noise Residual & Smoothing Inspector
│   └── risk_scoring/             # Configurable Risk Engine & Consistency Checker
│
├── database/                     # SQLite Database Storage (sih2.db)
├── reports/                      # PDF Audit Report Engine & Templates
├── tests/                        # Automated Unit Tests (100% Pass)
├── sample_data/                  # Synthetic Test Data Guidelines
│   └── synthetic_examples/       # Non-PII Synthetic Documents & Samples
│
├── docs/                         # Architecture Specs
├── temp/                         # Isolated Temporary Workspace
├── generated_reports/            # Output PDF Security Audit Reports
│
├── .gitignore                    # Version Control Exclusions
├── .env.example                  # Environment Variables Template
├── README.md                     # Comprehensive Setup & Project Guide
├── requirements.txt              # Dependency Manifest
├── CONTRIBUTING.md               # Team Collaboration & Git Guidelines
└── LICENSE                       # MIT Open-Source License
```

---

## 💻 Installation & Setup Instructions

### 1. Environment Setup
```bash
# From the repository root (Desktop/SIH2):
python -m venv venv

# On Windows (PowerShell):
.env\Scriptsctivate

# On Linux / macOS:
source venv/bin/activate
```

### 2. Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Exact Commands to Run

### 1. Start FastAPI Backend Microservice
```bash
# In Terminal 1 (from Desktop/SIH2 root):
python -m uvicorn backend.main:app --reload --port 8000
```
* **Health Endpoint:** `http://localhost:8000/health`
* **Swagger API Docs:** `http://localhost:8000/docs`

### 2. Start Streamlit Frontend Dashboard
```bash
# In Terminal 2 (from Desktop/SIH2 root):
streamlit run frontend/app.py
```
* **Dashboard Access:** `http://localhost:8501`

### 3. Run Automated Unit Tests
```bash
# From Desktop/SIH2 root:
python -m unittest discover -s tests
```

---

## 🤖 Required Models & AI Dependencies

* **OpenCV (`opencv-python-headless`):** Face detection Haar Cascades, ELA image subtraction, Laplacian variance, and HSV color histograms.
* **EasyOCR & PyTorch (`torch`, `torchvision`):** Document text extraction and OCR field parsing.
* **ReportLab (`reportlab`):** PDF audit document compilation.
* **SQLite (`sqlite3`):** Non-sensitive case history logging.

---

## 🔒 Privacy Considerations
1. **Ephemeral Processing:** Uploaded identity documents are processed in-memory. Raw user document images are **never permanently stored** on disk or database.
2. **Sanitized History Logs:** The SQLite database (`sih2.db`) records only case IDs, timestamps, risk scores, decisions, and non-sensitive OCR count summaries.
3. **Automatic Cleanup:** Temporary ELA files generated in `temp/` are automatically purged after pipeline execution.

---

## 👥 Team Collaboration Guidelines
Refer to [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming conventions, PR guidelines, and modular contribution rules.

---

## 🔮 Future Scope
* Integration of deep Learning face anti-spoofing models (Silent-Face-Anti-Spoofing / MiniFASNet).
* Fine-tuned EasyOCR models for regional Indian languages (Hindi, Tamil, Telugu, Marathi).
* Blockchain-based immutable audit trail for screening decisions.
