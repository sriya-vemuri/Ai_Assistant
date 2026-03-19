from fastapi import APIRouter, File, UploadFile, HTTPException
from app.utils.file_utils import save_doc
from app.core.retrieval import chunk_and_embed

router = APIRouter()

@router.post("/")
async def upload(files: list[UploadFile] = File(...)):
    """
    1) Save each uploaded file
    2) Run chunk_and_embed() to extract→chunk→embed
    """
    try:
        for f in files:
            path = await save_doc(f)
            await chunk_and_embed(path)
        return {"message": f"{len(files)} document(s) uploaded and indexed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
