import asyncio
import json
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated, Any, cast

import openai
from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from openai.types.responses import ResponseFunctionToolCall, ResponseInputParam
from pydantic import BaseModel, ConfigDict, Field

from app.auth import verify_api_key
from app.cost_log import write_cost_log
from app.llm import MODEL, PRICES, cost_usd, get_openai_client
from app.rate_limit import rate_limit
from app.sse import format_sse
from app.tools import MAX_STEPS, TOOLS, TOOLS_REGISTRY, execute_call

# Không CORS: trình duyệt chỉ gọi Next (/api/chat), Next server gọi FastAPI (server-to-server).
app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
  return {"status": "ok"}


class ChatRequest(BaseModel):
  model_config = ConfigDict(extra="forbid")
  message: str = Field(description="The user's message", max_length=500, min_length=1)


def parse_args(raw: str) -> dict[str, Any]:
  try:
    return json.loads(raw)
  except json.JSONDecodeError:
    return {"_raw": raw}


async def chat_events(openai_client: AsyncOpenAI, message: str) -> AsyncIterator[str]:
  input_list: ResponseInputParam = [{"role": "user", "content": message}]
  count = 0
  total_in = 0
  total_out = 0
  incomplete = False
  # Bài 3 cost log (Claude thêm theo yêu cầu, 2026-10-18):
  # khai báo trước try để finally luôn đọc được
  start = time.perf_counter()
  ttft_ms: int | None = None
  tools_called: list[str] = []
  steps = 0
  status = "ok"

  try:
    for step in range(MAX_STEPS):
      print(f"[step {step + 1}]")
      steps += 1
      response_stream = await openai_client.responses.create(
        model=MODEL,
        input=input_list,
        instructions=(
          "Trả lời ngắn gọn bằng tiếng Việt. "
          "Cần số liệu đơn hàng, doanh thu hay thời tiết thì gọi tool, không tự bịa số."
        ),
        stream=True,
        max_output_tokens=500,
        tools=TOOLS,
      )

      calls: list[ResponseFunctionToolCall] = []
      output_items = []

      # Lặp qua các luồng sự kiện được chuẩn hóa từ OpenAI
      async with response_stream:
        async for event in response_stream:
          if event.type == "response.incomplete":
            incomplete = True
          if event.type == "response.output_text.delta":
            if ttft_ms is None:
              ttft_ms = int((time.perf_counter() - start) * 1000)
            yield format_sse("delta", {"content": event.delta})
            count += 1
          elif event.type == "response.completed" or event.type == "response.incomplete":
            usage = event.response.usage
            output_items = event.response.output
            if usage is not None:
              total_in += usage.input_tokens
              total_out += usage.output_tokens
          elif event.type == "response.output_item.done" and event.item.type == "function_call":
            calls.append(event.item)

      if not calls:
        yield format_sse(
          "done",
          {
            "input_tokens": total_in,
            "output_tokens": total_out,
            "cost_usd": cost_usd(total_in, total_out, *PRICES[MODEL]),
            "steps": step + 1,
            "incomplete": incomplete,
          },
        )
        if incomplete:
          status = "incomplete"
        return

      input_list += cast(ResponseInputParam, output_items)

      for call in calls:
        tools_called.append(call.name)
        yield format_sse(
          "tool_call",
          {"call_id": call.call_id, "name": call.name, "arguments": parse_args(call.arguments)},
        )
        result = await execute_call(call, TOOLS_REGISTRY)
        yield format_sse("tool_result", {"call_id": call.call_id, "name": call.name, **result})
        input_list.append(
          {
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result, ensure_ascii=False),
          }
        )

    # Hết MAX_STEPS mà model vẫn gọi tool → dừng, báo client (Claude thêm theo yêu cầu, 2026-10-17)
    print(f"[max steps] vượt {MAX_STEPS} bước, dừng")
    status = "error"
    yield format_sse("error", {"message": "Câu hỏi cần quá nhiều bước, thử hỏi cụ thể hơn"})
  except asyncio.CancelledError:
    print(f"[stream cancelled] sau {count} delta")
    status = "cancelled"
    raise
  except (openai.APIError, RuntimeError) as e:
    print(f"[stream error] {type(e).__name__} | model={MODEL} | {e}")
    status = "error"
    yield format_sse("error", {"message": "Có lỗi khi tạo câu trả lời, thử lại sau"})
  finally:
    # 1 request = 1 dòng log, kể cả khi bị cancel / lỗi (finally luôn chạy)
    write_cost_log(
      {
        "ts": datetime.now(UTC).isoformat(),
        "model": MODEL,
        "steps": steps,
        "tools": tools_called,
        "input_tokens": total_in,
        "output_tokens": total_out,
        "cost_usd": cost_usd(total_in, total_out, *PRICES[MODEL]),
        "ttft_ms": ttft_ms,
        "latency_ms": int((time.perf_counter() - start) * 1000),
        "status": status,
      }
    )


@app.post("/chat/stream", dependencies=[Depends(verify_api_key), Depends(rate_limit)])
async def chat_stream(
  body: ChatRequest, openai_client: Annotated[AsyncOpenAI, Depends(get_openai_client)]
) -> StreamingResponse:
  return StreamingResponse(
    chat_events(openai_client, body.message),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache"},
  )
