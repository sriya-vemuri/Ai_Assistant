# app/routers/query.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.guardrails import check_query
from app.core.llm import generate_response
from app.core.retrieval import retrieve
from app.core.agent import run_agent                # analyzer
from app.core.langchain_onboarding_agent import run_onboarding_agent_lc  # onboarding

class QueryReq(BaseModel):
    question: str
    use_agent: bool = False
    agent_type: Optional[str] = None  # "analyzer" or "onboarding"

router = APIRouter()

@router.post("/")
async def query(req: QueryReq):
    # 1) guardrail
    await check_query(req.question)

    # 2) agent path
    if req.use_agent:
        if req.agent_type == "analyzer":
            return await run_agent(req.question)
        elif req.agent_type == "onboarding":
            return await run_onboarding_agent_lc(req.question)
        else:
            raise HTTPException(
                400, detail="agent_type must be 'analyzer' or 'onboarding'"
            )

    # 3) RAG fallback (chatbot)
    docs = await retrieve(req.question)
    prompt = (
        "Use only these excerpts to answer the question:\n\n"
        + "\n\n---\n\n".join(docs)
        + f"\n\nQuestion: {req.question}\nAnswer:"
    )
    try:
        answer = await generate_response(prompt)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(500, detail=f"LLM error: {e}")