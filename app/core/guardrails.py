import re
from fastapi import HTTPException

bad_words = ["classified", "confidential", "insider", "slur", "hate", "bully", "damn", "hell", "ass", "bitch", "shit", "fuck", "racist", "sexist", "homophobic", "bigot", "weed", "coke", "meth", "stoned", "kill", "murder", "assault", "weapon", "cheat", "plagiarize", "copycat", "douche", "loser", "suck", "crap", "porn", "nude", "sex", "kink"]

async def check_query(q: str):
    for term in bad_words:
        if re.search(rf"\b{term}\b", q, re.IGNORECASE):
            raise HTTPException(400, f"Query contains banned term: {term}")