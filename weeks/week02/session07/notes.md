# Buổi 7 — Function Calling / Tool Use (2h)

| Phần                                      | Thời lượng | Làm ở đâu      |
| ----------------------------------------- | ---------- | -------------- |
| Setup + đọc docs function calling         | ~15ph      | mục Setup      |
| Bài 1–2: 1 tool thủ công → vòng lặp + CSV | ~50ph      | `exercises.py` |
| Bài 3–4: parallel calls + xử lý lỗi       | ~40ph      | `exercises.py` |
| Bài 5: gắn vào CLI chatbot + đo token     | ~15ph      | `exercises.py` |

Bài 5 không kịp thì để buổi sau, Bài 1–4 là phần cốt lõi của checklist Notion.

## Setup (tự làm)

- [x] **Khai báo `httpx2` trong `pyproject.toml`** bằng `uv add` (như `pydantic` ở Buổi 5).
      `httpx2` là HTTP client mà `openai` đang dùng bên trong (bản fork `httpx` do team Pydantic giữ),
      nên đã có sẵn trong môi trường, chỉ thiếu khai báo trực tiếp. Giống bên Node: dùng `undici`
      thì phải có trong `package.json`, không dựa vào việc SDK khác kéo về.
      Có cả API sync (`httpx2.get(...)`, ~ `fetch` có `await` sẵn) lẫn async (`httpx2.AsyncClient`).
- [x] **Kiểm:** `uv tree --depth 1` thấy `httpx2` đứng ngang hàng `openai`. Gọi thử:
      `uv run python -c "import httpx2; print(httpx2.get('https://api.open-meteo.com/v1/forecast', params={'latitude': 21.03, 'longitude': 105.85, 'current': 'temperature_2m'}).json()['current'])"`
      → ra dict có `temperature_2m`.
- [x] Đọc nhanh docs: https://developers.openai.com/api/docs/guides/function-calling
      (phần định nghĩa function, vòng lặp gọi tool, strict mode, parallel function calling).

Không cần key mới: Open-Meteo miễn phí, không cần đăng ký. Dữ liệu CSV: `orders.csv` cùng thư mục
(15 đơn, khách An / Bình / Chi / Dũng / Em, 4 trạng thái).

## Nợ từ Buổi 6 (làm lúc rảnh, không chặn Buổi 7)

- [ ] `session06/notes.md` mục A: "Bản của mình" Pretraining / SFT / RLHF (viết từ trí nhớ)
- [ ] `session06/notes.md` mục B: bảng Prompt / RAG / Fine-tune
- [ ] `session06/notes.md` mục Bài 1: ghi quan sát
- [ ] Nhật ký Tuần 1 trên Notion (2–3 dòng "học được gì / vướng gì")

## Bài 1 — 1 tool, 1 vòng thủ công

_(Claude viết, 2026-10-06, chạy thật `run_bai1` với `gpt-6-luna`, câu "Hà Nội bây giờ bao nhiêu độ?")_

Luồng đã chạy:

```
→ get_weather({'city': 'Hà Nội'})
← {'city': 'Hà Nội', 'temperature_c': 22.4, 'condition': 'trời quang', 'observed_at': '2026-10-06 23:00'}
RESPONSE:  Hà Nội hiện khoảng 22,4°C, trời quang.
```

Output của tool (`WeatherResponse`) được rút gọn từ JSON thô của Open-Meteo:

- Chỉ giữ `city`, `temperature_c`, `condition`, `observed_at`. Bỏ `elevation`, `generationtime_ms`,
  `current_units`... vì LLM không cần, chỉ tốn input token.
- `timezone=Asia/Ho_Chi_Minh` trong `params`: không có thì `time` là giờ GMT (lệch 7 tiếng).
- `weather_code` là mã WMO (vd `81`), đổi sang chữ bằng `WMO_CODES` ("mưa rào"), không để LLM tự đoán.

Các item trong `response.output` lần 1 (type, có những field gì):

- Chỉ **1 item**, `type='function_call'`. Không có item `reasoning` (`reasoning_tokens=0`): câu đơn giản.
- Field: `name='get_weather'`, `arguments='{"city":"Hà Nội"}'`, `call_id='call_...'`, `id='fc_...'`,
  `status='completed'`.
- Có **2 ID khác nhau**: `call_id` dùng để ghép với `function_call_output`; `id` là ID của item, không
  dùng để ghép.
- `response.output_text` = `''`: lần 1 model chưa trả lời gì, chỉ yêu cầu gọi tool.
- `status='completed'` là item `function_call` đã sinh xong, KHÔNG có nghĩa tool đã chạy.

`arguments` là kiểu gì:

