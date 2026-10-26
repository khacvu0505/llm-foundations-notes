import json

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI()
load_dotenv()
client = AsyncOpenAI()


@app.get("/health")
def health():
  return {"status": "ok"}


class ChatRequest(BaseModel):
  message: str


def format_sse(event: str, data: dict) -> str:
  return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_answer(body: ChatRequest):
  try:
    response_stream = await client.responses.create(
      model="gpt-6-luna",
      instructions="Bạn là trợ lý ảo. Hãy trả lời ngắn gọn bằng tiếng Việt",
      input=body.message,
      stream=True,
    )
    async for event in response_stream:
      if event.type == "response.output_text.delta":
        yield format_sse("delta", {"content": event.delta})
    yield format_sse("done", {})
  except Exception as e:
    print(f"[stream error] {type(e).__name__}: {e}")
    yield format_sse("error", {"message": "Có lỗi khi tạo câu trả lời, thử lại sau"})


@app.post("/chat")
async def chat(body: ChatRequest):
  return StreamingResponse(stream_answer(body), media_type="text/event-stream")
