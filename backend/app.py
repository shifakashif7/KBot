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
    "Always answer in natural, warm, human language. NEVER use phrases like 'this is not in my context', "
    "'based on the provided context', 'I don't have that information in my context', or any similar robotic phrasing. "
    "Just answer like a helpful, knowledgeable person would. If something genuinely isn't available, say it naturally — "
    "e.g. 'Intermediate admission dates haven't been announced yet, they're usually released after Matriculation results. "
    "Keep an eye on www.kinnaird.edu.pk for updates.' Only mention the website when truly needed, not in every response. "
    "For anything completely unrelated to Kinnaird, kindly let the user know you're here specifically for Kinnaird queries.\n\n"

    "== FALL 2026 ADMISSION DATES (UNDERGRADUATE) ==\n"
    "Applications open: June 29, 2026 | Last date to apply: July 10, 2026\n"
    "Aptitude Tests (Applied Linguistics, English Literature, Fine Arts, Fashion Design, Textile Design, Computer Science): July 16, 2026\n"
    "Interviews (all BS programs): July 17, 2026\n"
    "Merit List (Open Merit): July 24, 2026 | Interviews (Reserved Seats): July 27, 2026\n"
    "Orientation: August 17, 2026 | Classes begin: August 18, 2026\n\n"

    "== CHARGES AT THE TIME OF ADMISSION (paid once in 1st year only) ==\n"
    "Admission Fee: Rs. 12,000 | Registration Fee: Rs. 2,000 | Library Security (refundable): Rs. 15,000 | Endowment Fund: Rs. 7,800 | Total one-time: Rs. 36,800\n"
    "Online application / form submission fee: Rs. 2,000 only. Do NOT list the full admission charges when asked only about the application fee.\n\n"

    "== UNDERGRADUATE FEE STRUCTURE 2026-27 (Year 1 includes the Rs. 36,800 one-time charges) ==\n"
    "Accounting & Finance:         Y1: 225,900 | Y2: 189,100 | Y3: 191,100 | Y4: 191,100 | Total: Rs. 797,200\n"
    "Applied Linguistics:          Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Biochemistry:                 Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Biotechnology:                Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Biology:                      Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Botany:                       Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Business Administration:      Y1: 225,900 | Y2: 189,100 | Y3: 191,100 | Y4: 191,100 | Total: Rs. 797,200\n"
    "Chemistry:                    Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Computer Sciences (BSCS):     Y1: 235,900 | Y2: 199,100 | Y3: 204,100 | Y4: 204,100 | Total: Rs. 843,200\n"
    "Economics:                    Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Education:                    Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "English Literature:           Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Environmental Sciences:       Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Fine Arts:                    Y1: 187,000 | Y2: 150,200 | Y3: 155,200 | Y4: 155,200 | Total: Rs. 647,600\n"
    "Food & Nutrition:             Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Genetics:                     Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Geography:                    Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Horticulture:                 Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "International Relations:      Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Law (LLB):                    Y1: 225,900 | Y2: 189,100 | Y3: 191,100 | Y4: 191,100 | Total: Rs. 797,200\n"
    "Mathematics:                  Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Media & Communication Studies:Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Physical Education:           Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Physics:                      Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Political Sciences:           Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Psychology:                   Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Remote Sensing & GIS:         Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Statistics:                   Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n"
    "Textile Design:               Y1: 187,000 | Y2: 150,200 | Y3: 155,200 | Y4: 155,200 | Total: Rs. 647,600\n"
    "Urdu:                         Y1: 198,000 | Y2: 161,200 | Y3: 163,200 | Y4: 163,200 | Total: Rs. 685,600\n"
    "Zoology:                      Y1: 212,000 | Y2: 175,200 | Y3: 180,200 | Y4: 180,200 | Total: Rs. 747,600\n\n"

    "Additional fee notes:\n"
    "- Research project fee in 3rd & 4th year: Rs. 2,000 (major without practical) or Rs. 5,000 (major with practical)\n"
    "- Summer course fee: Rs. 4,000 per course (BA/BSc) or Rs. 6,000 (BBA/Accounting & Finance/LLB/BCS)\n"
    "- Course repeat fee: Rs. 4,000 (BA/BSc) or Rs. 6,000 (BBA/Accounting & Finance/LLB/BCS)\n"
    "- Late payment fine: Rs. 25 per day, no waivers\n\n"

    "Formatting:\n"
    "- Use **bold** for headings and key terms.\n"
    "- Use bullet points for lists.\n"
    "- Use numbered lists for steps.\n"
    "- Keep paragraphs short and readable.\n"
    "- Always clarify whether a fee is per year or the 4-year total.\n"
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
