import numpy as np, faiss
from sentence_transformers import SentenceTransformer

chunks = np.load("app/chunks.npy", allow_pickle=True)
print(f"Loaded {len(chunks)} chunks.")
print("Snippet:", chunks[0][:100].replace('\n',' '), "...")

idx = faiss.read_index("app/faiss.index")
print(f"Index dimension: {idx.d}, total vectors: {idx.ntotal}")

embedder = SentenceTransformer("all-MiniLM-L6-v2")
v = embedder.encode([chunks[0]], convert_to_numpy=True, normalize_embeddings=True)
D, I = idx.search(v, 1)
print("Top match ID:", I[0][0], "— distance:", D[0][0])