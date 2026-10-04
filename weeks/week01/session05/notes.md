# Buổi 5 — Ghi chú quan sát

## Setup (tự làm)

- [x] **Khai báo pydantic trong `pyproject.toml`.** Pydantic đã có sẵn trong môi trường vì `openai` phụ thuộc vào nó,
      nhưng code của mình import trực tiếp thì nên khai báo trực tiếp. Dùng `uv add` như Buổi 3.
      Giống bên Node: dùng `zod` thì phải có `zod` trong `package.json`, không dựa vào việc thư viện khác kéo về.
- [x] **Kiểm:** mở `pyproject.toml`, thấy `pydantic` trong mục `dependencies`. Chạy `uv tree --depth 1` để thấy nó
      đứng ngang hàng với `openai`.
      → `pyproject.toml` có `pydantic>=2.13.5`; `uv tree --depth 1` ra `pydantic v2.13.5` ngang hàng `openai v3.19.2`.

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

- `OrderItem`: `product`, `quantity: int = Field(ge=1)`, `size: Literal["S", "M", "L", "XL"] | None`.
- `Order`: `customer_name`, `phone`, `address`, `note` đều `str | None`; `items: list[OrderItem]` là field bắt buộc duy nhất.
  (Bài 4 tách thành `OrderBase` chứa field + `Order(OrderBase)` chỉ thêm validator.)
- Mỗi field có `Field(description=...)` tiếng Việt → nằm trong JSON schema gửi LLM, nên **description cũng là prompt**.
- `@field_validator("phone")` + `@classmethod`: `None` cho qua; làm sạch bằng `re.sub(r"[\s.\-]", "", value)` rồi kiểm
  `re.fullmatch(r"0\d{9}", ...)`; sai thì `raise ValueError(...)`; đúng thì **trả về số đã làm sạch** → giá trị trả về của
  validator thay giá trị field (`"0901 234 567"` → `"0901234567"`).

Kết quả `bai2_validate()` (5 dict viết tay):

| Case | Input | Kết quả |
|---|---|---|
| 1 | phone `"0901 234 567"`, 2 món có size | ✅ pass, phone thành `0901234567` |
| 2 | phone `"0935.111.222"`, món không size, có note | ✅ pass |
| 3 | chỉ có `items` | ✅ pass (các field khác mặc định `None`) |
| 4 | phone `"090123"` | ❌ `value_error`, `loc=phone`: "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0" |
| 5 | `quantity=0` + `size="XXL"` | ❌ 2 lỗi cùng lúc: `items.0.quantity` (`greater_than_equal`), `items.1.size` (`literal_error`) |

- Lỗi trong list lồng nhau có `loc` chỉ đúng vị trí: `items.0.quantity`, `items.1.size` → biết món thứ mấy sai field nào.
- Pydantic gom **tất cả** lỗi trong 1 lần validate, không dừng ở lỗi đầu tiên → 1 `ValidationError` chứa 2 lỗi.
- Lỗi do `raise ValueError` trong validator có `type=value_error`, msg tự thêm tiền tố "Value error, ".
- `Field(ge=1)` và `Literal` nằm trong schema (LLM thấy); validator phone chỉ nằm trong Python (LLM không thấy) → Bài 4.

## Bài 3 — Structured output

- `client.responses.parse(..., text_format=Order)`: truyền thẳng class, SDK tự đổi sang JSON schema strict.
  Kết quả đã là object `Order` ở `response.output_parsed`, không cần `model_validate` lại.
- `output_parsed` có thể là `None` → kiểm trước khi gọi `model_dump_json()`.

Kết quả với tin nhắn mẫu (`gpt-4o-mini`, prompt mới):

| # | Tin | Kết quả | Ghi chú |
|---|---|---|---|
| 1 | Lan, 2 áo thun M + 1 quần jean L, "0901 234 567" | ✅ đúng hết | `phone="0901234567"`, đã mất dấu cách |
| 2 | "còn váy hoa ko ạ, lấy 1 cái, e ở Cần Thơ" | ✅ pass | `address="Cần Thơ"`: chỉ là tỉnh, chưa đủ để giao. Pass ≠ đúng → Bài 5 |
| 3 | không dấu: "2 ao thun M + 1 ao khoac XL..." | ✅ pass | Model tự thêm dấu: "áo khoác", "giờ hành chính" |
| 4 | "hôm nay shop mở cửa mấy giờ?" | toàn null, `items=[]` | Xem bên dưới |

