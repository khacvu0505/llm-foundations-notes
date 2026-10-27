import json
import os
from collections.abc import AsyncIterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2
import openai
import pytest
from fastapi.testclient import TestClient
from openai.types.responses import ResponseFunctionToolCall

from app import rate_limit
from app.llm import MODEL, PRICES, cost_usd, get_openai_client
from app.main import app

client = TestClient(app)


def test_health() -> None:
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "ok"}


# --- Claude viết (2026-10-16), theo yêu cầu ---


def test_chat_stream_missing_api_key() -> None:
  # Depends(verify_api_key) chạy TRƯỚC khi tạo StreamingResponse
  # → còn trả 401 thường (JSON), chưa phải stream
  response = client.post("/chat/stream", json={"message": "hi"})
  assert response.status_code == 401
  assert response.json() == {"detail": "Missing API Key"}
  assert not response.headers["content-type"].startswith("text/event-stream")


# --- Client OpenAI giả: chỉ làm đúng những gì chat_events gọi tới ---
#   await client.responses.create(...)  → FakeResponses.create (async)
#   async with stream:                  → FakeStream.__aenter__ / __aexit__
#   async for event in stream:          → FakeStream.__aiter__
#   event.type / .delta / .response.usage.input_tokens  → SimpleNamespace


# Bài 5 (Claude sửa, 2026-10-18): 1 "script" = list event của 1 bước tool loop.
#   FakeOpenAI([step1, step2]) → lần create() thứ 1 trả step1, thứ 2 trả step2, hết script thì
#   lặp lại script cuối (test rate limit gửi nhiều request với cùng 1 script).
#   error: ném exception SAU khi đã phát hết event của script (giả lập OpenAI đứt giữa stream).


class FakeStream:
  def __init__(self, events: list[Any], error: Exception | None = None) -> None:
    self._events = events
    self._error = error

  async def __aenter__(self) -> "FakeStream":
    return self

  async def __aexit__(self, *_args: object) -> None:
    return None

  async def __aiter__(self) -> AsyncIterator[Any]:
    for event in self._events:
      yield event
    if self._error is not None:
      raise self._error


class FakeResponses:
  def __init__(self, scripts: list[list[Any]], error: Exception | None = None) -> None:
    self._scripts = scripts
    self._error = error
    self.calls: list[dict[str, Any]] = []  # ghi lại tham số để kiểm endpoint gọi đúng

  async def create(self, **kwargs: Any) -> FakeStream:
    events = self._scripts[min(len(self.calls), len(self._scripts) - 1)]
    self.calls.append(kwargs)
    return FakeStream(events, self._error)


class FakeOpenAI:
  def __init__(self, scripts: list[list[Any]], error: Exception | None = None) -> None:
    self.responses = FakeResponses(scripts, error)


def completed(input_tokens: int, output_tokens: int, output: list[Any]) -> SimpleNamespace:
  """Event response.completed giả: usage + output của bước."""
  return SimpleNamespace(
    type="response.completed",
    response=SimpleNamespace(
      usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
      output=output,
    ),
  )


def delta(text: str) -> SimpleNamespace:
  return SimpleNamespace(type="response.output_text.delta", delta=text)


def function_call(call_id: str, name: str, arguments: str) -> ResponseFunctionToolCall:
  # dùng type thật của SDK: execute_call cần .name/.arguments, main cần .call_id
  return ResponseFunctionToolCall(
    type="function_call", call_id=call_id, name=name, arguments=arguments
  )


def tool_step(fc: ResponseFunctionToolCall, input_tokens: int, output_tokens: int) -> list[Any]:
  """Bước model gọi 1 tool: output_item.done (bắt call) + completed (usage, output)."""
  return [
    SimpleNamespace(type="response.output_item.done", item=fc),
    completed(input_tokens, output_tokens, [fc]),
  ]


