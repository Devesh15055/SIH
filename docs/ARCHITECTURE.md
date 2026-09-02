# 🏛️ SIH26188 System Architecture & Module Design

This document details the modular workflow and component interactions of the Fake Identity & Document Screening System.

## Pipeline Sequence

```
[User Document Upload]
        │
        ▼
[FastAPI REST API Gateway]
        │
        ├──► [Document Forensics Engine] ──► (ELA, Splice, Sharpness Residuals)
        ├──► [OCR & Field Extractor]     ──► (Text Fields & Regex Parsing)
        ├──► [MRZ Validator]             ──► (ICAO 9303 Checksums)
        ├──► [Face Verification Engine]  ──► (ID Photo vs Selfie Matching)
        └──► [Deepfake Detector]        ──► (Generative Artifact Check)
        │
        ▼
[Explainable Risk Scoring Engine] ───────► Aggregated Risk Score & Decision Flags
        │
        ▼
[PDF Audit Report Generator]     ───────► Downloadable Security Report
```
