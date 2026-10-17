import asyncio
import json
import os
import secrets
from collections.abc import AsyncIterator
from typing import Annotated, Any

import openai
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()
load_dotenv()  # load .env vào os.environ

origins = [
  "http://localhost:3000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_methods=["GET", "POST"],
  allow_headers=["content-type", "x-api-key"],
)

# Buổi 9 — SSE Streaming end-to-end (backend ở file này, frontend Next.js ở web/, ghi ở notes.md)
#
# Luật chơi: tự viết code dưới mỗi đề bài, tra docs chính thức khi cần:
#   https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
#   https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
#     (mục "Event stream format": data / event / id / retry, dòng trống kết thúc 1 event)
#   https://developers.openai.com/api/docs/guides/streaming-responses
#     (stream=True, các loại event)
# Import cần gì tự thêm ở đầu file.
#
# Chuẩn bị: làm mục "Setup (tự làm)" trong notes.md trước
#   (chép code từ session08, tạo app Next.js ở web/).
#
# Chạy server:  uv run fastapi dev weeks/week02/session09/exercises.py
# Xem stream:   curl -N http://127.0.0.1:8000/stream/fake
#               -N = tắt buffer của curl, thấy từng event hiện ra ngay
#               (bỏ -N là thấy cả cục ở cuối)
# Frontend:     cd weeks/week02/session09/web && pnpm dev   → http://localhost:3000
# Test:         uv run pytest weeks/week02/session09
# Vệ sinh:      uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Nhắc lại từ các buổi trước:
#   - Stream OpenAI (Buổi 4): stream=True, event response.output_text.delta (có .delta) và
#     response.completed (có .response.usage). Bỏ flush=True thì text đợi "\n" mới hiện (buffer).
#   - async def + client sync = chặn event loop (Buổi 8 bài 3). Generator stream cũng vậy.
#   - X-API-Key qua Depends, CORS chỉ cho http://localhost:3000, allow_headers có x-api-key
#     (Buổi 8 bài 4, 5).
#   - Lỗi OpenAI: bắt openai.APIError, log chi tiết ra terminal, client chỉ nhận câu gọn
#     (Buổi 7, Buổi 8).
#   - Mỗi buổi 1 file độc lập: CHÉP code cần dùng từ session08, không import chéo.
#
# Ý tưởng chính (so với TS / Node):
#   Node:     res.setHeader("Content-Type", "text/event-stream")
#             res.write(`data: ${x}\n\n`) ... res.end()
#   FastAPI:  return StreamingResponse(<async generator>, media_type="text/event-stream")
#             Mỗi lần generator `yield` 1 chuỗi = 1 lần res.write(...). Hết generator = res.end().
#   Generator (~ async function* bên JS): hàm có `yield` → gọi ra chưa chạy, ai lặp thì mới chạy.
#   Khác lớn nhất so với response thường: status code + header gửi đi NGAY lúc bắt đầu stream.
#   Lỗi xảy ra giữa chừng thì không đổi được sang 502 nữa (Bài 3).
#
# Hướng tới: Buổi 10–11 (Project #1) = endpoint chat của bài này + tools (Buổi 7)
#   + cost log + rate limit.


