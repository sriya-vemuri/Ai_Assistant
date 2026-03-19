import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# ─── CHUNKER ───────────────────────────────────────────────────────────────────
def chunk_text(text: str, size: int = 500) -> list[str]:
    """
    Split `text` into ~size-character chunks on sentence boundaries.
    """
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        if end < length:
            split = text.rfind(".", start, end)
            end = split + 1 if split > start else end
        chunks.append(text[start:end].strip())
        start = end
    return chunks

# ─── VECTOR STORE SETUP ───────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "faiss.index")
META_PATH  = os.path.join(BASE_DIR, "chunks.npy")

# initialize embedder
EMBED_MODEL = "all-MiniLM-L6-v2"
embedder   = SentenceTransformer(EMBED_MODEL)

# load or create FAISS index & metadata
if os.path.exists(INDEX_PATH):
    index  = faiss.read_index(INDEX_PATH)
    chunks = list(np.load(META_PATH, allow_pickle=True))
else:
    index  = None
    chunks = []

async def embed_and_store(texts: list[str]):
    """
    Embed a list of text chunks and store them in the FAISS index.
    """
    embs = embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    global index, chunks
    if index is None:
        dim   = embs.shape[1]
        index = faiss.IndexFlatIP(dim)
    index.add(embs)
    chunks.extend(texts)
    faiss.write_index(index, INDEX_PATH)
    np.save(META_PATH, np.array(chunks, dtype=object))

async def retrieve(question: str, k: int = 5) -> list[str]:
    """
    Retrieve the top-k most relevant chunks for a question.
    """
    q_emb = embedder.encode([question], convert_to_numpy=True, normalize_embeddings=True)
    D, I  = index.search(q_emb, k)
    return [chunks[i] for i in I[0]]

# ─── HOLISTIC UPLOAD -> CHUNK -> EMBED ────────────────────────────────────────
async def chunk_and_embed(path: str, chunk_size: int = 500):
    """
    Read a PDF, chunk its text, and embed+store those chunks.
    """
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text.replace("\n", " ")
    cks = chunk_text(text, size=chunk_size)
    await embed_and_store(cks)
