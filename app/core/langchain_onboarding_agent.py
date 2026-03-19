import os
import datetime
import re
from pathlib import Path

import pandas as pd
from fastapi import HTTPException

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from app.core.retrieval import retrieve

# ─── Prepare reports folder ───────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# ─── Initialize the Ollama LLM with configurable host ────────────────────
ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
llm = Ollama(model="mistral", base_url=ollama_host)

# ─── Prompt Templates ─────────────────────────────────────────────────────
checklist_template = PromptTemplate(
    input_variables=["docs"],
    template="""
You are a faculty onboarding assistant. Based on the following policy document excerpts,
generate a Week 1 onboarding checklist as bullet points:

{docs}
""",
)

quiz_template = PromptTemplate(
    input_variables=["docs"],
    template="""
You are a faculty onboarding assistant. Based on the following safety document excerpts,
create a 5‐question multiple‐choice quiz. For each question, list
a) … b) … c) … d) …, and then at the end write: Correct Answer: <letter>

{docs}
""",
)

async def run_onboarding_agent_lc(question: str) -> dict:
    """
    Runs two chains and returns:
     - filename: the Excel checklist filename
     - checklist: list[str]
     - quiz: list[{"question": str, "options": list[str], "answer": str}]
    """
    try:
        # 1) Retrieve policy excerpts
        policy_docs = await retrieve("onboarding policy")
        if not policy_docs:
            raise ValueError("No policy docs found for 'onboarding policy'.")
        policy_text = "\n\n---\n\n".join(policy_docs)

        # 2) Generate Week-1 checklist
        checklist_chain = LLMChain(llm=llm, prompt=checklist_template)
        checklist_text = await checklist_chain.arun(docs=policy_text)
        checklist_items = [
            line.lstrip("-* ").strip()
            for line in checklist_text.splitlines()
            if line.strip()
        ]

        # 3) Retrieve safety excerpts
        safety_docs = await retrieve("safety")
        if not safety_docs:
            raise ValueError("No safety docs found for 'safety'.")
        safety_text = "\n\n---\n\n".join(safety_docs)

        # 4) Generate mini-quiz
        quiz_chain = LLMChain(llm=llm, prompt=quiz_template)
        quiz_text = await quiz_chain.arun(docs=safety_text)

        # 5) Parse the quiz into structured form
        quiz: list[dict] = []
        current_q = None
        options = []

        for line in quiz_text.splitlines():
            line = line.strip()
            if not line:
                continue

            # question line: "1. Who …?"
            m_q = re.match(r"^(\d+)[\.\)]\s*(.+)", line)
            if m_q:
                # store previous
                if current_q:
                    current_q["options"] = options
                    quiz.append(current_q)
                current_q = {"question": m_q.group(2).strip()}
                options = []
                continue

            # option line: "a) Text…"
            m_opt = re.match(r"^([abcd])\)\s*(.+)", line, re.IGNORECASE)
            if m_opt and current_q is not None:
                options.append(m_opt.group(2).strip())
                continue

            # answer line: "Correct Answer: a" or "Answer: b"
            m_ans = re.match(r"^(?:Correct\s+Answer|Answer)\s*[:\-]\s*([abcd])", line, re.IGNORECASE)
            if m_ans and current_q is not None:
                letter = m_ans.group(1).lower()
                idx = ord(letter) - ord("a")
                if 0 <= idx < len(options):
                    current_q["answer"] = options[idx]
                else:
                    current_q["answer"] = ""
                continue

        # append last question
        if current_q:
            current_q["options"] = options
            if "answer" not in current_q:
                current_q["answer"] = ""
            quiz.append(current_q)

        # 6) Write checklist to Excel (no quiz in Excel)
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"onboarding_{ts}.xlsx"
        filepath = REPORT_DIR / filename

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            pd.DataFrame({"Week 1 Checklist": checklist_items}) \
              .to_excel(writer, sheet_name="Week1 Checklist", index=False)

        # 7) Return structured payload
        return {
            "filename": filename,
            "checklist": checklist_items,
            "quiz": quiz,
        }

    except Exception as e:
        # log for debugging
        print("🛑 Onboarding agent error:", e)
        raise HTTPException(status_code=500, detail=f"Onboarding agent error: {e}")
