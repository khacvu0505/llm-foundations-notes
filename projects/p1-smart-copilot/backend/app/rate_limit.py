import ipaddress
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

LIMIT = 5
WINDOW_S = 60
_hits: dict[str, deque[float]] = defaultdict(deque)


def client_ip(req: Request) -> str:
  # Buổi 12 A4 (Claude viết theo yêu cầu, 2026-10-26): sau Vercel, req.client.host = IP đi ra của
  # Vercel (đổi theo request) → đếm theo X-Client-IP do route.ts gửi (IP thật của user).
  # Tin được vì verify_api_key chạy TRƯỚC rate_limit (main.py) → chỉ ai có APP_API_KEY mới tới đây.
  # Thiếu header / không đúng dạng IP → về IP kết nối như cũ (local, test).
  header = req.headers.get("x-client-ip")
  if header:
    try:
      # str(...) chuẩn hoá: 1 IP viết 2 kiểu (IPv6 rút gọn / đầy đủ) vẫn chung 1 bộ đếm
      return str(ipaddress.ip_address(header.strip()))
    except ValueError:
      pass
  return req.client.host if req.client else "unknown"


def rate_limit(req: Request) -> None:
  ip = client_ip(req)
  now = time.monotonic()
  hits = _hits[ip]
  while hits and hits[0] <= now - WINDOW_S:
    hits.popleft()
  if len(hits) >= LIMIT:
    raise HTTPException(
      status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(WINDOW_S)}
    )
  hits.append(now)
