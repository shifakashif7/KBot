import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import docx2txt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

STORAGE_DIR = os.path.join(BASE_DIR, "KBot Storage")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
EMBED_MODEL = "text-embedding-3-large"
BATCH_SIZE = 100

if os.path.exists(STORAGE_DIR):
    print("Index already exists, skipping build.")
    exit()

client = OpenAI()


def extract_text(filepath):
    if filepath.lower().endswith(".pdf"):
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif filepath.lower().endswith(".docx"):
        return docx2txt.process(filepath)
    elif filepath.lower().endswith(".txt"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def chunk_text(text):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if len(c.strip()) > 50]


data_dirs = [d for d in [
    os.path.join(BASE_DIR, "data"),
    os.path.join(BASE_DIR, "new_data"),
] if os.path.exists(d)]

if not data_dirs:
    print("ERROR: No data/ or new_data/ directories found.")
    exit(1)

all_chunks = []
for data_dir in data_dirs:
    for fname in sorted(os.listdir(data_dir)):
        fpath = os.path.join(data_dir, fname)
        text = extract_text(fpath)
        if not text.strip():
            print(f"  WARNING: no text extracted from {fname}")
            continue
        chunks = chunk_text(text)
        print(f"  {fname}: {len(text):,} chars → {len(chunks)} chunks")
        all_chunks.extend(chunks)

print(f"\nTotal chunks to embed: {len(all_chunks)}")
print(f"Estimated cost: ~${len(all_chunks) * 0.0000013:.4f}")

all_embeddings = []
for i in range(0, len(all_chunks), BATCH_SIZE):
    batch = all_chunks[i:i + BATCH_SIZE]
    response = client.embeddings.create(model=EMBED_MODEL, input=batch)
    all_embeddings.extend([item.embedding for item in response.data])
    print(f"  Embedded {min(i + BATCH_SIZE, len(all_chunks))}/{len(all_chunks)}")

os.makedirs(STORAGE_DIR)
vectors = np.array(all_embeddings, dtype=np.float32)
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
vectors_norm = (vectors / (norms + 1e-10)).astype(np.float16)

np.save(os.path.join(STORAGE_DIR, "vectors.npy"), vectors_norm)
with open(os.path.join(STORAGE_DIR, "texts.json"), "w") as f:
    json.dump(all_chunks, f)

print(f"\nDone! Saved {len(all_chunks)} chunks.")
print(f"  vectors.npy: {vectors_norm.nbytes / 1024 / 1024:.1f} MB")
