"""
SQLite Database Manager for Non-Sensitive Case History Storage
Stores case metadata, timestamps, risk scores, decisions, and non-sensitive summary JSON.
Does NOT store raw identity document images.
"""

import sqlite3
import json
import datetime
import os
from typing import Dict, List, Any, Optional

DB_PATH = "C:/Users/Hp/OneDrive/Desktop/SIH2/database/sih2.db"

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screening_cases (
            case_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            processing_status TEXT NOT NULL,
            final_risk_score REAL NOT NULL,
            final_classification TEXT NOT NULL,
            decision TEXT NOT NULL,
            summary_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_screening_case(
    case_id: str,
    risk_score: float,
    classification: str,
    decision: str,
    summary_data: Dict[str, Any],
    status: str = "COMPLETED"
) -> bool:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        
        # Sanitize summary data to ensure NO raw image bytes/base64 are saved
        clean_summary = {
            "ocr_confidence": summary_data.get("ocr_result", {}).get("confidence", 0.0),
            "ocr_doc_number": summary_data.get("ocr_result", {}).get("fields", {}).get("document_number"),
            "mrz_detected": summary_data.get("mrz_result", {}).get("mrz_detected", False),
            "forensics_risk": summary_data.get("forensics_result", {}).get("risk_level", "LOW"),
            "face_status": summary_data.get("face_verification_result", {}).get("status", "INCONCLUSIVE"),
            "consistency_score": summary_data.get("consistency_result", {}).get("consistency_score", 100.0)
        }

        cursor.execute("""
            INSERT OR REPLACE INTO screening_cases 
            (case_id, timestamp, processing_status, final_risk_score, final_classification, decision, summary_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (case_id, now_str, status, float(risk_score), classification, decision, json.dumps(clean_summary)))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving screening case to DB: {str(e)}")
        return False

def get_all_screening_cases(limit: int = 100) -> List[Dict[str, Any]]:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT case_id, timestamp, processing_status, final_risk_score, final_classification, decision, summary_json
            FROM screening_cases
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "case_id": r["case_id"],
                "timestamp": r["timestamp"],
                "processing_status": r["processing_status"],
                "final_risk_score": r["final_risk_score"],
                "final_classification": r["final_classification"],
                "decision": r["decision"],
                "summary": json.loads(r["summary_json"]) if r["summary_json"] else {}
            })
        return results
    except Exception as e:
        print(f"Error fetching screening cases: {str(e)}")
        return []

def get_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT case_id, timestamp, processing_status, final_risk_score, final_classification, decision, summary_json
            FROM screening_cases
            WHERE case_id = ?
        """, (case_id,))
        r = cursor.fetchone()
        conn.close()

        if r:
            return {
                "case_id": r["case_id"],
                "timestamp": r["timestamp"],
                "processing_status": r["processing_status"],
                "final_risk_score": r["final_risk_score"],
                "final_classification": r["final_classification"],
                "decision": r["decision"],
                "summary": json.loads(r["summary_json"]) if r["summary_json"] else {}
            }
        return None
    except Exception as e:
        print(f"Error fetching case {case_id}: {str(e)}")
        return None
