# KBot — RAG-Powered Intelligent Chatbot

> A Python + Flask chatbot system that uses Retrieval-Augmented Generation (RAG) via LlamaIndex and the OpenAI API to deliver accurate, context-grounded responses from a persistent knowledge base.

---

## Overview

KBot is a full-stack AI chatbot built with a Flask backend and a Next.js frontend. Rather than relying solely on a language model's parametric knowledge, KBot retrieves relevant context from a pre-indexed knowledge base before generating each response — significantly reducing hallucination and improving factual accuracy on domain-specific queries.

The RAG pipeline is powered by **LlamaIndex** for document indexing and semantic retrieval, and **OpenAI** for embedding generation and response synthesis. The index is persisted locally and loaded at query time, making the system lightweight and stateless per request.

**Achieved 80% query accuracy** against domain-specific ground-truth test queries.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        KBot System                          │
│                                                             │
│  ┌──────────────┐     HTTP POST      ┌───────────────────┐  │
│  │  Next.js UI  │ ─────────────────▶ │   Flask Backend   │  │
│  │  (frontend)  │ ◀───────────────── │   app.py          │  │
│  └──────────────┘     JSON response  └────────┬──────────┘  │
│                                               │             │
│                                    ┌──────────▼──────────┐  │
│                                    │   LlamaIndex        │  │
│                                    │   StorageContext     │  │
│                                    │   (KBot Storage/)   │  │
│                                    └──────────┬──────────┘  │
│                                               │             │
│                                    ┌──────────▼──────────┐  │
│                                    │   OpenAI API        │  │
│                                    │   (embeddings +     │  │
│                                    │    LLM generation)  │  │
│                                    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Request flow:**
1. User submits a query via the Next.js frontend
2. Frontend sends a `POST /response` request to the Flask backend
3. Flask loads the persisted LlamaIndex from `KBot Storage/`
4. LlamaIndex embeds the query and retrieves the most relevant context chunks
5. OpenAI generates a grounded response using the retrieved context
6. Response is returned as JSON and displayed in the UI

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, Flask-CORS |
| AI / RAG | LlamaIndex (`llama-index`), OpenAI API |
| Embeddings & LLM | OpenAI (`text-embedding-ada-002`, GPT models) |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Environment | python-dotenv |
| Production server | Gunicorn |

---

## Project Structure

```
KBot/
├── app.py                  # Flask backend — RAG query endpoint
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── KBot Storage/           # Persisted LlamaIndex vector store
│
├── public/                 # Static assets (logos, images)
├── styles/
│   └── globals.css
│
├── node_modules/           # Frontend dependencies
├── package.json            # Frontend configuration
└── ...                     # Next.js app files
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- An OpenAI API key

---

### Backend Setup

```bash
# Clone the repository
cd KBot

# Install Python dependencies
pip install -r requirements.txt

# Create a .env file and add your OpenAI key
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Run the Flask server
python app.py
```

The backend will start at `http://localhost:5000`.

---

### Frontend Setup

```bash
# Install Node dependencies
npm install

# Run the Next.js development server
npm run dev
```

The frontend will start at `http://localhost:3000`.

---

## API Reference

### `POST /response`

Send a query to the chatbot and receive a RAG-grounded response.

**Request body:**
```json
{
  "query": "Your question here"
}
```

**Response:**
```json
{
  "response": "KBot's answer based on retrieved context"
}
```

**Error (missing query):**
```json
{
  "error": "Query is required"
}
```

---

## How the RAG Pipeline Works

KBot uses LlamaIndex's `StorageContext` to load a pre-built vector index from the `KBot Storage/` directory at query time. This avoids rebuilding the index on each request and keeps the API stateless and fast.

```python
# From app.py — the core RAG query logic
storage_context = StorageContext.from_defaults(persist_dir="KBot Storage")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()
response = query_engine.query(query)
```

When a query arrives, LlamaIndex embeds it using OpenAI's embedding model, performs a semantic similarity search over the stored document vectors, retrieves the most relevant chunks, and passes them as context to the OpenAI LLM for grounded response generation.

---

## Research Relevance

Building KBot surfaced several open problems directly relevant to AI safety research:

- **Hallucination vs. grounding**: Without retrieved context, LLM responses were plausible but factually unreliable. With RAG, accuracy improved significantly but the 20% failure cases were the most instructive — they tended to involve partially relevant context that misled the model rather than absent context.
- **Evaluation difficulty**: Measuring 80% accuracy required building informal ground-truth benchmarks. Scaling this to larger or more ambiguous knowledge bases is a core unsolved problem in scalable oversight.
- **Prompt sensitivity**: Small changes to system prompts measurably changed retrieval quality and response faithfulness.
- **Context window trade-offs**: Adjusting chunk size and the number of retrieved chunks produced non-obvious effects on both accuracy and latency.

These observations motivate my interest in empirical AI safety research, particularly around scalable oversight, LLM evaluation methodology, and hallucination detection.

---

## Dependencies

**Python (`requirements.txt`):**
```
flask
flask-cors
python-dotenv
gunicorn
llama-index
openai
pydantic
```

**Frontend:** Next.js, React, TypeScript, Tailwind CSS, Recharts, Radix UI, and standard shadcn/ui component library.

