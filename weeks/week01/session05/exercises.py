import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

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


class Order(BaseModel):
    customer_name: str | None = Field(description="Tên khách hàng", default=None)
    phone: str | None = Field(description="Số điện thoại", default=None)
    address: str | None = Field(description="Địa chỉ", default=None)
    items: list[OrderItem] = Field(description="Danh sách sản phẩm")
    note: str | None = Field(description="Ghi chú", default=None)

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


if __name__ == "__main__":
    # bai1_validate()
    # bai1_serialize()
    # bai1_schema()

    bai2_validate()