- `str` chứa JSON, không phải dict → `json.loads(call.arguments)` rồi `get_weather(**args)`.
- Nhờ `strict` + `enum`, giá trị `"Hà Nội"` khớp đúng key trong `CITIES`.
- `json.loads` trả `Any` nên pyright không kiểm `**args`: nếu LLM trả thành phố lạ thì chỉ lỗi lúc chạy
  (`KeyError`) → xử lý ở Bài 4c.

Lần 2 có cần gửi lại câu hỏi user không, vì sao:

- Có. API không nhớ gì giữa các lần gọi (giống Buổi 3, Buổi 6). Input lần 2 là cả đoạn hội thoại:

  ```
  user:   "Hà Nội bây giờ bao nhiêu độ?"
  model:  function_call         get_weather(city="Hà Nội")   ← input_list += response.output
  mình:   function_call_output  {22.4°C, trời quang}          ← input_list.append({...})
  ```

- `function_call` là "câu hỏi" của model, `function_call_output` là "câu trả lời" của mình, `call_id`
  nối 2 cái. Luôn đi thành cặp (Bài 5 cắt lịch sử cũng phải cắt nguyên cặp).

Thiếu `call_id` / thiếu item `function_call` thì sao:

- Bỏ dòng `input_list += response.output`, chỉ gửi `function_call_output` → **400**:
  `No tool call found for function call output with call_id call_...`
- Lỗi y vậy kể cả khi lần 2 không truyền `tools`. `tools` là "menu" tool **được gọi tiếp** (tương lai),
  còn item `function_call` là **lịch sử** đã gọi (quá khứ). Bỏ cái này không thay được cái kia.

`tools` ở lần gọi thứ 2 có cần không:

| Câu hỏi                                 | Lần 2 có `tools` | Input token lần 2 | Kết quả                                                    |
| --------------------------------------- | ---------------- | ----------------- | ---------------------------------------------------------- |
| "Hà Nội bây giờ bao nhiêu độ?"          | Có               | 147               | "Hà Nội hiện khoảng 22,4°C, trời quang."                   |
| như trên                                | Không            | 74                | Giống hệt                                                  |
| "... So sánh luôn với Đà Nẵng."         | Có               | 158               | Gọi tiếp `function_call` cho Đà Nẵng                       |
| như trên                                | Không            | 85                | "Mình đang kiểm tra Đà Nẵng..." rồi "chưa lấy được dữ liệu" |

(Thử với `parallel_tool_calls=False` để lần 1 chỉ gọi Hà Nội.)

- Câu cần 1 lượt tool: bỏ `tools` ở lần 2 tiết kiệm ~73 token, kết quả như nhau.
- Câu cần gọi thêm tool: không có `tools` thì model **trả lời dở dang và hứa suông**, API không báo lỗi gì.
- → Bài 1 bỏ được. Từ Bài 2 (vòng lặp) phải truyền `tools` ở **mọi** lần gọi, vì không biết trước lần
  nào là cuối. `instructions` cũng vậy: API không nhớ, lần nào cũng phải gửi.

Hỏi "Thủ đô của Pháp là gì?" có gọi tool không:

- Không. `response.output` = `['message']`, `output_text` = "Thủ đô của Pháp là Paris." → đi nhánh
  `if not calls: print(...); return`.
- Nhưng input vẫn **88 token** (câu Hà Nội: 90): tool schema được gửi ở mọi lời gọi có `tools`, dù model
  có dùng tool hay không (giống system prompt Buổi 6).

Số lời gọi API + token mỗi lần chạy:

- 2 lời gọi OpenAI + 1 HTTP Open-Meteo.
- Lần 1: ~90 input / 20 output. Lần 2: 147 input nếu có `tools`, 74 nếu không.
- Câu hỏi chỉ ~10 token → phần lớn input lần 1 là tool schema + khung (ước đoán, đo chính xác ở Bài 5).

Bẫy kiểu dữ liệu khi ghép `response.output` vào `input_list`:

- `response.output` là list object Pydantic (đồ **trả về**), `ResponseInputParam` là list TypedDict (đồ
  **gửi lên**) → pyright báo lỗi (`list` invariant, như Buổi 3) dù chạy vẫn đúng.
- Đã thử 4 cách:

  | Cách                                 | Pyright | Chạy thật                                         |
  | ------------------------------------ | ------- | ------------------------------------------------- |
  | `input_list += response.output`      | ❌      | ✅                                                |
  | `input_list.extend(response.output)` | ❌      | ✅                                                |
  | `[i.model_dump() for i in ...]`      | ❌      | ❌ 400 `Unknown parameter: 'input[1].async_'`     |
  | `cast(ResponseInputParam, ...)`      | ✅      | ✅                                                |

