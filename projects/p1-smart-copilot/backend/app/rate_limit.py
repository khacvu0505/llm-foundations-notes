import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

LIMIT = 5
WINDOW_S = 60
_hits: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(req: Request) -> None:
  ip = req.client.host if req.client else "unknown"
  now = time.monotonic()
  hits = _hits[ip]
  while hits and hits[0] <= now - WINDOW_S:
    hits.popleft()
  if len(hits) >= LIMIT:
    raise HTTPException(
      status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(WINDOW_S)}
    )
  hits.append(now)
