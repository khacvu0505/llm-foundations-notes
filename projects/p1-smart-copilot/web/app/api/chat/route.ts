export async function POST(request: Request) {
  const backendUrl = process.env.BACKEND_URL
  const appApiKey = process.env.APP_API_KEY

  if (!backendUrl || !appApiKey) {
    throw new Error("Server misconfigured")
  }

  // Option A: pass body through as raw text, FastAPI (Pydantic) validates it
  const body = await request.text()
  // Buổi 12 A4: FastAPI only sees Vercel's outgoing IP (changes per request) → send the user's IP for rate limit.
  // Safe on Vercel: it OVERWRITES x-forwarded-for with the client IP (docs "Request headers"), clients can't fake it.
  // Not safe self-hosted: Next only fills it when missing (`??=` in next/dist/server/base-server.js).
  const clientIp = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim()
  try {
    const upstream = await fetch(`${backendUrl}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": appApiKey,
        ...(clientIp ? { "X-Client-IP": clientIp } : {}),
      },
      body,
      signal: request.signal,
    })
    if (!upstream.ok) {
      const headers = new Headers({ "Content-Type": "application/json" })
      const retryAfter = upstream.headers.get("retry-after")
      if (retryAfter) {
        headers.set("Retry-After", retryAfter)
      }
      // same error shape as the 502 below: { error: string }
      // FastAPI sends { detail: string } (401, 429) or { detail: [...] } (422 validation list)
      const data = await upstream.json().catch(() => null)
      const error = typeof data?.detail === "string" ? data.detail : "Invalid request"
      return Response.json({ error }, { status: upstream.status, headers })
    }
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        // tell reverse proxies (Nginx...) not to buffer the stream — matters after deploy (Buổi 12)
        "X-Accel-Buffering": "no",
      },
    })
  } catch (error) {

    if (request.signal.aborted) {
      // user pressed Stop → nobody is waiting for this response
      return new Response(null, { status: 499 })
    }
    console.error("[api/chat] backend fetch failed:", error)
    return Response.json({ error: "Backend unavailable" }, { status: 502 })
  }
}