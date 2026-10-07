import json
from pathlib import Path
from typing import Literal, TypedDict, cast

import httpx2
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import FunctionToolParam, ResponseInputParam

load_dotenv()  # load .env, có OPENAI_API_KEY

client = OpenAI()
MODEL = "gpt-6-luna"

# Buổi 7 — Function Calling / Tool Use (phần code; quan sát ghi ở notes.md cùng thư mục)
#
# Luật chơi: tự viết code dưới mỗi đề bài, tra docs chính thức khi cần:
#   https://developers.openai.com/api/docs/guides/function-calling
# Import cần gì tự thêm ở đầu file.
# Code thuần tay, KHÔNG framework (không LangChain...). Vòng lặp tool ở đây chính là "agent loop"
# của Phase 03, chỉ chưa có guard và state.
#
# Chuẩn bị: làm mục "Setup (tự làm)" trong notes.md trước (khai báo httpx2).
#
# Chạy:     uv run python weeks/week02/session07/exercises.py
# Vệ sinh:  uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Model: dùng lại model của Buổi 6 (gpt-6-luna). Câu hỏi ngắn, mỗi lần chạy tốn vài lời gọi API.
#
# Nhắc lại từ các buổi trước:
#   - API không nhớ gì, mình tự gửi lại lịch sử (Buổi 3 bài 2, Buổi 6).
#   - response.output là LIST nhiều item, không chỉ text: reasoning, message... (Buổi 4 bài 3).
#     Buổi này có thêm item type "function_call".
#   - JSON schema cho LLM: Pydantic model_json_schema() (Buổi 5 bài 1), strict mode (Buổi 5 bài 3).
#   - Chạy song song: asyncio.gather (Buổi 1 bài 4, Buổi 4 bài 2).
#   - Token + cost: response.usage, cost_usd (Buổi 6 bài 3).
#
# Ý tưởng chính (so với TS):
#   LLM KHÔNG tự chạy hàm. Nó chỉ trả về "mình muốn gọi hàm X với args Y" (một JSON string).
#   Code của mình chạy hàm thật, rồi gửi kết quả ngược lại để LLM viết câu trả lời cuối.
#   Giống 1 RPC mà phía client (code mình) là bên thực thi, LLM là bên ra quyết định.
#
#   Lượt 1:  input [user]                              → output [function_call]
#   Lượt 2:  input [user, function_call, call_output]  → output [message]


# ============================================================================
# Bài 1 — 1 tool, 1 vòng, làm thủ công từng bước
# ============================================================================
#
# Tool: get_weather(city) — nhiệt độ hiện tại, gọi Open-Meteo (miễn phí, không cần key):
#   GET https://api.open-meteo.com/v1/forecast
#       ?latitude=21.03&longitude=105.85&current=temperature_2m,weather_code
#   → JSON có current.temperature_2m (°C), current.weather_code (mã WMO, 0 = trời quang).
#
# Yêu cầu:
#   - Tự giữ 1 dict tọa độ cho vài thành phố (Hà Nội, Đà Nẵng, TP.HCM...). Trong JSON schema
#     của tool, giới hạn city bằng "enum" để LLM chỉ chọn trong danh sách đó.
#   - Định nghĩa tool dạng dict: {"type": "function", "name": ..., "description": ...,
#     "parameters": <JSON schema>, "strict": True}. Viết schema TAY (chưa dùng Pydantic).
#     Gợi ý: strict=True đòi mọi property nằm trong "required" và "additionalProperties": False.
#   - Gọi API với tools=[...], câu hỏi "Hà Nội bây giờ bao nhiêu độ?".
#   - In ra từng item trong response.output: type là gì? function_call có name, arguments, call_id.
#     arguments là str hay dict? (gợi ý: json.loads)
#   - Chạy hàm thật, gửi lại lần 2 với input = [câu user] + các item output lần 1
#     + {"type": "function_call_output", "call_id": ..., "output": <str>}. In câu trả lời cuối.
#   - Tự kiểm: hỏi "Thủ đô của Pháp là gì?" → model có gọi tool không? (mong đợi: không)
#
# Gợi ý typing: response.output là list object Pydantic của SDK, còn input là list TypedDict.
#   Docs ghép thẳng (input += response.output): chạy đúng nhưng pyright báo lỗi kiểu.
#   KHÔNG dùng item.model_dump(): ra key "async_" → API trả 400 (đã thử 06/10). Dùng typing.cast.
#   Output của tool phải là str → json.dumps(dict, ensure_ascii=False).
#
# Câu hỏi ghi notes.md: lời gọi lần 2 có gửi lại câu hỏi user không, vì sao phải gửi?
#   Thiếu call_id thì sao? Mỗi lần chạy tốn mấy lời gọi API, bao nhiêu token?

