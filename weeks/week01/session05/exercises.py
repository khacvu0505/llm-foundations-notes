import json
import re
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import ResponseInputParam
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

load_dotenv()  # load .env, set OPENAI_API_KEY

# Buổi 5 — Structured Output với Pydantic
#
# Luật chơi: tự viết code dưới mỗi đề bài, tra docs chính thức khi cần
# (Pydantic v2 docs, OpenAI "Structured Outputs" guide).
# Import cần gì tự thêm ở đầu file.
#
# Chuẩn bị: xem mục "Setup" trong notes.md cùng thư mục (khai báo pydantic trong pyproject).
#
# Chạy:     uv run python weeks/week01/session05/exercises.py
# Vệ sinh:  uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Bài 1–2 chạy offline, không tốn tiền. Bài 3–5 gọi API: dùng gpt-4o-mini, prompt ngắn.
# Quan sát ghi vào notes.md cùng thư mục.
#
# Bảng map Zod → Pydantic (để tham khảo, tự kiểm chứng khi làm):
#   z.object({...})            → class X(BaseModel): ...
#   z.string() / z.number()    → str / int, float
#   .optional() / .nullable()  → X | None = None  /  X | None
#   z.enum(["a", "b"])         → Literal["a", "b"]
#   .min(0).max(150)           → Field(ge=0, le=150)
#   .describe("...")           → Field(description="...")
#   .refine(...)               → @field_validator
#   schema.parse(data)         → X.model_validate(data)        (lỗi: ValidationError)
#   schema.safeParse(data)     → try/except ValidationError
#   JSON.parse + parse         → X.model_validate_json(text)
#   z.infer<typeof schema>     → không cần: class chính là type


# ============================================================================
# Bài 1 — Pydantic cơ bản (offline)
# ============================================================================
#
# Yêu cầu:
#   - class Contact(BaseModel): name (str), phone (str | None), email (str | None),
#     age (int, 0–150 bằng Field).
#   - Thử model_validate với 5 dict: hợp lệ, thiếu name, age = -5, age = "25", age = "hai lăm".
#     Bắt ValidationError, in e.errors() để xem Pydantic báo lỗi ở field nào, vì sao.
#   - Để ý trường hợp age = "25": Pydantic ép thành số 25, còn Zod z.number() sẽ báo lỗi.
#     Thử thêm model_config = ConfigDict(strict=True) xem khác gì. Ghi vào notes.md.
#   - Thử model_dump(), model_dump_json(), model_validate_json('{"name": ...}').
#   - In Contact.model_json_schema(): đây là thứ sẽ được gửi sang OpenAI ở Bài 3.