- `gpt-4o-mini` và `gpt-6-luna` cho kết quả giống nhau với các tin này.

Tin nhắn không phải đơn hàng thì model trả gì:

- **Prompt cũ** ("nếu không phải đơn hàng, trả về null") →
  `items=[]`, các field null, nhưng `note='Không phải đơn hàng: hỏi giờ mở cửa của shop.'`
- Vì sao: **strict mode bắt model luôn trả 1 object `Order` khớp schema**, không trả `null` cho cả object được.
  Prompt đòi điều schema không cho → model tìm đường gần nhất: nhét lời giải thích vào `note`.
  → **Prompt mâu thuẫn với schema thì schema thắng**, phần prompt bị "bẻ" theo cách khó đoán.
- Hậu quả nếu lưu thẳng: đơn rỗng với ghi chú giao hàng "Không phải đơn hàng..."; muốn phát hiện phải đọc câu chữ.
- **Prompt mới** (`EXTRACT_INSTRUCTIONS`): nói rõ không phải đơn → `items=[]`, mọi field null kể cả `note`;
  `note` chỉ chứa yêu cầu của khách; kèm 1 ví dụ JSON. → Kết quả toàn null, `note=None`. Tin đặt hàng không bị ảnh hưởng.
- Chọn sửa prompt (không sửa schema): nhanh, không đụng Bài 2.
- ⚠️ Hạn chế: quy ước `items == []` = "không phải đơn" **không phân biệt được** với đơn thiếu món
  ("gửi về 12 Nguyễn Huệ, sđt 0901..." mà quên ghi món). Hai ca cần xử lý khác nhau (hỏi lại khách vs trả lời câu hỏi).
  Cách khác nếu cần: thêm field riêng kiểu `is_order: bool` đặt **đầu** class (model sinh JSON theo thứ tự field,
  quyết định trước rồi mới điền). Không nên ép `items` ≥ 1 phần tử: tin không phải đơn sẽ buộc model bịa ra món.

Phone `"0901234567"` do ai làm sạch, model hay validator?

- **Validator.** So `response.output_text` (JSON thô) với `output_parsed`, 3 lần chạy `gpt-4o-mini`:
  raw `"0901 234 567"` → parsed `"0901234567"`. Model giữ nguyên dấu cách như khách gõ (đúng quy tắc 3),
  `validate_phone` làm sạch.
- → **`@field_validator` chạy ngay bên trong `responses.parse`** (SDK gọi `model_validate_json`).
  Phone sai (`090123`) sẽ làm `parse` ném `ValidationError` luôn, không trả object → Bài 4 phải `try/except` quanh lời gọi.
- `output_text` = JSON thô LLM sinh ra, chưa qua Pydantic. Muốn biết model "thật sự" trả gì thì xem cái này.

## Bài 4 — Retry + fallback

### Vì sao phải tách schema (`OrderBase` / `Order`)

- `text_format=Order` → validator chạy **bên trong** `parse` → phone sai làm `parse` ném `ValidationError`,
  biến `response` không bao giờ được gán → **mất câu trả lời của model**, không gửi lại được để retry.
  Lời gọi `parse` đầu tiên nằm ngoài `try` → crash luôn.
- Cách làm: tách 2 tầng, giống `StrictContact(Contact)` ở Bài 1:
  - `OrderBase(BaseModel)`: 5 field, **không** validator → dùng làm `text_format`, `parse` luôn thành công.
  - `Order(OrderBase)`: chỉ thêm `@field_validator("phone")` → tự validate bằng Python, lỗi nằm trong `try`.
  - Field khai báo 1 lần, Bài 2–3 vẫn dùng `Order` không phải sửa.
  - Schema 2 class giống nhau (trừ `title`) → LLM không thấy validator (đúng như ghi chú Bài 1).
- Luồng mỗi lần thử: `parse(text_format=OrderBase)` → `draft` → `Order.model_validate(draft.model_dump())`
  → pass thì trả về / fail thì thêm vào lịch sử rồi thử lại.

### Bẫy gặp phải

- `Order.model_validate(<object>)` **không chạy validator**: object đã là `Order` thì Pydantic tin là hợp lệ, trả về
  luôn (test: `phone='090123'` lọt qua). Object `OrderBase` (class cha) thì không phải `Order` → lỗi.
  → Phải đưa vào **dict**: `draft.model_dump()`.