# ============================================================================
# Bài 1 — SSE bằng tay: stream token giả, chưa gọi OpenAI
# ============================================================================
#
# Yêu cầu:
#   - Chép từ session08: app FastAPI, /health, CORSMiddleware (origin http://localhost:3000).
#   - GET /stream/fake: async generator yield lần lượt từng chữ của 1 câu cố định
#     (vd "Xin chào, mình là bot giả lập."), mỗi chữ cách nhau 0.2s (await asyncio.sleep).
#     Mỗi chữ gửi theo đúng format SSE: "data: <chữ>\n\n". Cuối cùng gửi "data: [DONE]\n\n".
#   - Trả StreamingResponse với media_type="text/event-stream".
#   - Thử bằng curl -N và curl (không -N): khác nhau thế nào?
#   - Thử 3 kiểu sai, mỗi lần sửa 1 chỗ, quan sát bằng curl -N:
#       a) bỏ 1 "\n" (chỉ "data: x\n") → client SSE còn tách được event không?
#          (xem lại khi làm Bài 4)
#       b) token có xuống dòng (vd "dòng 1\ndòng 2") → format SSE vỡ thế nào? Sửa ra sao?
#          (gợi ý: json.dumps từng event, phía client JSON.parse)
#       c) đổi sang `def` + time.sleep(0.2) trong generator → bench kiểu Buổi 8 bắn 3 request
#          song song vào /stream/fake. Có giống /slow/async-block không?
#
# Gợi ý:
#   - Async generator: `async def gen(): ... yield "data: ...\n\n"`.
#     Truyền gen() (đã gọi, chưa await) vào StreamingResponse.
#   - Header nên có "Cache-Control: no-cache" (đừng cache stream).
#     Tra tham số headers= của StreamingResponse.
#
# Câu hỏi ghi notes.md: 1 event SSE gồm những gì, kết thúc bằng gì? Vì sao curl cần -N?
#   StreamingResponse khác return dict ở chỗ nào (status code, header gửi lúc nào)?


# TODO: viết code ở đây
@app.get("/health")
def health() -> dict[str, str]:
  return {"status": "ok"}


async def fake_tokens() -> AsyncIterator[str]:
  # token "chào\nbạn" có xuống dòng → json.dumps giữ event trên 1 dòng (Bài 1b')
  tokens = ["Xin", "chào\nbạn", "nhé"]
  for word in tokens:
    yield f"data: {json.dumps(word, ensure_ascii=False)}\n\n"
    await asyncio.sleep(0.2)

  yield "data: [DONE]\n\n"


