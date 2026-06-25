import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const query = req.nextUrl.searchParams.get("query");
  if (!query) {
    return NextResponse.json({ error: "Query is required" }, { status: 400 });
  }

  const flaskRes = await fetch("http://localhost:5000/response", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!flaskRes.ok) {
    return NextResponse.json(
      { error: "Backend error", status: flaskRes.status },
      { status: flaskRes.status }
    );
  }

  const data = await flaskRes.json();
  return NextResponse.json(data);
}
