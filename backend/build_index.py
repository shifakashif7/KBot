"""
Builds the vector index from:
  1. Scraped website pages  → scraped_data.json  (with URL + title metadata)
  2. PDF / DOCX files       → backend/data/

Output:
  KBot Storage/vectors.npy  — float16 normalized embeddings
  KBot Storage/texts.json   — list of {"text": "...", "url": "...", "title": "..."}

Run:
  python build_index.py
  (delete KBot Storage/ first if you want a full rebuild)
"""

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

client = OpenAI()


def chunk_text(text):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if len(c.strip()) > 50]


def extract_text_from_file(filepath):
    if filepath.lower().endswith(".pdf"):
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif filepath.lower().endswith(".docx"):
        return docx2txt.process(filepath)
    elif filepath.lower().endswith(".txt"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


# ── 1. Load scraped website pages ──────────────────────────────────────────
all_chunks = []  # list of {"text": str, "url": str, "title": str}

scraped_file = os.path.join(BASE_DIR, "scraped_data.json")
if os.path.exists(scraped_file):
    with open(scraped_file, encoding="utf-8") as f:
        pages = json.load(f)
    print(f"Loaded {len(pages)} scraped pages from scraped_data.json")
    for page in pages:
        url = page.get("url", "")
        title = page.get("title", "")
        text = page.get("text", "")
        if not text.strip():
            continue
        for chunk in chunk_text(text):
            all_chunks.append({"text": chunk, "url": url, "title": title})
    print(f"  → {len(all_chunks)} chunks from website")
else:
    print("WARNING: scraped_data.json not found — run scrape_website.py first")

# ── 2. Load PDF / DOCX files from data/ ────────────────────────────────────
data_dir = os.path.join(BASE_DIR, "data")
file_chunks_before = len(all_chunks)

if os.path.exists(data_dir):
    for fname in sorted(os.listdir(data_dir)):
        fpath = os.path.join(data_dir, fname)
        if not os.path.isfile(fpath):
            continue
        text = extract_text_from_file(fpath)
        if not text.strip():
            print(f"  WARNING: no text from {fname}")
            continue
        chunks = chunk_text(text)
        for chunk in chunks:
            all_chunks.append({"text": chunk, "url": "", "title": fname})
        print(f"  {fname}: {len(text):,} chars → {len(chunks)} chunks")
    added = len(all_chunks) - file_chunks_before
    print(f"  → {added} chunks from PDF/DOCX files")
else:
    print("WARNING: data/ directory not found — no PDF/DOCX files loaded")

# ── 3. Embed ────────────────────────────────────────────────────────────────
print(f"\nTotal chunks to embed: {len(all_chunks)}")
print(f"Estimated cost: ~${len(all_chunks) * 0.0000013:.4f}")

texts_only = [c["text"] for c in all_chunks]
all_embeddings = []

for i in range(0, len(texts_only), BATCH_SIZE):
    batch = texts_only[i:i + BATCH_SIZE]
    response = client.embeddings.create(model=EMBED_MODEL, input=batch)
    all_embeddings.extend([item.embedding for item in response.data])
    print(f"  Embedded {min(i + BATCH_SIZE, len(texts_only))}/{len(texts_only)}")

# ── 4. Save ─────────────────────────────────────────────────────────────────
os.makedirs(STORAGE_DIR, exist_ok=True)

vectors = np.array(all_embeddings, dtype=np.float32)
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
vectors_norm = (vectors / (norms + 1e-10)).astype(np.float16)

np.save(os.path.join(STORAGE_DIR, "vectors.npy"), vectors_norm)
with open(os.path.join(STORAGE_DIR, "texts.json"), "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False)

print(f"\nDone! Saved {len(all_chunks)} chunks.")
print(f"  vectors.npy : {vectors_norm.nbytes / 1024 / 1024:.1f} MB")
print(f"  texts.json  : {os.path.getsize(os.path.join(STORAGE_DIR, 'texts.json')) / 1024 / 1024:.1f} MB")