- `model_dump()` hỏng vì `async` là từ khóa Python nên SDK đặt tên field `async_`, API chỉ hiểu `async`.
- `cast` không làm gì lúc chạy, chỉ bảo pyright "tin tôi" (~ `as` bên TS) → chỉ dùng khi đã kiểm chắc.

Các lỗi gặp khi khai báo tool:

- `from ast import List`: IDE auto-import nhầm (`ast.List` là node cú pháp) → dùng `list[...]`.
- `ChatCompletionToolParam` (`openai.types.chat`) là kiểu của **Chat Completions**, lồng thêm lớp
  `"function": {...}` → Responses API dùng `FunctionToolParam` (`openai.types.responses`), dạng phẳng.
- `"strict": True` đặt trong `parameters` là sai cấp: `strict` là cài đặt của tool (ngang `name`),
  `additionalProperties` mới là luật của JSON Schema (trong `parameters`).
- Dict không khai kiểu → pyright suy ra `dict[str, ...]`, không thành TypedDict được nữa → khai
  `get_weather_tool: FunctionToolParam = {...}` ngay chỗ viết literal (~ `const x: T = {...}` bên TS).

## Bài 2 — Vòng lặp tổng quát + query CSV

_(Claude viết, 2026-10-07, chạy thật `run_bai2` với `gpt-6-luna`, `MAX_STEPS = 5`)_

Log các câu thử (tool nào được gọi, args gì, mấy bước):

| Câu hỏi                                          | Tool + args                                                                      | Số bước (lời gọi LLM) | Đúng không                                       |
| ------------------------------------------------ | -------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------ |
| "An đã đặt bao nhiêu đơn, tổng bao nhiêu tiền?"  | `query_orders(customer="An", status=None)`                                       | 2                     | ✅ 5 đơn, 277.000đ (khớp cộng tay từ CSV)        |
| "Có đơn nào đang pending không?"                 | `query_orders(customer=None, status="pending")`                                  | 2                     | ✅ 3 đơn (1009, 1011, 1015), 134.000đ            |
| "Đơn nào bị huỷ, và trời Đà Nẵng giờ thế nào?"   | `query_orders(None, "cancelled")` + `get_weather("Đà Nẵng")` **cùng step 1**     | 2                     | ✅ 1004 + 1012 = 64.000đ; Đà Nẵng 24,8°C mưa phùn |

- Mọi câu đều 2 bước: step 1 gọi tool, step 2 trả lời. Câu 3 cần 2 tool nhưng model gọi **song song
  trong cùng 1 response**, không tốn thêm bước.
- LLM gửi `null` đúng chỗ ("không lọc") nhờ `None` trong `enum` + description "null = mọi ...".

Tổng tiền: để tool tính hay để LLM cộng, vì sao:

- Tool tính sẵn (`total_amount_vnd`) và description nói rõ có field đó → LLM dùng luôn, 3/3 câu đúng số.
- LLM đoán token chứ không tính toán, cộng nhiều số dễ sai. Phép tính chắc chắn phải đúng thì để code làm
  (giống ý "offload burden" trong Best practices của docs, và đổi mã WMO sang chữ ở Bài 1).

Tool `query_orders`:

- Đọc CSV bằng `pandas` (`uv add pandas`, đề gợi ý module `csv`). `to_dict(orient="records")` trả `int`
  Python thường nên `json.dumps` được. `TypedDict` không kiểm gì lúc chạy: ô trống trong CSV sẽ thành `NaN`
  (chưa thử).
- Đường dẫn file: `Path(__file__).parent / "orders.csv"` (~ `__dirname`). Đường dẫn tương đối tính từ thư
  mục đang chạy lệnh, không phải thư mục file `.py`.
- Bẫy truthiness: `if customer:` → `query_orders("", None)` trả **cả 15 đơn** (`""` falsy nên bỏ qua lọc).
  Đổi thành `if customer is not None:` → 0 đơn (đúng: không khách nào tên rỗng). `None` = "không lọc",
  KHÁC `""`.
- Lỡ sửa thành `if customer is None: return None` → `query_orders(None, "pending")` ra `None`, hỏng câu
  "Có đơn nào pending". `None` ở đây nghĩa là "không lọc", không phải "không có dữ liệu".
- Không phân biệt hoa thường: `.lower()` 2 phía → `"an"` khớp `"An"`.

Tool dict với tham số có thể null (strict mode):

- `"type": ["string", "null"]` và **vẫn phải** nằm trong `required`. Strict = mọi key đều bắt buộc;
  "tùy chọn" là cho phép giá trị null (~ TS `status: string | null`, không phải `status?: string`).