- `messages = messages.extend([...])` → `messages` thành `None`. `append` / `extend` / `sort` sửa list tại chỗ và
  trả về `None` → chỉ gọi `messages.extend(...)`, không gán lại. pyright bắt được nhờ khai báo `messages: ResponseInputParam`.
- Lịch sử hội thoại: `[user: tin khách]` → mỗi lần fail thêm `assistant: draft.model_dump_json()` +
  `user: "Kết quả trước bị lỗi: ... Hãy sửa lại."`. `instructions=` thay cho message `system`.
- (Editor) `source.fixAll.ruff` khi save xóa import không dùng (F401): cắt validator rồi save trước khi dán →
  mất `import re` và `field_validator`. Chặn bằng `unfixable = ["F401"]` nếu muốn.

### Quan sát: model "sửa" lỗi thế nào

Tin test: `"2 ao thun M + 1 ao khoac XL, sdt 090123, giao gio hanh chinh"`, `max_retries=2` (tối đa 3 lần).

| Lần chạy | gpt-6-luna | gpt-4o-mini |
|---|---|---|
| 1 | FAIL, FAIL, **PASS lần 3** (`phone=None`) | FAIL, **PASS lần 2** (`phone=None`) |
| 2 | FAIL, FAIL, FAIL → **fallback `None`** | FAIL, **PASS lần 2** (`phone=None`) |
| 3 | FAIL, **PASS lần 2** (`phone=None`) | FAIL, **PASS lần 2** (`phone=None`) |

- Dự đoán trước: model chỉ có 2 đường, giữ `090123` (fail mãi) hoặc bịa thêm số (pass nhưng sai).
  Thực tế có **đường thứ 3: đổi `phone` thành `null`** → validator cho qua (`if value is None: return None`).
- ⚠️ **Pass ≠ đúng**: khách **có** gửi số (chỉ gõ thiếu), giờ đơn trông như khách không gửi số. `note` không còn dấu vết
  `090123` → shop không biết để hỏi lại. Code đếm là "pass sau retry", y như sửa thành công thật.
  Model tìm cách **rẻ nhất để qua validator**, không phải sửa lỗi. Prompt cấm bịa số, schema cho `null` → chọn `null`.
- **Không lần nào bịa số** ở cả 2 model → quy tắc 3 trong prompt có tác dụng.
- **Cùng model, mỗi lần chạy khác nhau** (luna: pass lần 3 / fallback / pass lần 2). Không truyền `temperature` →
  sinh token có ngẫu nhiên. Muốn biết xu hướng phải chạy nhiều lần.
- **Khác model, cư xử khác**: 4o-mini bỏ cuộc ngay sau lỗi đầu (đổi sang `null`), luna giữ lâu hơn và có lúc rơi vào fallback.
  - Giả thuyết (**chưa kiểm chứng đủ**): luna theo quy tắc 3 chặt hơn nên giữ `090123` lâu hơn.
    Sau khi `format_errors` in `input`, log lần fail đều là `phone = '090123'`, nhưng đợt chạy đó cả 2 model đều
    sửa ở lần 2 (tin báo lỗi đã nói rõ cách xử lý) → chưa thấy lại hành vi "giữ lâu".
  - → Tỉ lệ pass / fallback ở Bài 5 phụ thuộc model; ghi rõ model khi ghi số liệu.
- Retry giúp được lỗi **model đọc sai/định dạng sai**. Lỗi do **khách gõ sai** (số thiếu) thì model không thể biết số đúng
  → retry chỉ đẩy model tới chỗ bỏ trống hoặc bịa.

### Sửa tin báo lỗi để giữ lại số khách gõ

3 phiên bản tin báo lỗi (cùng tin `090123`, mỗi model 3 lần):

| Phiên bản | Tin báo lỗi | Kết quả |
|---|---|---|
| v1 | `"Kết quả trước bị lỗi: {str(e)}. Hãy sửa lại."` | `phone=None`, note **không có** `090123`. luna có lần fail cả 3 → fallback |
| v2 | "...Nếu không thể sửa, hãy để field đó là null." | 6/6 pass lần 2, `phone=None`, note **không có** `090123` → mất thông tin 100% |
| v3 | "...để null **và cập nhật vào note**" | 6/6 note có nhắc SĐT sai, nhưng chỉ **2/6** có `090123`; 4o-mini **ghi đè** note khách 2/3 lần; mỗi lần 1 format |
| v4 | Có `input` trong lỗi + "giữ nguyên note cũ, nối thêm đúng mẫu `'SĐT khách gõ không hợp lệ: <giá trị>'`" + quy tắc 4 thêm ngoại lệ | luna **3/3 đúng**, giống hệt nhau. 4o-mini 3/3 có `090123` nhưng **1/3 vẫn mất** "giao giờ hành chính" |

