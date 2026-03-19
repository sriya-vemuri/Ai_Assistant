import os, uuid
import aiofiles
from pathlib import Path

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)

async def save_doc(f):
    """
    Save the raw uploaded file to disk and return its path.
    """
    ext = os.path.splitext(f.filename)[1]
    fn  = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / fn

    # write the uploaded bytes to disk
    async with aiofiles.open(path, "wb") as out:
        await out.write(await f.read())

    return str(path)