- Có `enum` thì phải thêm `None` vào `enum`. Đã thử với API thật, câu "Khách An có bao nhiêu đơn?":

  | `enum` của `status`  | LLM gửi                                   |
  | -------------------- | ----------------------------------------- |
  | có `None`            | `{"customer":"An","status":null}` ✅      |
  | không có `None`      | `{"customer":"An","status":"delivered"}` ❌ |

  Thiếu `None` thì strict ép LLM chọn 1 trạng thái → chỉ đếm 3/5 đơn của An, **API không báo lỗi**.
- Description không nói tên file (`orders.csv`): LLM không cần biết, lộ chi tiết nội bộ (mục bảo mật Bài 4).
  Nói tool trả về gì (`order_count`, `total_amount_vnd`) để LLM khỏi tự cộng.

Vòng lặp `run_bai2`:

- Registry `TOOLS_REGISTRY[call.name](**args)` thay cho if/else theo tên (~ map handler bên Express).
  Tên tool gõ ở 2 nơi (key registry và `"name"` trong tool dict) → lệch là `KeyError` (Bài 4b).
- Mọi lần gọi đều truyền `tools=TOOLS` (đã chứng minh ở Bài 1: thiếu thì model không gọi thêm được).
- **Bug đã gặp:** để `input_list += response.output` **trong** vòng `for call` → câu 3 (2 call cùng
  lượt) thêm output 2 lần → **400** `Duplicate item found with id fc_... Remove duplicate items from your
  input`. Câu chỉ gọi 1 tool thì không lộ lỗi. Sửa: `+=` 1 lần trước vòng `for call`, còn
  `function_call_output` thì mỗi call 1 cái (append trong vòng).

`MAX_STEPS` để làm gì:

- `step` tăng 1 mỗi **lần gọi LLM**, không phải mỗi lần chạy tool (câu 3: 2 tool vẫn chỉ 1 step).
  → `MAX_STEPS` giới hạn số lời gọi LLM = tiền + thời gian.
- Cần vì **LLM quyết định khi nào dừng**: vòng lặp chỉ thoát khi LLM trả lời mà không gọi tool. LLM có thể
  không chịu dừng: tool lỗi liên tục, kết quả không như ý nên đổi tham số thử mãi, hoặc bị prompt injection.
- Hiện tại tool lỗi (vd 503) làm chương trình **sập** luôn, chưa lặp → `MAX_STEPS` chưa có tác dụng. Sau
  Bài 4a (bắt lỗi, gửi `{"error": ...}` cho LLM) mới có thể lặp và `MAX_STEPS` mới chặn (Bài 4d).
- Chạm giới hạn thì user chưa nhận được câu trả lời nào → Bài 4d: nên báo user thế nào.
- ~ `maxRetries` khi retry API, hoặc giới hạn ~20 redirect của `fetch`.

## Bài 3 — Parallel tool calls

| Cách                         | Số function_call / response | Số lời gọi API | Thời gian | Input token |
| ---------------------------- | --------------------------- | -------------- | --------- | ----------- |
| parallel (mặc định), tuần tự |                             |                |           |             |
| parallel, `gather`           |                             |                |           |             |
| `parallel_tool_calls=False`  |                             |                |           |             |

Thiếu output cho 1 `call_id` → lỗi gì:

-

Thứ tự output có cần khớp không:

-

## Bài 4 — Xử lý lỗi

| Tình huống             | Code làm gì | LLM phản ứng thế nào |
| ---------------------- | ----------- | -------------------- |
| a) Tool lỗi giữa chừng |             |                      |
| b) Tool không tồn tại  |             |                      |
| c) Args sai            |             |                      |
| d) Lặp tới `MAX_STEPS` |             |                      |

Gặp thật (2026-10-06, lúc làm Bài 1): Open-Meteo trả **`503 Service Unavailable`** một lần,
`raise_for_status()` ném `httpx2.HTTPStatusError` → chương trình sập kèm traceback. Gọi lại ngay thì
200. Lỗi tạm thời phía server, đúng tình huống a): phải bắt lỗi và gửi cho LLM, không được sập vòng lặp.

Bảo mật: cái gì không nên nằm trong output của tool:

-

Prompt injection qua dữ liệu CSV, kết quả:

-

## Bài 5 — CLI chatbot có tools

Input token "Xin chào" có tools vs không tools:

-

"An có mấy đơn?" → "Còn Bình?" có hiểu không:

-

Cắt lịch sử khi có function_call / function_call_output:

-

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

- Function calling hoạt động thế nào? LLM có tự chạy code không?
- Tool fail giữa chừng thì xử lý sao? (Exit criteria Phase 01 có câu này, Buổi 9 sẽ thêm phần "giữa stream")
- Làm sao chặn agent gọi tool lặp vô hạn?