def post_chat(fake: FakeOpenAI, message: str = "hi", client_ip: str | None = None) -> Any:
  api_key = os.getenv("APP_API_KEY")
  assert api_key is not None, "APP_API_KEY chưa có trong .env"
  app.dependency_overrides[get_openai_client] = lambda: fake
  headers = {"X-API-Key": api_key}
  if client_ip is not None:
    headers["X-Client-IP"] = client_ip  # giống route.ts gửi (Buổi 12 A4)
  return client.post("/chat/stream", json={"message": message}, headers=headers)


def parse_sse(body: str) -> list[tuple[str, dict[str, Any]]]:
  """Tách body SSE thành [(tên event, data đã json.loads), ...] — giống handleEvent ở page.tsx."""
  result: list[tuple[str, dict[str, Any]]] = []
  for raw in body.split("\n\n"):
    if not raw:
      continue
    name, data = "", ""
    for line in raw.split("\n"):
      if line.startswith("event:"):
        name = line.removeprefix("event:").strip()
      elif line.startswith("data:"):
        data = line.removeprefix("data:").strip()
    result.append((name, json.loads(data)))
  return result


def test_chat_stream_with_fake_openai() -> None:
  api_key = os.getenv("APP_API_KEY")
  assert api_key is not None, "APP_API_KEY chưa có trong .env"

  events = [
    SimpleNamespace(type="response.created"),  # event khác → server phải bỏ qua
    SimpleNamespace(type="response.output_text.delta", delta="Xin "),
    SimpleNamespace(type="response.output_text.delta", delta="chào\nbạn"),
    SimpleNamespace(
      type="response.completed",
      response=SimpleNamespace(usage=SimpleNamespace(input_tokens=10, output_tokens=3), output=[]),
    ),
  ]
  fake = FakeOpenAI([events])
  app.dependency_overrides[get_openai_client] = lambda: fake
  try:
    response = client.post("/chat/stream", json={"message": "hi"}, headers={"X-API-Key": api_key})
  finally:
    app.dependency_overrides.clear()  # không để override dính sang test khác

  assert response.status_code == 200
  assert response.headers["content-type"].startswith("text/event-stream")

  # endpoint truyền đúng message + bật stream
  assert len(fake.responses.calls) == 1
  call = fake.responses.calls[0]
  assert call["input"] == [{"role": "user", "content": "hi"}]
  assert call["model"] == MODEL
  assert call["stream"] is True

  # thứ tự: delta, delta, done — response.created bị bỏ qua
  sse = parse_sse(response.text)
  assert [name for name, _ in sse] == ["delta", "delta", "done"]
  assert sse[0][1] == {"content": "Xin "}
  assert sse[1][1] == {"content": "chào\nbạn"}  # json.dumps → json.loads ra lại "\n" thật

  done = sse[2][1]
  assert done["input_tokens"] == 10
  assert done["output_tokens"] == 3
  assert done["incomplete"] is False
  # gpt-6-luna: 10 × 0.10/1M + 3 × 0.50/1M = 2.5e-6 (float → approx, không so ==)
  assert done["cost_usd"] == pytest.approx(2.5e-6)


# --- Bài 5: Claude viết (2026-10-18), theo yêu cầu ---


