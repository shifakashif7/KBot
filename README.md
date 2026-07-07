# KBot — RAG-Powered Chatbot for Kinnaird College

> An AI assistant for Kinnaird College for Women University, Lahore. Built with a Flask backend (Railway) and a Next.js frontend (Vercel), using custom numpy-based vector retrieval and OpenAI for embeddings and response generation.

---

## Overview

KBot answers queries from prospective and current students about admissions, fee structure, program eligibility, and general college information. It uses Retrieval-Augmented Generation (RAG) — before generating a response, it retrieves the most relevant chunks from indexed college documents so answers are grounded in real data rather than guesswork.

The vector index is built from PDF and DOCX documents using `build_index.py`, stored as a compact `vectors.npy` (float16) + `texts.json` file pair, and hosted on GitHub Releases. The Railway container downloads it at startup via `start.sh`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          KBot System                            │
│                                                                 │
│  ┌──────────────────┐   SSE stream    ┌─────────────────────┐  │
│  │  Next.js UI      │ ──────────────▶ │   Flask Backend     │  │
│  │  (Vercel)        │ ◀────────────── │   (Railway)         │  │
│  └──────────────────┘  token-by-token └──────────┬──────────┘  │
│                                                  │             │
│                                       ┌──────────▼──────────┐  │
│                                       │  Numpy Retrieval    │  │
│                                       │  vectors.npy        │  │
│                                       │  texts.json         │  │
│                                       └──────────┬──────────┘  │
│                                                  │             │
│                                       ┌──────────▼──────────┐  │
│                                       │   OpenAI API        │  │
│                                       │  text-embedding-    │  │
│                                       │  3-large + gpt-4o-  │  │
│                                       │  mini (streaming)   │  │
│                                       └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Request flow:**
1. User submits a query in the Next.js chat UI
2. Frontend POSTs to `/api/response` (Next.js API route), forwarded to Railway
3. Flask embeds the query using `text-embedding-3-large`
4. Cosine similarity search over `vectors.npy` retrieves top-10 relevant chunks
5. Retrieved context + conversation history is sent to `gpt-4o-mini` with streaming
6. Tokens stream back as Server-Sent Events (SSE) and appear in the UI in real time

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask, Flask-CORS, Flask-Limiter |
| Vector Retrieval | NumPy (float16 vectors, cosine similarity) |
| Embeddings | OpenAI `text-embedding-3-large` |
| LLM | OpenAI `gpt-4o-mini` (streaming) |
| Index Building | pypdf, docx2txt |
| Frontend | Next.js 16 (App Router), React, TypeScript, Tailwind CSS |
| UI Components | Radix UI, shadcn/ui, Framer Motion, ReactMarkdown |
| Production server | Gunicorn |
| Backend hosting | Railway |
| Frontend hosting | Vercel |

---

## Project Structure

```
KBot/
├── backend/
│   ├── app.py                  # Flask backend — RAG query endpoint (SSE streaming)
│   ├── build_index.py          # Builds vectors.npy + texts.json from source documents
│   ├── start.sh                # Railway startup script — downloads index, runs gunicorn
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # OPENAI_API_KEY (not committed)
│   ├── data/                   # Source PDFs and DOCX files for indexing
│   └── KBot Storage/           # Generated index files (vectors.npy + texts.json)
│
└── portal/
    ├── app/
    │   ├── page.tsx             # Welcome / landing page
    │   ├── chat/page.tsx        # Chat interface
    │   └── api/response/route.ts  # Next.js API route — proxies to Railway backend
    ├── components/
    │   ├── chat-screen.tsx      # Main chat UI with SSE streaming
    │   ├── top-bar.tsx          # Navigation bar
    │   └── loading-dots.tsx     # Typing indicator
    ├── public/                  # Static assets (logos, bot image)
    ├── next.config.ts           # CSP headers for iframe embedding
    └── package.json
```

---

## Local Development

### Prerequisites

- Python 3.9+
- Node.js 18+
- An OpenAI API key

### Backend

```bash
cd KBot/backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI key
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the Flask dev server
python app.py
```

