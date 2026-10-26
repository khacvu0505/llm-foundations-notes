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


async def stream_answer(body: ChatRequest):
  response_stream = await client.responses.create(
    model="gpt-6-luna",
    instructions="Bạn là trợ lý ảo. Hãy trả lời ngắn gọn bằng tiếng Việt",
    input=body.message,
    stream=True,
  )
  async for event in response_stream:
    if event.type == "response.output_text.delta":
      yield f"{event.delta}"
  yield "\n\n"


@app.post("/chat")
async def chat(body: ChatRequest):
  return StreamingResponse(stream_answer(body), media_type="text/plain")
