import json
from collections.abc import Callable
from inspect import isawaitable
from pathlib import Path
from typing import Any, Literal, TypedDict, cast

import httpx2
import pandas as pd
from openai.types.responses import FunctionToolParam, ResponseFunctionToolCall

# Claude thêm (2026-10-18, Bài 5): hằng module để test monkeypatch sang CSV nhỏ
ORDERS_CSV = Path(__file__).parent.parent / "data" / "orders.csv"

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

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherResponse(TypedDict):
  city: str
  temperature_c: float
  condition: str
  observed_at: str


async def get_weather(city: Literal["Hà Nội", "Đà Nẵng", "TP.HCM"]) -> WeatherResponse:
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


Status = Literal["delivered", "shipping", "pending", "cancelled"]


class OrderItem(TypedDict):
  order_id: int
  customer: str
  product: str
  quantity: int
  unit_price: int
  status: Status
  created_at: str
  city: str


class OrderResponse(TypedDict):
  orders: list[OrderItem]
  order_count: int
  total_amount_vnd: int


def query_orders(
  customer: str | None, status: Status | None, csv_name: str = "orders.csv"
) -> OrderResponse:
  orders_path = Path(__file__).parent.parent / "data" / csv_name
  df = pd.read_csv(orders_path)

  orders = cast(list[OrderItem], df.to_dict(orient="records"))

  if customer is not None:
    orders = [o for o in orders if o["customer"].lower() == customer.lower()]
  if status is not None:
    orders = [o for o in orders if o["status"] == status]

  order_count = len(orders)
  total_amount_vnd = sum(o["quantity"] * o["unit_price"] for o in orders)

  return OrderResponse(
    orders=orders,
    order_count=order_count,
    total_amount_vnd=total_amount_vnd,
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
        "enum": list(CITIES.keys()),
        "description": "City name",
      },
    },
    "required": ["city"],
    "additionalProperties": False,
  },
}

query_orders_tool: FunctionToolParam = {
  "type": "function",
  "name": "query_orders",
  "description": (
    "Tra cứu đơn hàng (chỉ đọc), lọc theo tên khách và/hoặc trạng thái. "
    "Trả về danh sách đơn khớp, số đơn (order_count) và tổng tiền VND (total_amount_vnd). "
    "Mỗi đơn có city (Hà Nội / Đà Nẵng / TP.HCM) = thành phố giao hàng, "
    "dùng được với get_weather để xem thời tiết nơi giao."
  ),
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {
      "customer": {
        "type": ["string", "null"],  # null = không lọc theo khách
        "description": "Tên khách hàng. null = mọi khách.",
      },
      "status": {
        "type": ["string", "null"],  # null = không lọc theo trạng thái
        "enum": ["delivered", "shipping", "pending", "cancelled", None],  # phải có None
        "description": "Trạng thái đơn. null = mọi trạng thái.",
      },
    },
    # strict: mọi key phải nằm trong required. "Tùy chọn" = cho phép null ở type,
    # KHÔNG phải bỏ key khỏi required (~ TS `status: string | null`, không phải `status?:`)
    "required": ["customer", "status"],
    "additionalProperties": False,
  },
}

# Claude sửa schema (2026-10-17) theo yêu cầu; hàm sales_summary do bạn viết
sales_summary_tool: FunctionToolParam = {
  "type": "function",
  "name": "sales_summary",
  "description": (
    "Tổng hợp doanh thu (chỉ đọc), gom theo ngày hoặc theo món. "
    "Trả về danh sách {label, revenue_vnd, order_count} đã tính sẵn và sắp xếp sẵn: "
    "group_by='day' → theo ngày tăng dần (vẽ chart xu hướng); "
    "group_by='product' → theo doanh thu giảm dần (món bán chạy nhất đứng đầu). "
    "Dùng cho câu hỏi về doanh thu, món bán chạy, xu hướng theo ngày. "
    "Dùng số tool trả về, KHÔNG tự cộng lại."
  ),
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {
      "group_by": {
        "type": "string",  # bắt buộc, không null: tool cần biết gom theo gì
        "enum": ["day", "product"],
        "description": "Gom theo 'day' (ngày tạo đơn) hoặc 'product' (tên món).",
      },
      "status": {
        "type": ["string", "null"],  # null = mọi trạng thái trừ cancelled
        "enum": ["delivered", "shipping", "pending", "cancelled", None],  # phải có None
        "description": (
          "Trạng thái đơn. null = mọi trạng thái TRỪ cancelled (doanh thu thực). "
          "Muốn xem riêng đơn huỷ thì truyền 'cancelled'."
        ),
      },
    },
    # strict: mọi key phải nằm trong required. "Tùy chọn" = cho phép null ở type,
    # KHÔNG phải bỏ key khỏi required (~ TS `status: string | null`, không phải `status?:`)
    "required": ["group_by", "status"],
    "additionalProperties": False,
  },
}


class SalesRow(TypedDict):
  label: str
  revenue_vnd: int
  order_count: int


def sales_summary(group_by: Literal["day", "product"], status: Status | None) -> list[SalesRow]:
  col = {"day": "created_at", "product": "product"}[group_by]
  df = pd.read_csv(ORDERS_CSV)
  df["revenue"] = df["quantity"] * df["unit_price"]

  if status is not None:
    df = df[df["status"] == status]
  else:
    df = df[df["status"] != "cancelled"]

  summary = (
    df.groupby(col)
    .agg(revenue_vnd=("revenue", "sum"), order_count=("order_id", "count"))
    .reset_index()
  )
  summary = (
    summary.sort_values(col)
    if group_by == "day"
    else summary.sort_values("revenue_vnd", ascending=False)
  )

  return [
    {
      "label": row[col],
      "revenue_vnd": row["revenue_vnd"],
      "order_count": row["order_count"],
    }
    for row in summary.to_dict(orient="records")
  ]


TOOLS_REGISTRY: dict[str, Callable[..., Any]] = {
  "get_weather": get_weather,
  "query_orders": query_orders,
  "sales_summary": sales_summary,
}
TOOLS = [get_weather_tool, query_orders_tool, sales_summary_tool]
MAX_STEPS = 5


async def execute_call(
  call: ResponseFunctionToolCall, registry: dict[str, Callable[..., Any]]
) -> dict[str, Any]:
  # Claude sửa (2026-10-17) theo yêu cầu: shape thống nhất {ok, data} | {ok, error},
  # giữ giá trị Python thô — json.dumps 1 lần ở main.py (SSE + function_call_output)
  func = registry.get(call.name)
  if func is None:
    print(f"[tool error] unknown tool | {call.name} | {call.arguments}")
    return {"ok": False, "error": f"Unknown tool: {call.name}"}

  try:
    args = json.loads(call.arguments)
    result = func(**args)
    if isawaitable(result):
      result = await result
    return {"ok": True, "data": result}

  except json.JSONDecodeError:
    print(f"[tool error] JSON hỏng | {call.name} | {call.arguments}")
    return {"ok": False, "error": "arguments không phải JSON hợp lệ"}
  except Exception as e:
    print(f"[tool error] {type(e).__name__} | {call.name} | {call.arguments} | {e}")
    return {"ok": False, "error": f"Tool {call.name} lỗi, thử lại sau"}