Backend runs at `http://localhost:5000`.

### Frontend

```bash
cd KBot/portal

# Install dependencies
npm install

# Point the frontend to the local backend
echo "BACKEND_URL=http://localhost:5000" > .env.local

# Start the dev server
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## Building the Vector Index

The index must be rebuilt any time source documents change.

```bash
cd KBot/backend
source venv/bin/activate

# Place PDFs and DOCX files in backend/data/
# Then run:
python build_index.py
```

This produces:
- `KBot Storage/vectors.npy` — float16 normalized embeddings (~1.2 MB)
- `KBot Storage/texts.json` — the corresponding text chunks (~10 MB)

To deploy the new index, compress it and upload to GitHub Releases:

```bash
cd backend
tar -czf kbot_storage.tar.gz "KBot Storage/"
```

Upload `kbot_storage.tar.gz` to your GitHub Release. Update the download URL in `start.sh` if the release tag changed.

---

## Deploying the Backend to Railway

### First-time setup

1. **Install the Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Link or create a project**
   ```bash
   cd KBot/backend
   railway init          # Creates a new Railway project
   # OR
   railway link          # Links to an existing project
   ```

4. **Set the OpenAI API key as an environment variable**

   In the Railway dashboard → your project → Variables, add:
   ```
   OPENAI_API_KEY=sk-...
   ```

5. **Deploy**
   ```bash
   railway up
   ```

   Railway will detect `start.sh` (set as the start command) and run it. `start.sh` downloads the index from GitHub Releases and then starts gunicorn.

### Re-deploying after changes

```bash
cd KBot/backend
railway up
```

Or push to your connected GitHub branch — Railway auto-deploys on push if the repo is connected in the Railway dashboard.

### Getting your Railway backend URL

In the Railway dashboard, go to your service → Settings → Networking → Generate a public domain. The URL will look like `https://your-project.up.railway.app`. You'll need this for the Vercel setup.

---

## Deploying the Frontend to Vercel

### First-time setup

1. **Install the Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd KBot/portal
   vercel --prod
   ```

   Follow the prompts to link or create a Vercel project.

4. **Set the backend URL as an environment variable**

   In the Vercel dashboard → your project → Settings → Environment Variables, add:
   ```
   BACKEND_URL=https://your-project.up.railway.app
   ```

   Then redeploy:
   ```bash
   vercel --prod
   ```

### Re-deploying after changes

```bash
cd KBot/portal
vercel --prod
```

### Embedding the chat in a website (WordPress snippet)

The chat page at `https://your-vercel-app.vercel.app/chat` is embeddable as an iframe. It includes a `frame-ancestors` CSP header allowing embedding from `kinnaird.edu.pk`. Use the widget HTML snippet to add a floating chat button to any webpage.

---

## API Reference

### `POST /response`

Streams a RAG-grounded response as Server-Sent Events.

**Request body:**
```json
{
  "query": "What is the fee for Computer Science?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

**SSE stream output:**
```
data: {"token": "The"}
data: {"token": " fee"}
data: {"token": " for"}
...
data: [DONE]
```

**Rate limit:** 10 requests/minute per IP.  
**Max query length:** 1000 characters.

---

## Environment Variables

| Variable | Where | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | Railway (backend) | Your OpenAI secret key |
| `BACKEND_URL` | Vercel (frontend) | Full URL of the Railway backend, e.g. `https://xyz.up.railway.app` |

---

## Knowledge Base

The bot's knowledge comes from two sources:

1. **Vector index** — PDFs and DOCX files in `backend/data/` indexed by `build_index.py`. Contains the Kinnaird Admission Handbook and other college documents. Top-10 chunks are retrieved per query.

2. **System prompt** — Key facts injected directly for reliability: full fee table for all 30 programs, admission dates, intermediate closing merit (2025), intermediate stream subjects, and program-specific eligibility requirements.

---

## Author

**Shifa Kashif**  
BSCS '24, Kinnaird College for Women University  
**Linkedin**  
www.linkedin.com/in/shifa-kashif


