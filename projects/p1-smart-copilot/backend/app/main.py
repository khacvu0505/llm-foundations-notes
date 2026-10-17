import asyncio
from collections.abc import AsyncIterator
from typing import Annotated

import openai
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

from app.auth import verify_api_key
from app.llm import MODEL, PRICES, cost_usd, get_openai_client
from app.sse import format_sse

app = FastAPI()

origins = [
  "http://localhost:3000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_methods=["GET", "POST"],
  allow_headers=["content-type", "x-api-key"],
)


@app.get("/health")
def health() -> dict[str, str]:
  return {"status": "ok"}


class ChatRequest(BaseModel):
  model_config = ConfigDict(extra="forbid")
  message: str = Field(description="The user's message", max_length=500, min_length=1)


async def chat_events(openai_client: AsyncOpenAI, message: str) -> AsyncIterator[str]:
  count = 0

  try:
    response_stream = await openai_client.responses.create(
      model=MODEL,
      input=message,
      instructions="Trả lời ngắn gọn, bằng tiếng Việt.",
      stream=True,
      max_output_tokens=500,
    )

    # Lặp qua các luồng sự kiện được chuẩn hóa từ OpenAI
    async with response_stream:
      async for event in response_stream:
        if event.type == "response.output_text.delta":
          yield format_sse("delta", {"content": event.delta})
          count += 1
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
async def chat_stream(
  body: ChatRequest, openai_client: Annotated[AsyncOpenAI, Depends(get_openai_client)]
) -> StreamingResponse:
  return StreamingResponse(
    chat_events(openai_client, body.message),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache"},
  )
