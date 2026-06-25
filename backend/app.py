from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from openai import OpenAI as OpenAIClient
import json
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

STORAGE_DIR = os.path.join(BASE_DIR, "KBot Storage")

print("Loading index...")
vectors = np.load(os.path.join(STORAGE_DIR, "vectors.npy"))
with open(os.path.join(STORAGE_DIR, "texts.json")) as f:
    texts = json.load(f)
print(f"Loaded {len(texts)} nodes.")

openai_client = OpenAIClient()

SYSTEM_PROMPT = (
    "You are KBot, a friendly and knowledgeable AI assistant for Kinnaird College for Women University, Lahore, Pakistan. "
    "You help prospective students, current students, and parents with questions about Kinnaird College.\n\n"
    "You are provided with relevant excerpts from official Kinnaird College documents. Use this information to give confident, "
    "direct answers. Never say things like 'it's not in my context' or 'I don't have that information in my context' — "
    "instead, answer naturally as a helpful assistant would.\n\n"
    "Guidelines:\n"
    "- Answer directly from the provided document excerpts. If the answer is there, give it confidently.\n"
    "- If a question is about something not covered in the documents (e.g. very specific real-time info), "
    "naturally suggest visiting www.kinnaird.edu.pk or contacting the admissions office — but keep it brief and don't repeat it every response.\n"
    "- For questions completely unrelated to Kinnaird College, politely let the user know you're specialized for Kinnaird only.\n"
    "- NEVER fabricate specific dates, fees, or figures. Only state numbers that explicitly appear in the provided context.\n"
    "- Fee question rules:\n"
    "  * 'Online application fee' or 'form submission fee' = Rs. 2,000 (Registration Fee only). Do NOT list the full admission charges for this.\n"
    "  * When giving annual fees for a program, always state the TOTAL (tuition + funds + practical fee if any), not just tuition.\n"
    "  * For BSCS: annual fee = Rs. 235,900 (Tuition Rs. 181,000 + Funds Rs. 44,900 + Practical Fee Rs. 10,000). Do NOT say Rs. 225,900 — that is for BBA/LLB.\n"
    "  * 1st year one-time additional charges (paid only once at admission): Admission Fee Rs. 12,000 + Registration Fee Rs. 2,000 + Library Security Rs. 15,000 (refundable) + Endowment Fund Rs. 7,800 = Rs. 36,800 total.\n"
    "  * Always mention these 1st year additional charges when answering any fee question for a program.\n"
    "  * For a 4-year BS program: total = (annual fee × 4) + Rs. 36,800 one-time charges. Calculate and state this total.\n"
    "- Admission dates for Fall 2026 undergraduate programs: applications open June 29, 2026 and the last date to apply is July 10, 2026. Always give both the start and end date when asked.\n"
    "- If asked about something not covered in the context (e.g. intermediate admission dates, a program not mentioned), "
    "respond naturally — for example: 'Intermediate admission dates haven't been announced yet. They are typically released after Matriculation results — stay tuned to www.kinnaird.edu.pk for updates.' "
    "Adapt this style to whatever is missing, rather than guessing or making up information.\n\n"
    "Formatting:\n"
    "- Use **bold** for headings and key terms.\n"
    "- Use bullet points for lists of items or requirements.\n"
    "- Use numbered lists for steps or sequences.\n"
    "- Keep paragraphs short and readable.\n"
    "- For fees, always mention whether the amount is per year, per semester, or total program cost.\n"
    "- End responses with a warm, helpful closing line."
)

app = Flask(__name__)
CORS(app, resources={r"/response": {"origins": [
    "https://kbot-portal.vercel.app",
    "https://kinnaird.edu.pk",
    "https://www.kinnaird.edu.pk",
    "http://localhost:3000",
]}})

limiter = Limiter(get_remote_address, app=app, default_limits=["30 per minute", "200 per day"])
MAX_QUERY_LENGTH = 1000


def retrieve(query, top_k=10):
    resp = openai_client.embeddings.create(model="text-embedding-3-large", input=query)
    qv = np.array(resp.data[0].embedding, dtype=np.float16)
    qv = qv / (np.linalg.norm(qv) + 1e-10)
    scores = vectors @ qv
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [texts[i] for i in top_indices]


@app.route('/')
def home():
    return 'Hello from Flask!'


@app.route('/response', methods=['POST'])
@limiter.limit("10 per minute")
def get_response():
    data = request.json
    query = data.get("query", "")
    history = data.get("history", [])
    if not query:
        return jsonify({"error": "Query is required"}), 400
    if len(query) > MAX_QUERY_LENGTH:
        return jsonify({"error": f"Query too long. Max {MAX_QUERY_LENGTH} characters."}), 400

    context_chunks = retrieve(query)
    context = "\n\n".join(context_chunks)

    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext from Kinnaird College documents:\n{context}"}]
    for msg in history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    def generate():
        stream = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, stream=True)
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == '__main__':
    app.run(debug=False)
