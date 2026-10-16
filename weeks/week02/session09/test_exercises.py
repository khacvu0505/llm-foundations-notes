import json
import os
from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import pytest
from exercises import MODEL, app, get_openai_client
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Claude viết (2026-10-16), theo yêu cầu ---


def test_stream_fake() -> None:
    response = client.get("/stream/fake")

    assert response.status_code == 200
    # Starlette tự thêm "; charset=utf-8" → không so ==
    assert response.headers["content-type"].startswith("text/event-stream")

    # "\\n" = 2 ký tự "\" + "n" do json.dumps escape → event vẫn nằm trên 1 dòng
    # phần tử "" cuối: body kết thúc bằng "\n\n"
    events = response.text.split("\n\n")
    assert events == [
        'data: "Xin"',
        'data: "chào\\nbạn"',
        'data: "nhé"',
        "data: [DONE]",
        "",
    ]


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


class FakeStream:
    def __init__(self, events: list[SimpleNamespace]) -> None:
        self._events = events

    async def __aenter__(self) -> "FakeStream":
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def __aiter__(self) -> AsyncIterator[SimpleNamespace]:
        for event in self._events:
            yield event


class FakeResponses:
    def __init__(self, events: list[SimpleNamespace]) -> None:
        self._events = events
        self.calls: list[dict[str, Any]] = []  # ghi lại tham số để kiểm endpoint gọi đúng

    async def create(self, **kwargs: Any) -> FakeStream:
        self.calls.append(kwargs)
        return FakeStream(self._events)


class FakeOpenAI:
    def __init__(self, events: list[SimpleNamespace]) -> None:
        self.responses = FakeResponses(events)


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
            response=SimpleNamespace(usage=SimpleNamespace(input_tokens=10, output_tokens=3)),
        ),
    ]
    fake = FakeOpenAI(events)
    app.dependency_overrides[get_openai_client] = lambda: fake
    try:
        response = client.post(
            "/chat/stream", json={"message": "hi"}, headers={"X-API-Key": api_key}
        )
    finally:
        app.dependency_overrides.clear()  # không để override dính sang test khác

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    # endpoint truyền đúng message + bật stream
    assert len(fake.responses.calls) == 1
    call = fake.responses.calls[0]
    assert call["input"] == "hi"
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