@app.get("/stream/fake")
def stream_fake() -> StreamingResponse:
  return StreamingResponse(
    fake_tokens(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
  )


# ============================================================================
# Bài 2 — Stream câu trả lời thật từ OpenAI: POST /chat/stream
# ============================================================================
#
# Yêu cầu:
#   - Chép từ session08: ChatRequest, verify_api_key, get_openai_client, PRICES, cost_usd, MODEL.
#   - POST /chat/stream (có X-API-Key qua Depends, body ChatRequest):
#       gọi client.responses.create(..., stream=True) với AsyncOpenAI,
#       lặp `async for event in stream`.
#   - Gửi 2 loại event SSE, data là JSON:
#       event: delta   data: {"text": "<mảnh chữ>"}
#                      ← mỗi event response.output_text.delta của SDK
#       event: done    data: {"input_tokens": ..., "output_tokens": ..., "cost_usd": ...}
#                      ← lấy từ event response.completed
#   - Đo bằng curl -N: TTFT (thời gian tới event delta đầu tiên) vs tổng thời gian.
#     So với POST /chat không stream (Buổi 8, chép sang nếu muốn so).
#   - Câu dài (vd "Giải thích transformer trong 5 câu") để thấy rõ chữ chảy ra.
#
# Gợi ý:
#   - Format có tên event: "event: delta\ndata: {...}\n\n"
#     (dòng event trước, dòng data sau, dòng trống kết thúc).
#   - Event của SDK có nhiều loại; chỉ lấy 2 loại trên, bỏ qua phần còn lại (nhớ Buổi 4).
#   - json.dumps(..., ensure_ascii=False) để tiếng Việt giữ nguyên
#     (mặc định "ạ" bị đổi thành \u1ea1).
#   - Viết hàm nhỏ format_sse(event: str, data: dict) -> str dùng chung cho mọi bài.
#
# Câu hỏi ghi notes.md: TTFT vs tổng thời gian, user cảm thấy khác gì so với /chat không stream?
#   Usage / cost có từ lúc nào trong stream (đầu hay cuối)? Vì sao?

# TODO: viết code ở đây
PRICES: dict[str, tuple[float, float]] = {
  "gpt-4.1-nano": (0.10, 0.40),
  "gpt-4o-mini": (0.15, 0.60),
  "gpt-6-luna": (0.10, 0.50),
}


def cost_usd(
  input_tokens: int,
  output_tokens: int,
  price_in_per_mtok: float,
  price_out_per_mtok: float,
) -> float:
  return (input_tokens / 1_000_000) * price_in_per_mtok + (
    output_tokens / 1_000_000
  ) * price_out_per_mtok


# client = OpenAI()
client = AsyncOpenAI()
MODEL = "gpt-6-luna"
# MODEL = "gpt-khong-ton-tai"


class ChatRequest(BaseModel):
  model_config = ConfigDict(extra="forbid")
  message: str = Field(description="The user's message", max_length=500, min_length=1)


def verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
  expected = os.getenv("APP_API_KEY")
  if expected is None:
    raise HTTPException(status_code=500, detail="Server misconfigured")

  if x_api_key is None:
    raise HTTPException(status_code=401, detail="Missing API Key")

  if not secrets.compare_digest(expected, x_api_key):
    raise HTTPException(status_code=401, detail="Invalid API Key")


def get_openai_client() -> AsyncOpenAI:
  return client


def format_sse(event: str, data: dict[str, Any]) -> str:
  return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def chat_events(openai_client: AsyncOpenAI, message: str) -> AsyncIterator[str]:
  count = 0

  try:
    stream = await openai_client.responses.create(
      model=MODEL,
      input=message,
      instructions="Trả lời ngắn gọn, bằng tiếng Việt.",
      stream=True,
      max_output_tokens=300,
    )
    async with stream:
      async for event in stream:
        if event.type == "response.output_text.delta":
          yield format_sse("delta", {"content": event.delta})
          count += 1
          # if count == 3:
          #     raise RuntimeError("Fake error")
        # incomplete: chạm max_output_tokens (model reasoning tính cả token "nghĩ")
        # pyright chỉ thu hẹp union qua ==, không qua `in (...)` → viết 2 vế or
        elif event.type == "response.completed" or event.type == "response.incomplete":
          incomplete = event.type == "response.incomplete"
          usage = event.response.usage
          if usage is None:
            yield format_sse(
              "done",
              {
                "input_tokens": None,
                "output_tokens": None,
                "cost_usd": None,
                "incomplete": incomplete,
              },
            )
          else:
            yield format_sse(
              "done",
              {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cost_usd": cost_usd(
                  usage.input_tokens,
                  usage.output_tokens,
                  *PRICES[MODEL],
                ),
                "incomplete": incomplete,
              },
            )
  except asyncio.CancelledError:
    print(f"[stream cancelled] sau {count} delta")
    raise
  except (openai.APIError, RuntimeError) as e:
    print(f"[stream error] {type(e).__name__} | model={MODEL} | {e}")
    yield format_sse("error", {"message": "Có lỗi khi tạo câu trả lời, thử lại sau"})
  finally:
    print(f"[stream closed] đã gửi {count} delta")


@app.post("/chat/stream", dependencies=[Depends(verify_api_key)])
def chat_stream(
  body: ChatRequest, openai_client: Annotated[AsyncOpenAI, Depends(get_openai_client)]
) -> StreamingResponse:
  return StreamingResponse(
    chat_events(openai_client, body.message),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache"},
  )


# ============================================================================
# Bài 3 — Lỗi giữa stream + client ngắt kết nối
# ============================================================================
#
# Phần A — lỗi:
#   - Tạm đổi MODEL thành tên sai, gọi /chat/stream. Client nhận mã gì?
#     Có giống 502 của Buổi 8 không?
#   - Giả lập lỗi SAU khi đã gửi vài delta (vd raise sau delta thứ 5).
#     Status code lúc này là gì, còn đổi được không? Client thấy gì (curl -N)?
#   - Sửa: bắt lỗi trong generator → gửi event: error, data: {"message": "<câu gọn>"},
#     rồi kết thúc stream. Log chi tiết ra terminal như Buổi 8.
#   - Phân biệt: lỗi TRƯỚC khi stream bắt đầu (còn trả 502 được)
#     vs lỗi GIỮA stream (chỉ còn cách gửi event error).
#
# Phần B — client bỏ đi giữa chừng:
#   - Gọi /chat/stream bằng curl -N với câu dài, Ctrl+C sau 1–2 giây.
#     Terminal server: generator có dừng không? Lời gọi OpenAI có dừng không (còn tốn token không)?
#   - Log ra terminal khi client ngắt
#     (gợi ý: asyncio.CancelledError, hoặc request.is_disconnected()).
#     Nhớ: bắt CancelledError thì log xong phải raise lại (Buổi 8: không nuốt tín hiệu dừng).
#
# Câu hỏi ghi notes.md: "Tool call / OpenAI fail giữa stream xử lý sao?" (exit criteria Phase 01).
#   Client ngắt thì server có tự dừng gọi OpenAI không, vì sao quan trọng với chi phí?

