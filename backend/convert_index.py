import json
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "KBot Storage")

print("Loading vector store (319 MB, takes ~30s)...")
with open(os.path.join(STORAGE_DIR, "default__vector_store.json")) as f:
    vs = json.load(f)

embedding_dict = vs["embedding_dict"]
node_ids = list(embedding_dict.keys())
print(f"Found {len(node_ids)} nodes")

print("Building numpy array...")
vectors = np.array([embedding_dict[nid] for nid in node_ids], dtype=np.float32)
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
vectors_norm = (vectors / (norms + 1e-10)).astype(np.float16)
np.save(os.path.join(STORAGE_DIR, "vectors.npy"), vectors_norm)
print(f"Saved vectors.npy ({vectors_norm.nbytes / 1024 / 1024:.1f} MB)")

with open(os.path.join(STORAGE_DIR, "node_ids.json"), "w") as f:
    json.dump(node_ids, f)

print("Loading docstore...")
with open(os.path.join(STORAGE_DIR, "docstore.json")) as f:
    ds = json.load(f)

doc_data = ds["docstore/data"]
texts = []
for nid in node_ids:
    node = doc_data.get(nid, {})
    data = node.get("__data__", {})
    if isinstance(data, str):
        data = json.loads(data)
    texts.append(data.get("text", ""))

with open(os.path.join(STORAGE_DIR, "texts.json"), "w") as f:
    json.dump(texts, f)
print(f"Saved texts.json ({os.path.getsize(os.path.join(STORAGE_DIR, 'texts.json')) / 1024 / 1024:.1f} MB)")

print("Removing original large files...")
os.remove(os.path.join(STORAGE_DIR, "default__vector_store.json"))
os.remove(os.path.join(STORAGE_DIR, "docstore.json"))

print("Done! KBot Storage is now lightweight.")
