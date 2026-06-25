import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { query, history } = body;

  if (!query) {
    return NextResponse.json({ error: "Query is required" }, { status: 400 });
  }

  const backendUrl = process.env.BACKEND_URL ?? "http://localhost:5000";

  const flaskRes = await fetch(`${backendUrl}/response`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, history: history ?? [] }),
  });

  if (!flaskRes.ok) {
    return NextResponse.json(
      { error: "Backend error", status: flaskRes.status },
      { status: flaskRes.status }
    );
  }

  return new Response(flaskRes.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
    },
  });
}
