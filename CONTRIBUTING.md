# 👥 Contributing Guidelines — SIH26188 Team

Thank you for contributing to the **AI-Based Fake Identity & Document Screening System (SIH26188)**.  
Our codebase is structured into isolated, decoupled modules so that multiple team members can work on frontend, backend, and AI engines simultaneously without code conflicts.

---

## 🌿 Simple Team Git Workflow

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SIH2
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/module-name
```
*Examples:* `feature/ocr-parser`, `feature/mrz-checksums`, `feature/face-matching`

### 3. Make Changes & Test
```bash
# Run unit test suite before committing:
python -m unittest discover -s tests
```

### 4. Stage and Commit Changes
```bash
git add .
git commit -m "Describe the change"
```

### 5. Push Branch to GitHub
```bash
git push origin feature/module-name
```

### 6. Create a Pull Request
Open a Pull Request on GitHub against the `main` branch. Describe your modular additions, test results, and tag team members for code review.

---

## 🧩 Module Ownership Breakdown

| Module | Directory Location | Core Responsibilities |
| :--- | :--- | :--- |
| **Frontend** | `frontend/` | Streamlit layout, multi-page routing, UI components, PDF download. |
| **Backend API** | `backend/` | FastAPI REST endpoints (`/health`, `/screen`, `/cases`), CORS, schema validation. |
| **OCR Module** | `ai_modules/ocr/` | Document text extraction and line-bounded field parsing (Name, DOB, Doc No, Expiry). |
| **MRZ Validation** | `ai_modules/mrz_validation/` | ICAO 9303 MRZ line detector and 7-3-1 weight check digit calculation. |
| **Document Forensics** | `ai_modules/document_forensics/` | ELA visual heatmaps, EXIF software metadata, 8x8 JPEG compression analysis. |
| **Face Verification** | `ai_modules/face_verification/` | ID photo vs selfie matching, image quality metrics, HSV histogram similarity. |
| **Selfie Screening** | `ai_modules/deepfake_detection/` | Noise residual analysis, digital smoothing detection (Prototype AI Screening). |
| **Risk Scoring** | `ai_modules/risk_scoring/` | Configurable weighted risk aggregation & human-readable explainability. |
| **PDF Reports** | `reports/` | Audit PDF generation (`reportlab`). |
| **Database** | `database/` | Non-sensitive SQLite case history storage (`sih2.db`). |

---

## 🔒 Security & Privacy Directives

1. **Never Commit Secrets:** Do not commit `.env` or API credentials.
2. **Never Commit Model Weights:** Large model files (`*.pth`, `*.onnx`) belong in release assets, not Git.
3. **Never Commit Real PII:** Uploaded document images are for ephemeral processing only. Never store or commit real personal identity documents into Git.