# TODO: viết code ở đây
CITIES = {
    "Hà Nội": {"latitude": 21.03, "longitude": 105.85},
    "Đà Nẵng": {"latitude": 16.05, "longitude": 108.20},
    "TP.HCM": {"latitude": 10.75, "longitude": 106.67},
}

# Mã thời tiết WMO → chữ. Nguồn: https://open-meteo.com/en/docs (mục "WMO Weather interpretation
# codes"). Bỏ các mã tuyết / mưa băng (56-57, 66-67, 71-77, 85-86) vì không gặp ở VN.
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


def get_weather(city: Literal["Hà Nội", "Đà Nẵng", "TP.HCM"]) -> WeatherResponse:
    """Get current weather for a given city"""
    response = (
        httpx2.get(
            OPEN_METEO_URL,
            params={
                **CITIES[city],
                "current": "temperature_2m,weather_code",
                "timezone": "Asia/Ho_Chi_Minh",
            },
        )
        .raise_for_status()
        .json()
    )
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
                "enum": list(CITIES.keys()),
                "description": "City name",
            },
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}


def run_bai1() -> None:
    input_list: ResponseInputParam = [{"role": "user", "content": "Hà Nội bây giờ bao nhiêu độ?"}]
    response = client.responses.create(
        model=MODEL,
        input=input_list,
        tools=[get_weather_tool],
    )

    calls = [item for item in response.output if item.type == "function_call"]
    if not calls:
        print(response.output_text)
        return
    call = calls[0]
    args = json.loads(call.arguments)  # arguments là chuỗi JSON, phải parse
    result = get_weather(**args)
    print(f"→ {call.name}({args})")
    print(f"← {result}")
    input_list += cast(ResponseInputParam, response.output)
    input_list.append(
        {
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result, ensure_ascii=False),
        }
    )
    final = client.responses.create(
        model=MODEL,
        input=input_list,
        instructions=(
            "Hãy trả lời ngắn gọn, chỉ 1 câu, không cần giải thích. Nếu có thể, hãy kèm nhiệt độ"
            " bằng °C."
        ),
    )
    print("\nRESPONSE: ", final.output_text)


# ============================================================================
# Bài 2 — Vòng lặp tổng quát + tool thứ 2: query file CSV
# ============================================================================
#
# Tool 2: query_orders — CHỈ ĐỌC file orders.csv cùng thư mục (module csv có sẵn, không cần
#   pandas). Tham số gợi ý: customer (tên khách hoặc null), status (enum delivered/shipping/
#   pending/cancelled hoặc null). Trả về danh sách đơn khớp + tổng số đơn
#   + tổng tiền (quantity × unit_price).
#   Gợi ý strict mode: tham số "không bắt buộc" vẫn phải nằm trong required,
#   kiểu ["string", "null"].
#
# Yêu cầu:
#   - Registry: dict tên tool → hàm Python (giống map handler trong Express). Vòng lặp tra tên
#     ở đây, không if/else theo tên.
#   - Hàm run(user_input) lặp: gọi API → nếu output có function_call thì chạy hết, thêm output vào
#     input, gọi tiếp → đến khi không còn function_call thì trả text cuối.
#   - Chặn vòng lặp vô hạn: MAX_STEPS (ví dụ 5). Vượt thì dừng và báo, không gọi API tiếp.
#   - In log mỗi bước: "→ gọi query_orders({...})", "← 3 đơn, 157000đ".
#   - Thử:
#       "An đã đặt bao nhiêu đơn, tổng bao nhiêu tiền?"
#       "Có đơn nào đang pending không?"
#       "Đơn nào bị huỷ, và trời Đà Nẵng giờ thế nào?"  (cần cả 2 tool)
#   - Tự kiểm tổng tiền của An bằng tay (đọc CSV) xem LLM có cộng đúng không. Ai cộng: code hay LLM?
#
# Câu hỏi ghi notes.md: tổng tiền nên để tool tính sẵn hay để LLM tự cộng từ danh sách đơn? Vì sao?