# TODO: viết code ở đây


# ============================================================================
# Bài 4 — Next.js đọc stream: fetch + ReadableStream (code ở web/, không ở file này)
# ============================================================================
#
# Yêu cầu (trong web/, Client Component, vd app/page.tsx với "use client"):
#   - Ô nhập + nút Gửi. fetch POST http://127.0.0.1:8000/chat/stream,
#     header Content-Type + X-API-Key.
#   - Đọc res.body.getReader() + TextDecoder, ghép buffer, tách event theo "\n\n",
#     parse "event:" / "data:":
#       delta → nối chữ vào state; done → hiện token + cost; error → hiện lỗi.
#   - Thử: chữ có hiện dần không? DevTools → Network → request /chat/stream
#     → tab Response / EventStream.
#   - Thử lại lỗi Bài 1a (bỏ 1 "\n") với client này: chuyện gì xảy ra?
#   - Nút "Dừng": AbortController → fetch bị huỷ. Terminal server có log ngắt như Bài 3B không?
#
# Gợi ý:
#   - Vì sao không dùng EventSource (API SSE có sẵn của trình duyệt)?
#     Tra: EventSource gửi được method nào, có gửi header tuỳ ý (X-API-Key) được không?
#   - 1 lần read() không đảm bảo = 1 event: có thể nhận nửa event, hoặc 3 event dính nhau
#     → cần buffer.
#   - Key trong code frontend: chỉ để học local (NEXT_PUBLIC_... trong web/.env.local).
#     Mọi biến NEXT_PUBLIC_ đều lộ cho người dùng (xem được trong DevTools).
#     Ghi lại cách làm đúng ở notes (Bài 5).
#   - CORS: request từ localhost:3000 có header x-api-key → preflight OPTIONS (Buổi 8 bài 5).
#
# Câu hỏi ghi notes.md: vì sao phải tự tách event bằng buffer? So với res.json() bên fetch thường?

# (code ở web/app/page.tsx)


# ============================================================================
# Bài 5 — Test + SSE vs WebSocket
# ============================================================================
#
# Phần A — test (test_exercises.py cùng thư mục, tự tạo):
#   - TestClient: /stream/fake trả content-type text/event-stream, có đủ event + "[DONE]".
#   - /chat/stream thiếu X-API-Key → 401 (trước khi stream bắt đầu).
#   - (Tuỳ chọn) /chat/stream với client OpenAI GIẢ qua app.dependency_overrides[get_openai_client]:
#     client giả trả vài event delta + 1 event completed → kiểm thứ tự event delta... done.
#     (Đây là lúc Depends ở Buổi 8 có tác dụng thật.)
#
# Phần B — lý thuyết (notes.md), không code:
#   - SSE vs WebSocket vs long polling: chiều dữ liệu, giao thức, tự kết nối lại,
#     qua proxy / CDN, độ phức tạp server. Vì sao chat LLM chọn SSE?
#   - Key ở frontend: NEXT_PUBLIC_ lộ key → cách đúng là Next.js Route Handler (chạy ở server)
#     gọi FastAPI và chuyển tiếp stream, key chỉ nằm ở server. (Buổi 10–11 làm thật.)
#
# Câu hỏi ghi notes.md: điền bảng SSE vs WebSocket, 3 câu phỏng vấn cuối file notes.

# TODO: viết code ở đây
