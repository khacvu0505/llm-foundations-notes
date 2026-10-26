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
  # TẠM — Buổi 12 A4 bước 1 (Claude viết theo yêu cầu, 2026-10-26): đo IP backend thấy sau Vercel.
  # Xoá khi sửa xong. hits = số lượt đã dùng trong 60s TRƯỚC request này
  # → 2 máy mà cùng 1 ip thì số này cộng dồn
  print(f"[rate_limit] ip={ip} xff={req.headers.get('x-forwarded-for')} hits={len(hits)}")
  if len(hits) >= LIMIT:
    raise HTTPException(
      status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(WINDOW_S)}
    )
  hits.append(now)