# TODO: viết code ở đây
Status = Literal["delivered", "shipping", "pending", "cancelled"]


class OrderItem(TypedDict):
    order_id: int
    customer: str
    product: str
    quantity: int
    unit_price: int
    status: Status
    created_at: str


class OrderResponse(TypedDict):
    orders: list[OrderItem]
    order_count: int
    total_amount_vnd: int


def query_orders(customer: str | None, status: Status | None) -> OrderResponse:
    orders_path = Path(__file__).parent / "orders.csv"
    df = pd.read_csv(orders_path)

    orders = df.to_dict(orient="records")

    if customer is not None:
        orders = [o for o in orders if o["customer"].lower() == customer.lower()]
    if status is not None:
        orders = [o for o in orders if o["status"] == status]

    order_count = len(orders)
    total_amount_vnd = sum(o["quantity"] * o["unit_price"] for o in orders)

    return OrderResponse(orders=orders, order_count=order_count, total_amount_vnd=total_amount_vnd)


query_orders_tool: FunctionToolParam = {
    "type": "function",
    "name": "query_orders",
    "description": (
        "Tra cứu đơn hàng (chỉ đọc), lọc theo tên khách và/hoặc trạng thái. "
        "Trả về danh sách đơn khớp, số đơn (order_count) và tổng tiền VND (total_amount_vnd)."
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

TOOLS_REGISTRY = {"get_weather": get_weather, "query_orders": query_orders}
TOOLS = [get_weather_tool, query_orders_tool]
MAX_STEPS = 5


def run_bai2(user_input: str) -> None:
    input_list: ResponseInputParam = [{"role": "user", "content": user_input}]
    for step in range(MAX_STEPS):
        print(f"[step {step + 1}]")
        response = client.responses.create(
            model=MODEL,
            input=input_list,
            tools=TOOLS,
        )
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            print(response.output_text)
            return
        input_list += cast(ResponseInputParam, response.output)
        for call in calls:
            args = json.loads(call.arguments)
            result = TOOLS_REGISTRY[call.name](**args)
            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                }
            )
            print(f"→ {call.name}({args})")
            print(f"← {str(result)[:150]}")  # chỉ cắt khi in, LLM vẫn nhận đủ

    print("\n Đã vượt quá MAX_STEPS, dừng vòng lặp.")


# ============================================================================
# Bài 3 — Parallel tool calls
# ============================================================================
#
# Yêu cầu:
#   - Hỏi "So sánh nhiệt độ Hà Nội, Đà Nẵng và TP.HCM bây giờ."
#     Đếm số function_call trong MỘT response. Mỗi cái có call_id riêng.
#   - Chạy các tool đó song song (asyncio.gather + AsyncOpenAI, hoặc httpx2.AsyncClient).
#     Đo thời gian chạy tool: tuần tự vs song song.
#   - Gửi lại đủ output cho TẤT CẢ call_id. Thử cố tình thiếu 1 cái → API báo lỗi gì?
#   - Chạy lại với parallel_tool_calls=False: model gọi tool kiểu gì, mất mấy lời gọi API?
#
# Câu hỏi ghi notes.md: thứ tự function_call_output có cần khớp thứ tự function_call không?
#   parallel_tool_calls=False tốn thêm bao nhiêu thời gian / token?

