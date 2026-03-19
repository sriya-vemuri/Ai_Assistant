import os
import re
import datetime
import pandas as pd
from app.core.retrieval import chunks

# Directory to save reports
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

async def run_agent(question: str):
    """
    Document Analyzer Agent:
     - Flags outdated (year < 2022) 
     - Flags exact duplicates (redundant chunks)
     - Writes an Excel report with chunk_id, issue, snippet, details
    """
    rows = []

    # 1) Outdated: look for any year < 2022 in chunk text
    year_pattern = re.compile(r"\b(19[0-9]{2}|20[0-9]{2})\b")
    for idx, chunk in enumerate(chunks):
        for match in year_pattern.findall(chunk):
            year = int(match)
            if year < 2022:
                rows.append({
                    "chunk_id": idx,
                    "issue": "outdated",
                    "detail": f"Found year {year}",
                    "snippet": chunk[:200]
                })
                break

    # 2) Redundant: exact duplicate text
    seen = {}
    for idx, chunk in enumerate(chunks):
        if chunk in seen:
            rows.append({
                "chunk_id": idx,
                "issue": "redundant",
                "detail": f"Duplicate of chunk_id {seen[chunk]}",
                "snippet": chunk[:200]
            })
        else:
            seen[chunk] = idx

    # 3) Write to Excel
    df = pd.DataFrame(rows)
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    report_file = os.path.join(REPORT_DIR, f"doc_analysis_{ts}.xlsx")
    df.to_excel(report_file, index=False)

    return {"report_path": report_file, "issues_found": len(rows)}