- v4 so với v3: chỉ dẫn mơ hồ ("cập nhật vào note") → model tự diễn giải, mỗi lần một kiểu. Nói rõ **ghi gì, mẫu nào,
  giữ hay xóa cái cũ** → ổn định hơn hẳn.
- `format_errors` phải có `input`: tin báo lỗi nhắc lại `'090123'` thì model không phải tự tìm lại trong câu trả lời trước.
- Prompt và tin báo lỗi phải khớp nhau: quy tắc 4 cấm ghi nhận xét vào note → phải thêm ngoại lệ, không thì 2 chỉ dẫn mâu thuẫn.
- Tin số đúng (Lan): PASS lần 1 ở cả 2 model → sửa tin báo lỗi không ảnh hưởng ca bình thường.
- **Giới hạn của cách sửa prompt**: tốt lên nhiều nhưng không 100% (4o-mini vẫn ghi đè 1/3). Muốn chắc chắn → để **code**
  tự ghi: lưu `input` của lỗi phone từ lần fail đầu, rồi ở cả lối ra PASS (nếu `phone is None`) lẫn fallback,
  gán `phone=None` + nối vào `note`. Code có sẵn dữ liệu trong `e.errors()`, không phụ thuộc model nghe lời.
- Mẫu `'SĐT khách gõ không hợp lệ'` đang viết riêng cho phone; thêm validator khác thì phải tổng quát hóa tin báo lỗi.

Chọn fallback nào, vì sao:

- **Lỗi không sửa được (khách gõ sai) → giữ đơn, `phone = None`, ghi số khách gõ vào `note`** (do model làm theo tin
  báo lỗi v4). Lý do: đơn vẫn có giá trị (đủ món, có ghi chú giao hàng), shop chỉ cần nhắn hỏi lại số;
  bỏ cả đơn (`return None`) là mất khách vì 1 field.
- **Hết số lần thử vẫn fail / `output_parsed is None` → `return None`**. Hiếm gặp sau v4; nếu gặp thì không có kết quả
  đáng tin để giữ.
- Đánh đổi: `note` giờ lẫn yêu cầu khách + ghi chú hệ thống. Sạch hơn là thêm field riêng (ví dụ `warnings: list[str]`),
  nhưng phải đổi schema → để sau.

## Bài 5 — 10 tin nhắn

### Cách đo

- `extract_with_retry` trả `ExtractResult(order, attempts, input_tokens, output_tokens)` thay vì `Order | None`
  (giống `Measurement` Buổi 4) → bên ngoài biết số lần gọi LLM và token **cộng dồn qua mọi lần thử** của 1 tin.
  Token cộng ngay sau `parse`, trước mọi `return` → lần gọi bị từ chối cũng được tính tiền.
- Cost: `PRICES` + `cost_usd` chép từ Buổi 4 (giá tra 2026-09-30), `result_cost(result)` tra giá theo `MODEL`.
  ⚠️ `model: str = MODEL` là default chốt lúc định nghĩa hàm → đổi `MODEL` lúc runtime thì phải truyền model rõ ràng.
- Phân loại (theo code): pass ngay = có order + `attempts == 1`; pass sau retry = có order + `attempts > 1`;
  fallback = `order is None`. Đếm riêng "pass nhưng bỏ SĐT sai, ghi vào note" vì đó là đơn chưa đủ, shop phải hỏi lại.

### Kết quả (`gpt-6-luna`)

| Chỉ số | Giá trị |
|---|---|
| Pass ngay lần đầu | 9/10 |
| Pass sau retry | 1/10 (tin 7, bỏ SĐT sai và ghi vào note) |
| Fallback | 0/10 |
| Trích xuất đúng thật (so với tin gốc) | 10/10 |
| Đơn đủ thông tin để giao (SĐT hợp lệ + địa chỉ cụ thể + có món) | 5/10 (tin 1, 5, 6, 8, 9) |
| Tổng token | in = 7483, out = 1225 |
| Tổng cost | $0.001361 (~$0.000136 / tin) |

- 2 lần chạy cho cùng phân loại (9 / 1 / 0). Token, cost lấy từ lần 1; bảng từng tin bên dưới lấy từ lần 2.
- Ước tính: 1000 tin/ngày ≈ $0.14/ngày ≈ $4/tháng với luna.
- Đánh giá đúng/sai do Claude chấm theo tiêu chí bên dưới, **cần tự duyệt lại**.