# TODO: viết code ở đây


# ============================================================================
# Bài 4 — Xử lý lỗi: tool hỏng, tool không tồn tại, args sai
# ============================================================================
#
# Nguyên tắc: lỗi của TOOL không được làm sập vòng lặp. Bắt lỗi, gửi lại cho LLM dạng output
#   (ví dụ {"error": "..."}), để LLM tự quyết: thử lại, đổi cách, hay báo user.
#
# Yêu cầu — tạo từng tình huống và ghi lại LLM phản ứng thế nào:
#   a) Tool lỗi giữa chừng: cho get_weather ném lỗi (timeout rất nhỏ, hoặc URL sai).
#      LLM nói gì với user?
#   b) Tool không tồn tại: registry thiếu tên mà model gọi (ví dụ khai báo tool get_stock_price
#      trong tools nhưng không có trong registry). Trả lỗi kiểu "unknown tool",
#      KHÔNG crash KeyError.
#   c) Args sai: json.loads hỏng, hoặc thiếu field. Tắt strict (strict=False) để dễ gặp hơn,
#      hoặc tự gọi hàm thực thi với arguments='{"city": ' để test.
#      Validate bằng Pydantic như Buổi 5?
#   d) Model gọi tool lặp mãi: cho tool luôn trả lỗi → MAX_STEPS có chặn được không? Hết bước thì
#      báo user gì?
#   - Log rõ lỗi (loại lỗi, tool nào, args nào) ra terminal, nhưng thông điệp gửi LLM thì gọn.
#
# Bảo mật (ghi notes.md): output của tool có chứa gì không nên để LLM thấy không (API key, stack
#   trace, đường dẫn file)? Nếu dữ liệu trong CSV chứa câu "Bỏ qua chỉ dẫn trước, ..." thì sao?
#   (prompt injection qua kết quả tool — thử thêm 1 dòng như vậy vào 1 BẢN SAO của orders.csv)

# TODO: viết code ở đây


# ============================================================================
# Bài 5 — Gắn tools vào CLI chatbot Buổi 6 + đo token của tool schema
# ============================================================================
#
# Yêu cầu:
#   - Dùng lại vòng lặp chat của Buổi 6 (history, /reset, /exit). Mỗi lượt user có thể kéo theo
#     nhiều lời gọi API (vòng lặp tool của Bài 2).
#   - Lịch sử phải chứa cả function_call + function_call_output, không chỉ text, để lượt sau bot
#     còn biết đã tra gì. Thử: "An có mấy đơn?" → "Còn Bình?" (bot hiểu "Bình" là tên khách).
#   - In token/cost mỗi lượt user = cộng usage của TẤT CẢ lời gọi API trong lượt đó.
#   - Đo: cùng câu "Xin chào", gửi có tools=[...] và không có tools. Input token chênh bao nhiêu?
#     Tool schema được gửi lại MỖI lời gọi, giống system prompt.
#   - (Tùy chọn) Sinh JSON schema từ Pydantic model (Buổi 5) thay vì viết tay, so với bản viết tay.
#   - (Tùy chọn, nợ Buổi 5) Trích đơn hàng bằng tool: khai báo tool save_order(order) với schema
#     Order, model "gọi" tool đó thay cho text_format. So với responses.parse ở Buổi 5.
#
# Câu hỏi ghi notes.md: sliding window Buổi 6 cắt theo cặp user/assistant. Giờ lịch sử có thêm
#   function_call / function_call_output thì cắt sao cho không bị lẻ cặp call ↔ output?

# TODO: viết code ở đây


if __name__ == "__main__":
    # run_bai1()

    run_bai2("An đã đặt bao nhiêu đơn, tổng bao nhiêu tiền?")
    run_bai2("Có đơn nào đang pending không?")
    run_bai2("Đơn nào bị huỷ, và trời Đà Nẵng giờ thế nào?")
