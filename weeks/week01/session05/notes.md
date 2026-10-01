# Buổi 5 — Ghi chú quan sát

## Setup (tự làm)

- [ ] **Khai báo pydantic trong `pyproject.toml`.** Pydantic đã có sẵn trong môi trường vì `openai` phụ thuộc vào nó,
      nhưng code của mình import trực tiếp thì nên khai báo trực tiếp. Dùng `uv add` như Buổi 3.
      Giống bên Node: dùng `zod` thì phải có `zod` trong `package.json`, không dựa vào việc thư viện khác kéo về.
- [ ] **Kiểm:** mở `pyproject.toml`, thấy `pydantic` trong mục `dependencies`. Chạy `uv tree --depth 1` để thấy nó
      đứng ngang hàng với `openai`.

## Bài 1 — Pydantic vs Zod

### Tóm tắt: 3 hàm, 3 nhóm chức năng

Cả 3 hàm dùng chung `Contact` / `StrictContact`, mỗi hàm demo 1 nhóm:

| Hàm | Demo cái gì | Method chính | Dùng lại ở |
|---|---|---|---|
| `bai1_validate` | **Kiểm tra dữ liệu**: dict hợp lệ không, lỗi ở field nào, strict khác lax ra sao | `model_validate(dict)`, `e.errors()` | Bài 2 (test validator phone), Bài 4 (đọc lỗi để retry) |
| `bai1_serialize` | **Chuyển đổi dữ liệu**: object ↔ dict / JSON string | `model_dump()`, `model_dump_json()`, `model_validate_json(text)` | Bài 3 (parse output LLM, in kết quả), Bài 5 (log kết quả) |
| `bai1_schema` | **Mô tả hình dạng**: class → JSON Schema để gửi cho LLM | `model_json_schema()` | Bài 3 (SDK gửi schema cho OpenAI) |

Ứng với 3 giai đoạn của 1 lần gọi LLM ở Bài 3 (`client.responses.parse(...)` gộp cả 3):

```
bai1_schema     →  gửi schema cho LLM          ("trả về JSON hình dạng này")
bai1_serialize  →  nhận text về → parse ra object; dump ra để log/lưu
bai1_validate   →  hiểu lỗi khi dữ liệu sai   (e.errors(), strict/lax)
```

### Chi tiết từng case

| Input | Kết quả | Ghi chú |
|---|---|---|
| dict hợp lệ | ✅ pass | Không có key `phone`/`email` vẫn pass vì 2 field này có default `= None` |
| thiếu name | ❌ `missing` | `loc=('name',)`, "Field required" |
| age = -5 | ❌ `greater_than_equal` | Vi phạm `Field(ge=0)`, `ctx={'ge': 0}` |
| age = "25" | ✅ pass, `age=25` (int) | Pydantic tự ép str → int (lax mode). Zod `z.number()` sẽ báo lỗi |
| age = "hai lăm" | ❌ `int_parsing` | Pydantic **có thử** parse str → int nhưng thất bại |

`X | None` vs `X | None = None`:

- `phone: str | None` (không default) = Zod `.nullable()`: bắt buộc có key, giá trị `None` được. Thiếu key → `missing`.
- `phone: str | None = None` = Zod `.optional().nullable()`: không có key cũng pass.
- Bài 3 (OpenAI strict) cần kiểu thứ nhất: mọi field bắt buộc, field được trống thì khai báo `X | None`.

Bật `strict=True` thì sao:

- **Strict = không chuyển kiểu.** Input phải đúng type ngay từ đầu. Các ràng buộc khác (`ge`/`le`, field bắt buộc)
  giữ nguyên → 3 case đầu cho kết quả giống hệt bản thường.
- `age = "25"`: ✅ pass → ❌ `int_type`. Lúc này giống Zod `z.number()`.
- `age = "hai lăm"`: `int_parsing` → `int_type`.
  - `int_parsing` = đã **thử** parse rồi thất bại (lax).
  - `int_type` = **không thử**, từ chối luôn vì sai type (strict).
  - → Nhìn mã lỗi là biết đang ở chế độ nào.
- Phạm vi: `ConfigDict(strict=True)` áp cho **cả model**, `Field(strict=True)` chỉ áp cho **1 field**.
  Ví dụ `name: b"A"` (bytes): strict cấp field (chỉ ở `age`) vẫn pass, strict cấp model báo `string_type`.
- Lax **không** phải nhận gì cũng được, chỉ chuyển khi không mất thông tin:
  - `25.0` → `25` ✅, `25.5` → ❌ `int_from_float`.
  - `int` không tự thành `str` (`phone: 901234567` → `string_type`), kể cả không strict.
  - ⚠️ Bẫy: `True` → `1` ở lax mode. LLM trả nhầm `true` vào `age` vẫn lọt qua.
- Parse output LLM: lax = dễ dãi (LLM trả `"25"` vẫn chạy), strict = bắt chặt mọi chỗ sai type nhưng dễ fail hơn.
- Cách viết: `class StrictContact(Contact)` + `model_config = ConfigDict(strict=True)` → kế thừa field,
  chỉ thêm phần khác biệt, không chép lại.

### Serialize / parse