| # | Tình huống | Lần thử | Model trích ra | Trích đúng? | Đủ để giao? |
|---|---|---|---|---|---|
| 1 | mẫu: đủ thông tin | PASS 1 | Tùng, `0935111222`, 45 Lê Lợi Đà Nẵng, 3 áo polo L | ✅ | ✅ |
| 2 | mẫu: "e ở Cần Thơ" | PASS 1 | `address: "Cần Thơ"`, 1 váy hoa, size null | ✅ | ❌ chỉ có tỉnh, không SĐT |
| 3 | mẫu: không dấu | PASS 1 | `0912345678`, 2 áo thun M + 1 áo khoác XL, note "Giao giờ hành chính" | ✅ | ❌ không địa chỉ |
| 4 | teencode + thiếu info | PASS 1 | `address: "Q7"`, 2 áo thun size null, note "Không cần giao gấp" | ✅ | ❌ chỉ có quận, không SĐT |
| 5 | nhiều món | PASS 1 | 2 quần jean L + 1 áo thun S, 456 Trần Phú HCM | ✅ | ✅ |
| 6 | đổi ý "à thôi lấy size L" | PASS 1 | 1 váy hoa **L** | ✅ | ✅ |
| 7 | SĐT sai, đứng đầu, dính món | FAIL → PASS | `phone: null`, note "Gọi trước khi giao\nSĐT khách gõ không hợp lệ: 0901 2345" | ✅ | ❌ phải hỏi lại SĐT |
| 8 | nhiều món | PASS 1 | 1 áo khoác XL + 2 quần short M | ✅ | ✅ |
| 9 | lẫn tiếng Anh | PASS 1 | 1 hoodie S + 1 cap (size null), note "Ship COD" | ✅ | ✅ |
| 10 | không phải đơn | PASS 1 | toàn null, `items: []` | ✅ | (không áp dụng) |

### Nhận xét

- **"Pass" bị đếm cao hơn thực tế**: tin 10 không phải đơn nhưng vẫn tính "pass ngay" (hạn chế `items == []` ở Bài 3).
  Tin 7 tính "pass sau retry" dù đơn chưa dùng được. → Pass 10/10, nhưng **dùng được ngay chỉ 5/10**.
- **3 mức khác nhau**: pass validation (schema + validator) ≠ trích đúng (khớp tin gốc) ≠ đủ để xử lý (nghiệp vụ).
  Validator chỉ bắt được mức 1. Tin 2, 4 trích **đúng** (model không bịa, đúng quy tắc 1) nhưng đơn **không đủ**:
  đó là việc của logic nghiệp vụ (ví dụ kiểm thiếu SĐT/địa chỉ → nhắn hỏi lại), không phải của LLM.
- Model làm tốt: đổi ý giữa chừng (tin 6), tách SĐT sai dính liền món (tin 7), không bịa size (tin 2, 4, 9),
  hiểu teencode (tin 4), giữ nguyên tên món tiếng Anh (tin 9).
- **Cost do prompt + schema quyết định**: tin khách ~30 token, nhưng 1 lần gọi ~650 token input
  (`EXTRACT_INSTRUCTIONS` + JSON schema có `description`, gửi lại mỗi lần). Retry gửi lại cả lịch sử
  → tin `090123` (Bài 4): 2 lần gọi = 1511 token in, so với 660 khi pass ngay. Muốn giảm cost: rút gọn prompt/schema.
- Bộ test còn dễ: luna trích đúng 10/10. Muốn thử khó hơn: `+84 901 234 567` (số **thật, hợp lệ** nhưng validator
  từ chối → lỗi do validator chứ không phải do khách), 2 SĐT trong 1 tin, số lượng bằng chữ ("hai cái"), đổi món chứ không chỉ đổi size.

Tin nào khó nhất, vì sao:

- **Tin 7** (`"0901 2345 áo thun M x1, ..."`): SĐT sai nằm đầu câu, dính liền tên món, không có chữ "sđt" đánh dấu.
  Là tin duy nhất cần retry. Model vẫn tách đúng số khỏi món và giữ được note "gọi trước khi giao".
- Khó theo nghĩa nghiệp vụ: **tin 2, 4** (địa chỉ chỉ có tỉnh/quận). Pass và trích đúng, nhưng hệ thống không
  tự nhận ra đơn chưa giao được.
