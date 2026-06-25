from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
from openai import OpenAI as OpenAIClient
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")

storage_context = StorageContext.from_defaults(persist_dir=os.path.join(BASE_DIR, "KBot Storage"))
index = load_index_from_storage(storage_context)
retriever = index.as_retriever(similarity_top_k=4)
openai_client = OpenAIClient()

SYSTEM_PROMPT = (
    "You are KBot, an official AI assistant for Kinnaird College for Women University, Lahore, Pakistan. "
    "You ONLY answer questions about Kinnaird College. If asked about any other institution or unrelated topic, "
    "politely decline and remind the user you can only assist with Kinnaird College queries.\n\n"
    "Important: Your knowledge is based on Kinnaird College documents and website content. "
    "Some information such as admission dates and fee structures may be from a previous academic year. "
    "Always advise users to verify current dates and fees from the official website: www.kinnaird.edu.pk.\n\n"
    "Formatting rules:\n"
    "- Use **bold** for headings, labels, and important terms.\n"
    "- Use bullet points (- item) for listing multiple items, options, or requirements.\n"
    "- Use numbered lists for steps or ranked information.\n"
    "- Break answers into short paragraphs — never write a wall of text.\n"
    "- For fees, always clarify whether the amount is per year, per semester, or total for the full program.\n"
    "- End with a friendly line offering further help.\n"
    "- If information is not available, say so honestly rather than guessing."
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
    nodes = retriever.retrieve(query)
    context = "\n\n".join([n.get_content() for n in nodes])
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