def test_tool_loop_two_steps(isolate: Path) -> None:
  # bước 1: model gọi query_orders; bước 2: model trả lời bằng chữ
  fc = function_call("c1", "query_orders", '{"customer": "An", "status": "shipping"}')
  fake = FakeOpenAI(
    [
      tool_step(fc, input_tokens=100, output_tokens=10),
      [delta("An không "), delta("có đơn đang giao."), completed(150, 5, [])],
    ]
  )
  response = post_chat(fake, "Đơn nào của An đang giao?")

  assert response.status_code == 200
  sse = parse_sse(response.text)
  assert [name for name, _ in sse] == ["tool_call", "tool_result", "delta", "delta", "done"]

  tool_call, tool_result = sse[0][1], sse[1][1]
  assert tool_call == {
    "call_id": "c1",
    "name": "query_orders",
    "arguments": {"customer": "An", "status": "shipping"},  # dict, không phải chuỗi
  }
  assert tool_result["call_id"] == "c1"  # cùng call_id để frontend ghép cặp
  assert tool_result["ok"] is True
  assert tool_result["data"]["order_count"] == 0  # data/orders.csv: An không có đơn shipping

  done = sse[-1][1]
  assert done["steps"] == 2
  assert done["input_tokens"] == 100 + 150  # usage cộng đủ 2 bước
  assert done["output_tokens"] == 10 + 5
  assert done["cost_usd"] == pytest.approx(cost_usd(250, 15, *PRICES[MODEL]))

  # bước 2 phải gửi lại kết quả tool cho model (function_call_output đúng call_id)
  assert len(fake.responses.calls) == 2
  outputs = [i for i in fake.responses.calls[1]["input"] if isinstance(i, dict)]
  fco = [i for i in outputs if i.get("type") == "function_call_output"]
  assert len(fco) == 1 and fco[0]["call_id"] == "c1"
  assert json.loads(fco[0]["output"])["ok"] is True

  # cost log: đúng 1 dòng, ghi vào file tạm (conftest), status ok
  log = [json.loads(line) for line in isolate.read_text(encoding="utf-8").splitlines()]
  assert len(log) == 1
  assert log[0]["status"] == "ok"
  assert log[0]["tools"] == ["query_orders"]
  assert log[0]["steps"] == 2


def test_tool_error_still_done() -> None:
  # model gọi tool không tồn tại → tool_result ok:false, KHÔNG event: error, stream vẫn tới done
  fc = function_call("c2", "nope", "{}")
  fake = FakeOpenAI([tool_step(fc, 50, 5), [delta("Xin lỗi."), completed(60, 3, [])]])
  sse = parse_sse(post_chat(fake).text)

  names = [name for name, _ in sse]
  assert names == ["tool_call", "tool_result", "delta", "done"]
  assert "error" not in names
  assert sse[1][1]["ok"] is False
  assert sse[1][1]["error"] == "Unknown tool: nope"


def test_openai_error_mid_stream(isolate: Path) -> None:
  # OpenAI đứt sau 1 delta → event: error, không có done
  boom = openai.APIConnectionError(request=httpx2.Request("POST", "https://api.openai.com"))
  fake = FakeOpenAI([[delta("Đang ")]], error=boom)
  response = post_chat(fake)

  assert response.status_code == 200  # stream đã bắt đầu → status không đổi được nữa
  sse = parse_sse(response.text)
  assert [name for name, _ in sse] == ["delta", "error"]
  assert "message" in sse[-1][1]

  log = json.loads(isolate.read_text(encoding="utf-8"))
  assert log["status"] == "error"  # finally vẫn ghi log


def test_rate_limit_6th_is_429() -> None:
  fake = FakeOpenAI([[delta("ok"), completed(1, 1, [])]])
  codes = [post_chat(fake).status_code for _ in range(6)]

  assert codes == [200, 200, 200, 200, 200, 429]
  blocked = post_chat(fake)
  assert blocked.status_code == 429
  assert "retry-after" in blocked.headers
  assert len(fake.responses.calls) == 5  # request bị 429 không tới OpenAI


# Buổi 12 A4 (Claude viết theo yêu cầu, 2026-10-26): TestClient luôn là IP "testclient" — giống mọi
# user sau Vercel cùng 1 IP kết nối → X-Client-IP phải tách bộ đếm theo user.
def test_rate_limit_counts_per_client_ip() -> None:
  fake = FakeOpenAI([[delta("ok"), completed(1, 1, [])]])
  codes = [post_chat(fake, client_ip="1.1.1.1").status_code for _ in range(6)]

  assert codes == [200, 200, 200, 200, 200, 429]
  assert post_chat(fake, client_ip="2.2.2.2").status_code == 200  # IP khác: bộ đếm riêng


def test_client_ip_header_without_key_is_401() -> None:
  # header IP chỉ có tác dụng SAU khi qua key → không key thì 401, IP giả không vào bộ đếm
  response = client.post("/chat/stream", json={"message": "hi"}, headers={"X-Client-IP": "9.9.9.9"})

  assert response.status_code == 401
  assert "9.9.9.9" not in rate_limit._hits
