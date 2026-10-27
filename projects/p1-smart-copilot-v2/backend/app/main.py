import json
from typing import Literal, TypedDict

import httpx2
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from openai.types.responses import FunctionToolParam
from pydantic import BaseModel

app = FastAPI()
load_dotenv()
client = AsyncOpenAI()

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


CITIES = {
  "Hà Nội": {"latitude": 21.03, "longitude": 105.85},
  "Đà Nẵng": {"latitude": 16.05, "longitude": 108.20},
  "TP.HCM": {"latitude": 10.75, "longitude": 106.67},
}

WMO_CODES: dict[int, str] = {
  0: "trời quang",
  1: "ít mây",
  2: "mây rải rác",
  3: "nhiều mây, u ám",
  45: "sương mù",
  48: "sương mù",
  51: "mưa phùn nhẹ",
  53: "mưa phùn",
  55: "mưa phùn dày",
  61: "mưa nhỏ",
  63: "mưa vừa",
  65: "mưa to",
  80: "mưa rào nhẹ",
  81: "mưa rào",
  82: "mưa rào rất to",
  95: "dông",
  96: "dông kèm mưa đá nhỏ",
  97: "dông mạnh",
  99: "dông kèm mưa đá lớn",
}


@app.get("/health")
def health():
  return {"status": "ok"}


class ChatRequest(BaseModel):
  message: str


def format_sse(event: str, data: dict) -> str:
  return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


class WeatherResponse(TypedDict):
  city: str
  temperature_c: float
  condition: str
  observed_at: str


async def get_weather(city: Literal["Hà Nội", "Đà Nẵng", "TP.HCM"]):
  """Get current weather for a given city"""
  async with httpx2.AsyncClient() as http:
    res = await http.get(
      OPEN_METEO_URL,
      params={
        **CITIES[city],
        "current": "temperature_2m,weather_code",
        "timezone": "Asia/Ho_Chi_Minh",
      },
    )
    response = res.raise_for_status().json()

  current = response["current"]
  code = current["weather_code"]
  return WeatherResponse(
    city=city,
    temperature_c=current["temperature_2m"],
    condition=WMO_CODES.get(code, f"không xác định (mã {code})"),
    observed_at=current["time"].replace("T", " "),
  )


get_weather_tool: FunctionToolParam = {
  "type": "function",
  "name": "get_weather",
  "description": "Get current weather for a given city",
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "enum": ["Hà Nội", "Đà Nẵng", "TP.HCM"],
        "description": "City name",
      }
    },
    "required": ["city"],
    "additionalProperties": False,
  },
}

TOOLS = [get_weather_tool]


async def stream_answer(body: ChatRequest):
  try:
    response_stream = await client.responses.create(
      model="gpt-6-luna",
      instructions="Bạn là trợ lý ảo. Hãy trả lời ngắn gọn bằng tiếng Việt",
      input=body.message,
      stream=True,
      tools=TOOLS,
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