```
dict        ── model_validate ──────▶  object  ── model_dump ──────▶  dict
JSON string ── model_validate_json ─▶  object  ── model_dump_json ─▶  JSON string
```

- Mẹo nhớ: có đuôi `_json` → đầu kia là JSON string, không có → dict.
- `model_validate*` gọi trên **class** (`Contact.…`), `model_dump*` gọi trên **object** (`contact.…`).
  Gọi `Contact.model_dump(dict)` → `AttributeError: 'dict' object has no attribute '__pydantic_serializer__'`.
- Vì sao cần: dữ liệu vào/ra chương trình luôn là **text** (LLM trả về, file, API), còn trong code thì làm việc
  với **object** đã kiểm. `model_validate_json` = cổng vào, `model_dump_json` = cổng ra.
  OpenAI SDK `responses.parse(text_format=...)` bên trong gọi đúng `model_validate_json`
  (`openai/_compat.py:178`).

**Phần A — object → dict / JSON string:**

- `model_dump()` → `<class 'dict'>`, `None` vẫn là `None` (Python).
- `model_dump_json()` → `<class 'str'>`, `None` thành `null` (JSON), không có dấu cách. `indent=2` để in đẹp.
- Không `json.dumps(contact)` được → `TypeError: Object of type Contact is not JSON serializable`.
  Muốn lưu/log/gửi object thì phải `model_dump_json()`.

**Phần B — JSON string → object (`model_validate_json`):**

| JSON | `Contact` | `StrictContact` |
|---|---|---|
| `{"name": ..., "age": 25}` | ✅ pass | ✅ pass |
| `{"name": ..., "age": "25"}` | ✅ pass, `age=25` | ❌ `int_type` |
| `{"name": ..., "age": 25,}` (thừa dấu phẩy) | ❌ `json_invalid` | ❌ `json_invalid` |

- `"25"` từ JSON: cư xử **giống hệt** lúc dùng dict ở bước 2–3 (lax ép kiểu, strict từ chối).
- `json_invalid` vẫn là **`ValidationError`**, `msg`: "Invalid JSON: trailing comma at line 1 column 36".
- `loc=()` rỗng vì lỗi xảy ra ở bước parse cú pháp JSON, **trước khi** đọc ra được field nào → không có field để
  trỏ tới, lỗi thuộc về cả input.
- Lợi ích: 1 `except ValidationError` bắt được cả JSON hỏng lẫn dữ liệu sai. Nếu tách 2 bước
  `json.loads` + `model_validate` thì JSON hỏng ném `json.JSONDecodeError` (không phải `ValidationError`)
  → phải viết 2 nhánh `except`. Quan trọng cho Bài 4 (retry).

### JSON Schema (`Contact.model_json_schema()`)

- JSON Schema = bản mô tả **hình dạng** dữ liệu, viết bằng JSON (giống `type Contact = {...}` của TS nhưng ở dạng
  data). Gọi trên **class**, không cần data. Bài 3: SDK gửi schema này cho OpenAI **trước khi có data**, LLM đọc
  rồi sinh ra JSON khớp với nó.
- In bằng `json.dumps(schema, indent=2)`: `print(dict)` thẳng ra cú pháp Python (`None`, nháy đơn), không phải JSON.

| Code Python | Key trong JSON Schema |
|---|---|
| `name: str` | `"type": "string"` |
| `str \| None` | `"anyOf": [{"type": "string"}, {"type": "null"}]` (= "một trong các kiểu") |
| `= None` | `"default": null` |
| tên field `phone` | `"title": "Phone"` (tự sinh, viết hoa chữ đầu) |
| `Field(ge=0, le=150)` | `"minimum": 0`, `"maximum": 150` (có tính bằng) |
| *(thêm)* `Field(gt=0, lt=150)` | `"exclusiveMinimum": 0`, `"exclusiveMaximum": 150` (không tính bằng) |

- `"required": ["name", "age"]` → quy luật: **có default → không required, không default → required.**
  Bài 3 (OpenAI strict) mọi field đều bị bắt buộc → field được trống phải khai báo `X | None`.
- `Contact` vs `StrictContact`: schema **chỉ khác `title`**, không có key nào về strict.
  → **LLM không biết model đang strict.** Strict chỉ có tác dụng ở bước Python validate sau khi nhận JSON về.
- Phân biệt:
  - **Nằm trong schema** (type, `required`, `minimum`/`maximum`, sau này `description`) → LLM **thấy**.
  - **Chỉ nằm trong Python** (`strict`, `@field_validator` ở Bài 2) → LLM **không thấy** → Python phải tự bắt lỗi
    → lý do Bài 4 cần retry.

## Bài 2 — Schema đơn hàng

-

## Bài 3 — Structured output

Kết quả với tin nhắn mẫu:

Tin nhắn không phải đơn hàng thì model trả gì:

-

## Bài 4 — Retry + fallback

Chọn fallback nào, vì sao:

-

## Bài 5 — 10 tin nhắn

| Chỉ số | Giá trị |
|---|---|
| Pass ngay lần đầu | |
| Pass sau retry | |
| Fallback | |
| Đúng thật (tự kiểm bằng mắt) | |
| Tổng token | |
| Tổng cost | |

Tin nào khó nhất, vì sao:

-