# TODO: viết code ở đây
class Contact(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    age: int = Field(ge=0, le=150)


class StrictContact(Contact):
    model_config = ConfigDict(strict=True)


def bai1_validate() -> None:
    cases = [
        {"name": "Nguyen Van A", "age": 25},
        {"age": 16},
        {"name": "Nguyen Van C", "age": -5},
        {"name": "Nguyen Van D", "age": "25"},
        {"name": "Nguyen Van E", "age": "hai lam"},
    ]

    for model in (Contact, StrictContact):
        print(f"\n=== {model.__name__} ===")
        for data in cases:
            try:
                print(model.model_validate(data))

            except ValidationError as e:
                print()
                print(e.errors())


def bai1_serialize() -> None:

    # Phần A: object Pydantic (đầu vào) -> dict / JSON string (đầu ra)
    print("=== dump ===")
    contact = Contact.model_validate({"name": "Nguyen Van A", "age": 25})

    dumped = contact.model_dump()
    print(type(dumped), dumped)

    dumped_json = contact.model_dump_json()
    print(type(dumped_json), dumped_json)
    print(contact.model_dump_json(indent=2))

    # Phần B: JSON string (đầu vào) -> object Pydantic (đầu ra), parse + validate cùng lúc
    texts = [
        '{"name": "Nguyen Van A", "age": 25}',
        '{"name": "Nguyen Van D", "age": "25"}',
        '{"name": "Nguyen Van F", "age": 25,}',  # JSON hỏng: thừa dấu phẩy cuối
    ]

    for model in (Contact, StrictContact):
        print(f"\n=== {model.__name__}.model_validate_json ===")
        for text in texts:
            try:
                print(model.model_validate_json(text))

            except ValidationError as e:
                print()
                print(e.errors())


def bai1_schema() -> None:
    for model in (Contact, StrictContact):
        print(f"\n=== {model.__name__} JSON schema ===")
        print(json.dumps(model.model_json_schema(), indent=2))


# ============================================================================
# Bài 2 — Schema cho bài toán thật: đơn hàng (offline)
# ============================================================================
#
# Tình huống: shop nhận tin nhắn đặt hàng lộn xộn qua chat, cần tách thành dữ liệu có cấu trúc.
#
# Yêu cầu:
#   - class OrderItem(BaseModel): product (str), quantity (int, >= 1),
#     size (Literal S/M/L/XL | None)
#   - class Order(BaseModel): customer_name (str | None), phone (str | None),
#     address (str | None), items (list[OrderItem]), note (str | None)
#   - Thêm Field(description=...) tiếng Việt cho từng field. Description được gửi kèm
#     schema, nên nó cũng là một phần của prompt.
#   - @field_validator cho phone: số VN 10 chữ số, bắt đầu bằng 0. Cho phép người dùng gõ
#     có dấu cách/chấm ("0901 234 567", "0901.234.567"): làm sạch rồi mới kiểm.
#   - Tự test bằng 3–4 dict viết tay, gồm 1 dict sai phone.


# TODO: viết code ở đây
class OrderItem(BaseModel):
    product: str = Field(description="Tên sản phẩm")
    quantity: int = Field(ge=1, description="Số lượng")
    size: Literal["S", "M", "L", "XL"] | None = Field(description="Kích cỡ", default=None)


class OrderBase(BaseModel):
    customer_name: str | None = Field(description="Tên khách hàng", default=None)
    phone: str | None = Field(description="Số điện thoại", default=None)
    address: str | None = Field(description="Địa chỉ", default=None)
    items: list[OrderItem] = Field(description="Danh sách sản phẩm")
    note: str | None = Field(description="Ghi chú", default=None)


class Order(OrderBase):
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        phone_clean = re.sub(r"[\s.\-]", "", value)
        if not re.fullmatch(r"0\d{9}", phone_clean):
            raise ValueError("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0")

        return phone_clean


def bai2_validate() -> None:
    cases = [
        # 1. Valid: phone with spaces, should be cleaned to "0901234567"
        {
            "customer_name": "Lan",
            "phone": "0901 234 567",
            "address": "12 Nguyễn Huệ Q1",
            "items": [
                {"product": "áo thun", "quantity": 2, "size": "M"},
                {"product": "quần jean", "quantity": 1, "size": "L"},
            ],
            "note": None,
        },
        # 2. Valid: phone with dots, item without size, has note
        {
            "customer_name": "Tùng",
            "phone": "0935.111.222",
            "address": "45 Lê Lợi Đà Nẵng",
            "items": [{"product": "áo polo", "quantity": 3}],
            "note": "giao giờ hành chính",
        },
        # 3. Valid: missing info (no name, phone, address); only items is required
        {
            "items": [{"product": "váy hoa", "quantity": 1}],
        },
        # 4. Wrong phone: only 6 digits
        {
            "customer_name": "Minh",
            "phone": "090123",
            "items": [{"product": "áo khoác", "quantity": 1, "size": "XL"}],
        },
        # 5. Wrong items: quantity = 0 and size not in the Literal list
        {
            "customer_name": "Hoa",
            "phone": "0912345678",
            "items": [
                {"product": "áo thun", "quantity": 0, "size": "M"},
                {"product": "quần short", "quantity": 1, "size": "XXL"},
            ],
        },
    ]

    for index, data in enumerate(cases, start=1):
        print(f"\n--- Case {index} ---")
        try:
            order = Order.model_validate(data)
            print(f"PASS: {order.customer_name}")
        except ValidationError as e:
            print("Invalid data:", e)


# ============================================================================
# Bài 3 — Ép LLM trả đúng schema (native structured output)
# ============================================================================
#
# Yêu cầu:
#   - def extract_order(text: str) -> Order | None
#     Dùng client.responses.parse(model=..., instructions=..., input=text, text_format=Order).
#     Kết quả đã được parse sẵn ở response.output_parsed (có thể là None, nhớ kiểm).
#   - Thử với 1 tin nhắn, ví dụ:
#       "Chị ơi e lấy 2 áo thun size M với 1 quần jean L nha, giao về 12 Nguyễn Huệ Q1,
#        sđt 0901 234 567, tên Lan"
#   - In model_dump_json(indent=2) để xem kết quả.
#   - Điểm cần biết (đã kiểm với SDK): ở chế độ strict, MỌI field đều bị đánh dấu bắt buộc.
#     Field được phép trống phải khai báo X | None, model sẽ trả null. Field có default
#     vẫn bắt buộc, model sẽ luôn điền giá trị.
#   - Thử 1 tin nhắn KHÔNG phải đơn hàng ("hôm nay shop mở cửa mấy giờ?"). Model trả gì?
#
# (Tùy chọn) Cách cũ hơn: tool-based extraction, khai báo Order làm 1 tool rồi đọc
# arguments. Đọc qua để biết, Buổi 7 (function calling) sẽ làm kỹ.

# TODO: viết code ở đây
client = OpenAI()

EXTRACT_INSTRUCTIONS = """\
Bạn là trợ lý của một shop quần áo online. Nhiệm vụ: đọc tin nhắn chat của khách \
và trích xuất thông tin đơn hàng theo schema được cung cấp.

Quy tắc:
1. Chỉ lấy thông tin có trong tin nhắn. Field nào khách không nhắc tới thì để null, \
không suy đoán, không bịa.
2. Mỗi sản phẩm là một item riêng. Nếu khách đổi ý giữa chừng (ví dụ "à thôi lấy size L"), \
dùng thông tin cuối cùng.
3. Số điện thoại: giữ nguyên các chữ số khách gõ, không tự thêm hay bớt số.
4. note: chỉ ghi yêu cầu của khách liên quan tới đơn hàng (giờ giao, gói quà, ...). \
Không ghi nhận xét hay giải thích của bạn vào note, \
trừ khi được yêu cầu ghi lại thông tin không hợp lệ.
5. Nếu tin nhắn KHÔNG phải đặt hàng (hỏi giờ mở cửa, hỏi giá, chào hỏi, ...): \
items để rỗng [], tất cả field còn lại là null, kể cả note.

Ví dụ tin không phải đơn hàng:
Tin nhắn: "shop ơi mấy giờ mở cửa vậy"
Kết quả: {"customer_name": null, "phone": null, "address": null, "items": [], "note": null}
"""
MODEL = "gpt-6-luna"  # hoặc "gpt-4o" nếu muốn model mạnh hơn, tốn tiền hơn


def extract_order(text: str) -> Order | None:
    response = client.responses.parse(
        model=MODEL,
        instructions=EXTRACT_INSTRUCTIONS,
        input=text,
        text_format=Order,
    )

    return response.output_parsed


def bai3_run() -> None:
    test_messages = [
        (
            "Chị ơi e lấy 2 áo thun size M với 1 quần jean L nha, giao về 12 Nguyễn Huệ Q1, sđt"
            " 0901 234 567, tên Lan"
        ),
        "shop ơi còn váy hoa ko ạ, lấy 1 cái nha, e ở Cần Thơ",
        "2 ao thun M + 1 ao khoac XL, sdt 0912 345 678, giao gio hanh chinh",
        "hôm nay shop mở cửa mấy giờ?",
    ]

    for index, message in enumerate(test_messages, start=1):
        print(f"\n--- Test Message {index} ---")
        order = extract_order(message)
        if order is not None:
            print(order.model_dump_json(indent=2))
        else:
            print("No order extracted.")


# ============================================================================
# Bài 4 — Xử lý fail: retry kèm thông báo lỗi, rồi fallback
# ============================================================================
#
# Tình huống: schema JSON không diễn tả được hết luật của bạn (ví dụ validator phone ở Bài 2).
# LLM trả đúng JSON nhưng vẫn có thể fail validator.
#
# Yêu cầu:
#   - def extract_with_retry(text: str, max_retries: int = 2) -> Order | None
#   - Gọi LLM, rồi validate kết quả bằng Order (có validator).
#     Mẹo: với responses.parse, validator chạy ngay lúc parse; lỗi validate sẽ ném ra
#     pydantic.ValidationError. Tự kiểm chứng điều này khi làm.
#   - Nếu fail: gửi lại cho model cả câu trả lời trước lẫn thông báo lỗi
#     ("Kết quả trước bị lỗi: <lỗi>. Hãy sửa lại."), tức là dùng lịch sử hội thoại như Buổi 3 bài 2.
#   - Hết số lần retry vẫn fail → fallback: return None, hoặc trả Order với phone = None
#     và ghi chú lỗi. Tự chọn và ghi lý do vào notes.md.
#   - In ra mỗi lần thử: lần thứ mấy, pass hay fail, lỗi gì.
#   - Test bằng tin nhắn có số điện thoại sai, ví dụ "sđt 090123" (thiếu số).


# TODO: viết code ở đây
def format_errors(e: ValidationError) -> str:
    error_messages = []
    for err in e.errors():
        loc = " -> ".join(str(part) for part in err.get("loc", []))
        msg = err.get("msg", "")
        error_messages.append(f"{loc} = {err.get('input')!r}: {msg}")
    return "; ".join(error_messages)


@dataclass
class ExtractResult:
    order: Order | None
    attempts: int
    input_tokens: int
    output_tokens: int


def extract_with_retry(text: str, max_retries: int = 2) -> ExtractResult:
    messages: ResponseInputParam = [{"role": "user", "content": text}]
    input_tokens = 0
    output_tokens = 0

    for attempt in range(max_retries + 1):
        response = client.responses.parse(
            model=MODEL,
            instructions=EXTRACT_INSTRUCTIONS,
            input=messages,
            text_format=OrderBase,
        )
        if response.usage is not None:
            input_tokens += response.usage.input_tokens
            output_tokens += response.usage.output_tokens
        draft = response.output_parsed
        if draft is None:
            print(f"Attempt {attempt + 1}: FAIL - No output parsed")
            return ExtractResult(
                order=None,
                attempts=attempt + 1,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        try:
            order = Order.model_validate(draft.model_dump())
            print(f"Attempt {attempt + 1}: PASS")
            return ExtractResult(
                order=order,
                attempts=attempt + 1,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        except ValidationError as pydantic_err:
            messages.extend(
                [
                    {"role": "assistant", "content": draft.model_dump_json()},
                    {
                        "role": "user",
                        "content": (
                            f"Kết quả trước bị lỗi: {format_errors(pydantic_err)}.\n"
                            "Nếu sửa được dựa trên tin nhắn của khách thì sửa lại. Nếu không sửa"
                            " được (khách gõ sai), làm đúng 2 việc:\n"
                            "1. Để field đó là null.\n"
                            "2. GIỮ NGUYÊN nội dung note cũ, nối thêm vào cuối đúng mẫu:"
                            " 'SĐT khách gõ không hợp lệ: <giá trị khách gõ>'."
                            " Nếu note cũ là null thì note chỉ gồm dòng này."
                        ),
                    },
                ]
            )
            print(f"Attempt {attempt + 1}: FAIL - {format_errors(pydantic_err)}")
    print("All retries failed. Returning None.")
    return ExtractResult(
        order=None,
        attempts=max_retries + 1,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def bai4_run() -> None:
    test_message = "2 ao thun M + 1 ao khoac XL, sdt 090123, giao gio hanh chinh"
    result = extract_with_retry(test_message)
    if result.order is not None:
        print(f"Extracted order after {result.attempts} attempts:")
        print(result.order.model_dump_json(indent=2))
        print(f"Token: in={result.input_tokens}, out={result.output_tokens}")
    else:
        print(f"No valid order extracted after {result.attempts} attempts.")


# ============================================================================
# Bài 5 — Test: 10 tin nhắn lộn xộn, đo tỉ lệ pass validation
# ============================================================================
#
# Yêu cầu:
#   - Viết list 10 tin nhắn đặt hàng. 3 tin mẫu bên dưới, tự viết thêm 7 tin, cố tình đa dạng:
#     teencode/viết tắt, thiếu thông tin, nhiều sản phẩm, số điện thoại sai, không phải đơn hàng,
#     lẫn tiếng Anh, sửa ý giữa chừng ("à thôi lấy size L").
#   - Chạy extract_with_retry cho cả 10 tin. Có thể chạy song song bằng AsyncOpenAI + gather
#     như Buổi 4 (tùy chọn).
#   - Đo và in: số tin pass ngay lần đầu, số tin pass sau retry, số tin fallback,
#     tổng token và tổng cost (dùng công thức Buổi 3).
#   - Đọc lại từng kết quả: pass validation chưa chắc là ĐÚNG
#     (ví dụ đúng format nhưng sai số lượng).
#     Tự đánh dấu đúng/sai bằng mắt, ghi tỉ lệ "pass" và tỉ lệ "đúng thật" vào notes.md.
#

# Tin mẫu:
#   "cho mình 3 cái áo polo size L, gửi về 45 Lê Lợi Đà Nẵng. Tùng 0935.111.222"
#   "shop ơi còn váy hoa ko ạ, lấy 1 cái nha, e ở Cần Thơ"
#   "2 ao thun M + 1 ao khoac XL, sdt 0912 345 678, giao gio hanh chinh"


# TODO: viết code ở đây

# Giá USD / 1M token (input, output), tra ngày 2026-09-30 (chép từ Buổi 4)
# Nguồn: developers.openai.com/api/docs/pricing
PRICES: dict[str, tuple[float, float]] = {
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-6-luna": (0.10, 0.50),
}


def cost_usd(
    input_tokens: int, output_tokens: int, price_in_per_mtok: float, price_out_per_mtok: float
) -> float:
    return (input_tokens / 1_000_000) * price_in_per_mtok + (
        output_tokens / 1_000_000
    ) * price_out_per_mtok


def result_cost(result: ExtractResult, model: str = MODEL) -> float:
    price_in, price_out = PRICES[model]
    return cost_usd(result.input_tokens, result.output_tokens, price_in, price_out)


def print_summary(results: list[ExtractResult]) -> None:
    # Phân loại theo code: có order = pass (kể cả pass nhờ để phone null), không có order = fallback
    first_pass = sum(1 for r in results if r.order is not None and r.attempts == 1)
    retry_pass = sum(1 for r in results if r.order is not None and r.attempts > 1)
    fallback = sum(1 for r in results if r.order is None)
    # Pass nhưng đơn chưa đủ: model bỏ SĐT sai và ghi vào note (luật trong tin báo lỗi Bài 4)
    phone_dropped = sum(
        1
        for r in results
        if r.order is not None and r.order.phone is None and "SĐT khách gõ" in (r.order.note or "")
    )
    total_in = sum(r.input_tokens for r in results)
    total_out = sum(r.output_tokens for r in results)
    total_cost = sum(result_cost(r) for r in results)

    print(f"\n=== Tổng kết ({len(results)} tin, model {MODEL}) ===")
    print(f"Pass ngay lần đầu: {first_pass}")
    print(f"Pass sau retry:    {retry_pass} (trong đó bỏ SĐT sai, ghi vào note: {phone_dropped})")
    print(f"Fallback:          {fallback}")
    print(f"Token: in={total_in}, out={total_out}")
    print(f"Cost:  ${total_cost:.6f}")


def bai5_run() -> None:
    order_messages = [
        "cho mình 3 cái áo polo size L, gửi về 45 Lê Lợi Đà Nẵng. Tùng 0935.111.222",
        "shop ơi còn váy hoa ko ạ, lấy 1 cái nha, e ở Cần Thơ",
        "2 ao thun M + 1 ao khoac XL, sdt 0912 345 678, giao gio hanh chinh",
        # teencode + thiếu info
        "sh oi lay e 2 cai ao thun nha, k can gap dau, ship ve nha e o Q7 nhe",
        "cho mình 2 quần jean size L, 1 áo thun size S, sdt 0912345678, giao 456 Trần Phú, HCM",
        (
            "shop ơi, mình muốn 1 váy hoa size M, nhưng à thôi lấy size L, sdt 0909876543, giao 789"
            " Nguyễn Trãi, ĐN"
        ),
        "0901 2345 áo thun M x1, 321 Lý Thường Kiệt Q10, gọi trước khi giao",  # sai sdt, đứng đầu
        (
            "cho mình 1 áo khoác size XL, 2 quần short size M, sdt 0912345678, giao 654 Phan Đình"
            " Phùng, HCM"
        ),
        (  # lẫn tiếng Anh + nhiều sản phẩm
            "hi shop, I want to order 1 hoodie size S và 1 cap nha, ship COD to 987 Lê Duẩn Q1,"
            " phone 0912345678, thanks!"
        ),
        "hôm nay shop mở cửa mấy giờ?",  # không phải đơn hàng
    ]

    results: list[ExtractResult] = []
    for index, message in enumerate(order_messages, start=1):
        print(f"\n--- Test Message {index} ---")
        result = extract_with_retry(message)
        results.append(result)
        if result.order is not None:
            print(f"Extracted order after {result.attempts} attempts:")
            print(result.order.model_dump_json(indent=2))
        else:
            print(f"No valid order extracted after {result.attempts} attempts.")
        print(f"Token: in={result.input_tokens}, out={result.output_tokens}")

    print_summary(results)


if __name__ == "__main__":
    # bai1_validate()
    # bai1_serialize()
    # bai1_schema()

    # bai2_validate()

    # bai3_run()

    # bai4_run()

    bai5_run()
