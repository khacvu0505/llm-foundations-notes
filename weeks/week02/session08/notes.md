# Buổi 8 — FastAPI cơ bản (2h)

| Phần                                          | Thời lượng | Làm ở đâu      |
| --------------------------------------------- | ---------- | -------------- |
| Setup + đọc nhanh docs FastAPI tutorial       | ~10ph      | mục Setup      |
| Bài 1: routes, path/query params              | ~25ph      | `exercises.py` |
| Bài 2: request body Pydantic, POST /chat      | ~25ph      | `exercises.py` |
| Bài 3: async def vs def + HTTPException       | ~25ph      | `exercises.py` |
| Bài 4: Depends (client dùng chung, API key)   | ~20ph      | `exercises.py` |
| Bài 5: CORS + TestClient + so sánh Express    | ~15ph      | `exercises.py` |

Bài 3 phần A (đo `def` vs `async def`) là phần quan trọng nhất, không kịp thì cắt phần tuỳ chọn của Bài 4–5.

Checklist Notion Buổi 8:

- Routes, path/query params, request body với Pydantic, dependency injection cơ bản → Bài 1, 2, 4
- Async endpoints, error handling (HTTPException), CORS → Bài 3, 5
- So sánh với Express / Next API routes, ghi lại điểm khác → bảng cuối file

## Setup (tự làm)

- [x] **Cài FastAPI:** `uv add "fastapi[standard]"` (để trong ngoặc kép, zsh hiểu `[...]` là pattern).
      Kéo theo `uvicorn` (server, ~ Node http server), `fastapi-cli` (lệnh `fastapi dev`), `httpx` (bản
      gốc, `TestClient` cần). `httpx` này **khác** `httpx2` mà `openai` đang dùng (Buổi 7), 2 cái cùng tồn
      tại được.
- [x] **Kiểm:** `uv tree --depth 1` thấy `fastapi` ngang hàng `openai`.
- [x] **Dữ liệu:** copy `orders.csv` từ session07 sang session08 (mỗi buổi 1 thư mục độc lập).
- [x] **`.env`:** thêm 1 dòng `APP_API_KEY=<tự đặt>` cho Bài 4. Không commit `.env`.
- [x] **Chạy thử:** viết xong app + `/health` ở Bài 1 thì
      `uv run fastapi dev weeks/week02/session08/exercises.py` → mở http://127.0.0.1:8000/docs
- [ ] Đọc nhanh tutorial: First Steps, Path Parameters, Query Parameters, Request Body, Handling Errors,
      Dependencies, CORS, Testing (https://fastapi.tiangolo.com/tutorial/) + trang
      https://fastapi.tiangolo.com/async/ mục "In a hurry?".

## Nợ từ Buổi 7 (làm lúc rảnh, không chặn Buổi 8)

- [x] Notion: tick Buổi 7 + ghi "Status dd/mm/yyyy" (học được gì / còn nợ gì)
- [ ] Code hàm cắt lịch sử theo lượt (ranh giới `user`, bỏ cặp tool ở lượt cũ) — notes Buổi 7 mục Bài 5
- [ ] Chạy lại Bài 4d sau khi sửa câu trả lời cố định khi chạm `MAX_STEPS` (chưa chạy lại)
- [ ] (Tuỳ chọn) Sinh tool schema từ Pydantic; tool `save_order`
- [ ] Nợ Buổi 6 vẫn còn (xem `session07/notes.md` mục "Nợ từ Buổi 6")
- [ ] Nhật ký Tuần 2 trên Notion (cuối tuần, 2–3 dòng "học được gì / vướng gì")

## Bài 1 — Routes, path params, query params

_(Claude viết, 2026-10-10, số liệu từ các lần gọi thật vào `fastapi dev` + 1 script nháp `TestClient` để kiểm thứ
tự route và body hỏng)_

Lệnh / request đã thử và kết quả (mã + body):

| Request                              | Mã  | Body / ghi chú                                                                                     |
| ------------------------------------ | --- | -------------------------------------------------------------------------------------------------- |
| `GET /health`                        | 200 | `{"status":"ok"}`                                                                                  |
| `GET /orders?customer=An`            | 200 | 5 đơn (1001, 1003, 1006, 1011, 1015), khớp Buổi 7                                                  |
| `GET /orders?customer=an`            | 200 | 5 đơn, nhờ `.lower()` 2 phía                                                                       |
| `GET /orders?status=pending`         | 200 | 3 đơn (1009, 1011, 1015)                                                                           |
| `GET /orders?customer=An&status=delivered` | 200 | 2 đơn (1001, 1003): 2 filter nối tiếp = AND                                                  |
| `GET /orders` (không param)          | 200 | cả 15 đơn: không truyền = `None` = không lọc                                                       |
| `GET /orders?customer=` (chuỗi rỗng) | 200 | 0 đơn: `""` khác `None`, nhờ `is not None` (bẫy truthiness Buổi 7)                                 |
| `GET /orders?status=abc`             | 422 | `literal_error`, `loc: ["query","status"]`, `msg` liệt kê 4 giá trị hợp lệ, `input: "abc"`         |
| `GET /orders/1003`                   | 200 | đơn 1003 (An, Bánh mì thịt)                                                                        |
| `GET /orders/1003.0`                 | 200 | vẫn ra đơn 1003: lax mode Pydantic (Buổi 5) ép `"1003.0"` → 1003                                   |
| `GET /orders/abc`                    | 422 | `int_parsing`, `loc: ["path","order_id"]`, `input: "abc"`                                          |
| `GET /orders/9999`                   | 200 | `null`: hàm return `None` → JSON `null`, client không biết là "không có". Bài 3 đổi sang 404       |
| `GET /orders/summary` (đặt sau)      | 422 | `int_parsing`, `loc: ["path","order_id"]`, **`input: "summary"`** → rơi vào route `{order_id}`     |
| `GET /orders/summary` (đặt trước)    | 200 | `{"total_orders":13,"total_amount":866000}` (bỏ 2 đơn `cancelled` 1004, 1012 = 64.000)             |

Query param bên Express là string, bên FastAPI là gì:

- Trên URL thì vẫn là chuỗi, nhưng FastAPI **ép sang kiểu khai trong type hint** trước khi gọi hàm: `n: int` nhận
  `int` thật, `status: Status` chỉ nhận 4 giá trị của `Literal`. Bên Express `req.query.n` luôn là `string`,
  phải tự `Number(...)` + tự validate (Zod).
- Tham số **có trong `{...}` của path** → path param; **không có** → query param; **có default** (`= None`) → tuỳ
  chọn. Không cần `req.params` / `req.query`.
- `X | None = None` = "không truyền thì không lọc". `None` (không truyền) ≠ `""` (truyền rỗng).

422 là gì, khác 400 chỗ nào, lỗi validate xảy ra trước hay sau khi vào hàm:

- **422 Unprocessable Content** = request đúng định dạng HTTP nhưng **giá trị không hợp lệ** (sai kiểu, ngoài
  `Literal`, thiếu field). **400 Bad Request** = lỗi chung chung "request hỏng", tự mình trả khi muốn.
- FastAPI trả **422 cho mọi lỗi validate**, kể cả body không phải JSON (`type: json_invalid`, đã thử bằng
  `TestClient` với FastAPI 0.143). Muốn 400 thì phải tự đổi (exception handler).
- Lỗi xảy ra **trước** khi vào hàm: `get_orders` / `get_order` không chạy dòng nào (không `print`, không đọc CSV).
  Body lỗi có cấu trúc: `type` (loại lỗi), `loc` (ở đâu: `query` / `path` / `body` + tên field), `msg`, `input`.

Thứ tự route (`/orders/summary` vs `/orders/{order_id}`):

- FastAPI so URL với route **theo thứ tự khai báo**, route nào khớp trước thì dùng. `{order_id}` khớp **mọi**
  đoạn path, kể cả chữ `summary` → thử ép `"summary"` sang `int` → 422. Route `/orders/summary` khai sau không
  bao giờ được chạy tới.
- Sửa: khai route **cố định** (`/orders/summary`) **trước** route có tham số (`/orders/{order_id}`).
- Bên Express cũng theo thứ tự như vậy, khác ở chỗ `req.params.id = "summary"` (string) **vào được handler**,
  thường thành bug âm thầm (tìm đơn id `"summary"` → không thấy). FastAPI báo 422 nên lộ lỗi ngay.

`/docs` so với tự viết Swagger bên Express:

- `/docs` sinh **tự động** từ type hint: path/query param, kiểu, giá trị `Literal` (dropdown), schema response
  (`OrderItem`, `OrdersSummary`), có nút "Try it out". Spec gốc ở `/openapi.json`.
- Express phải viết tay JSDoc/YAML (`swagger-jsdoc`) hoặc sinh từ Zod (`zod-to-openapi`) → docs dễ **lệch** code.
  FastAPI: code đổi là docs đổi theo, vì cùng 1 nguồn.
- Khai kiểu trả về (`-> OrdersSummary`) mới có schema response; `-> dict[str, int]` chỉ hiện "object số nguyên",
  client không biết tên field.

Bẫy "pyright 0 lỗi nhưng không thật sự kiểm":

| Code                                         | Pyright | Thực tế                                                                 |
| -------------------------------------------- | ------- | ----------------------------------------------------------------------- |
| `from fastapi import Path` rồi `Path(__file__).parent` | 0 lỗi | `fastapi.Path` (khai path param) trả `Any` → chạy ném `AssertionError` → 500. Cần `pathlib.Path` |
| `cast(OrderResponse, df.to_dict(...))`       | lỗi ở chỗ **khác** (dòng lọc) | `cast` sai kiểu → pyright tin theo, `for` qua dict ra key `str`. Đúng: `cast(list[OrderItem], ...)` |
| `summary = {...}` rồi `return OrdersSummary(**summary)` | 0 lỗi | `**dict[str, int]` không kiểm key: gõ sai `total_ordrs` vẫn qua (đã thử). Đúng: `summary: OrdersSummary = {...}` |
| `from weeks.week02.session07.exercises import ...` | 0 lỗi | `fastapi dev` → `ModuleNotFoundError: No module named 'weeks'` (giống Buổi 7 Bài 5) |

- Chung 1 ý: `Any`, `cast`, `**dict` là các chỗ pyright **tin mình**. TypedDict không kiểm gì lúc chạy.
- `Could not find FastAPI app in module`: file chưa có biến `app = FastAPI()` ở cấp module.

## Bài 2 — Request body Pydantic, POST /chat

_(Claude viết, 2026-10-10. a–d, e', f: gọi thật vào app (`fastapi run` port 8765, `gpt-6-luna`,
`max_output_tokens=200`), cột "gọi OpenAI" đọc từ log server (dòng `Received message: ...` in ở đầu hàm `chat`).
e và phần lọc field: script nháp `TestClient` trong scratchpad, không gọi OpenAI, để khỏi sửa code bài)_

| Thử                                    | Mã  | Body / ghi chú                                                                                    | Có gọi OpenAI không |
| -------------------------------------- | --- | ------------------------------------------------------------------------------------------------- | ------------------- |
| a) body đúng                           | 200 | `{"reply":"Xin chào! Mình có thể giúp gì cho bạn?","input_tokens":25,"output_tokens":17,"cost_usd":0.000011}` | **Có** (log in `Received message: Xin chào`) |
| b) thiếu `message`                     | 422 | `type: missing`, `loc: ["body","message"]`, `msg: "Field required"`                               | Không               |
| c) `message = ""`                      | 422 | `type: string_too_short`, `ctx: {"min_length": 1}`                                                | Không               |
| d) `message` 600 ký tự                 | 422 | `type: string_too_long`, `msg: "...at most 500 characters"`, `input` = **nguyên 600 ký tự** gửi lại | Không               |
| e) thêm field lạ `foo`                 | 200 | Mặc định `extra="ignore"`: `foo` bị **bỏ âm thầm**, `body.model_dump()` = `{"message":"hi"}`      | **Có** (hàm vẫn chạy) |
| e') thêm field lạ + `extra="forbid"`   | 422 | `type: extra_forbidden`, `loc: ["body","foo"]`, `msg: "Extra inputs are not permitted"`           | Không               |
| f) body không phải JSON                | 422 | `type: json_invalid`, `loc: ["body",0]`, `msg: "JSON decode error"` (**không phải 400**)          | Không               |
| (thêm) thiếu header `Content-Type`     | 422 | `type: model_attributes_type`: không có header JSON → body bị coi là **chuỗi**, không phải object | Không               |

- 6/7 request lỗi bị chặn **trước** hàm `chat`: log server chỉ có đúng 1 dòng `Received message` (của a), các dòng
  còn lại chỉ có `POST /chat ... 422`. Body hỏng **không tốn tiền OpenAI**.
- `loc` luôn bắt đầu bằng `"body"` (Bài 1 là `"query"` / `"path"`) → client biết lỗi nằm ở phần nào của request.
- Lỗi d trả **lại nguyên input** trong `input`. Body 500 ký tự thì không sao, nhưng nếu không giới hạn độ dài thì
  response lỗi cũng phình theo. Body có dữ liệu nhạy cảm thì nó bị gửi ngược lại (vẫn là của chính client).
- Request a: 25 input token cho câu "Xin chào" + `instructions` ngắn, không có tool (so Buổi 7: 176 khi có 2 tool).

Mặc định `ignore` vs `forbid`:

- `ignore` dễ chịu với client, nhưng **giấu lỗi gõ sai tên field**: gửi `{"mesage": "hi"}` (sai chính tả) sẽ báo
  "thiếu `message`" chứ không báo "field lạ `mesage`" → khó đoán ra nguyên nhân. (Suy luận, chưa thử.)
- `forbid` ~ Zod `.strict()`, chặt hơn, hợp cho endpoint tốn tiền như `/chat`.
- `model_config = ConfigDict(...)` là **cấu hình** của model (thuộc tính class), không phải field. Phải đúng tên
  `model_config`.

`response_model` lọc field nội bộ:

| Route (script nháp)                                     | Hàm return                          | Client nhận                                             |
| ------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------- |
| `response_model=ChatResponse`, hàm `-> dict[str, Any]`  | dict có thêm `"model": "gpt-6-luna"` | `{"reply","input_tokens","output_tokens","cost_usd"}`: **mất `model`** |
| không `response_model`, hàm `-> dict[str, Any]`         | `{"reply": "ok", "model": "gpt-6-luna"}` | nguyên dict, **lộ `model`**                         |

- `response_model` = **lớp lọc ở đầu ra**: chỉ field khai trong model mới tới client, field thừa bị bỏ. Ngược
  chiều với `extra="forbid"` (lọc đầu vào, báo lỗi), và lọc đầu ra thì **không báo lỗi**, bỏ âm thầm.
- Lợi: return thẳng object nội bộ (có `model`, `user_id`, `api_key`...) mà không sợ lộ, giống Buổi 7 "LLM chỉ thấy
  field cần". Bên Express phải tự `pick` / `omit` hoặc chạy qua Zod schema trước `res.json()`.
- Muốn return dict có field thừa thì kiểu trả về của hàm phải đổi (vd `-> dict[str, Any]`), vì `-> ChatResponse`
  thì pyright không cho. Khi đó `response_model` mới là thứ quyết định client nhận gì, không phải type hint của hàm.
- App thật (`exercises.py`) chưa làm phần này: hàm vẫn return `ChatResponse(...)` nên không có field thừa để lọc.

Giới hạn 500 ký tự ở model Pydantic thay vì `if` trong hàm, lợi gì (liên hệ chống spam Buổi 10–11):

- **Chặn trước khi tốn tiền**: message 600 ký tự bị 422 ngay, không vào hàm, không gọi OpenAI (log không có
  `Received message`). `if` trong hàm cũng chặn được, nhưng phải nhớ đặt **trước** lời gọi OpenAI, dễ sót khi sửa code.
- **Khai 1 lần, dùng mọi nơi**: cùng 1 model cho validate, docs (`/docs` hiện `maxLength: 500`) và lỗi có cấu trúc.
  `if` tự viết thì phải tự viết thông báo lỗi, tự cập nhật docs.
- **Không quên được**: thêm route mới dùng lại `ChatRequest` là có giới hạn sẵn.
- Liên hệ Buổi 10–11: đây là tầng 1 của chống spam (giới hạn **input**). Cần thêm `max_output_tokens` (giới hạn
  **output**, đã đặt 200) và rate limit theo IP (giới hạn **số lần gọi**). Giới hạn ký tự ≠ giới hạn token: tiếng Việt
  tốn token hơn tiếng Anh (Buổi 3), 500 ký tự tiếng Việt có thể ra nhiều token hơn 500 ký tự tiếng Anh.

Body hỏng bị chặn ở đâu, có tốn lời gọi OpenAI không:

- Ở tầng **FastAPI + Pydantic**, trước khi gọi hàm route. Thứ tự: parse JSON (f) → kiểm kiểu object (thiếu
  `Content-Type`) → kiểm field có / thiếu / thừa (b, e') → kiểm ràng buộc `Field` (c, d) → mới gọi hàm.
- Không tốn lời gọi OpenAI nào (6/7 request lỗi, log chỉ có 1 `Received message`).

Các lỗi đã gặp khi viết Bài 2:

- `max_length=600` thay vì 500 → trường hợp d sẽ **lọt qua** và gọi OpenAI thật. `/openapi.json` hiện `maxLength`
  là cách kiểm nhanh.
- `usage` là `None` → trả `0` là **nói dối** (client tưởng miễn phí). Sửa: field `int | None`, gán `usage` 1 lần,
  `if usage is None: return ...` sớm (early return + narrowing, ~ guard clause TS).
- Đổi tham số `cost_usd` thành `int | None` → lỗi chỉ **chuyển vào trong hàm** (`Operator "/" not supported for
  "None"`). Hàm tính toán nhận dữ liệu đã chắc chắn có, xử lý `None` ở chỗ gọi.
- Gõ `null` → `F821 Undefined name`. Python dùng `None` (và `True` / `False`).
- `max_output_tokens=200` với model reasoning: reasoning token tính vào giới hạn → câu khó có thể `incomplete`,
  `reply` cụt / rỗng (Buổi 3). Chưa thử với câu dài.

## Bài 3 — async def vs def + xử lý lỗi

_(Claude viết, 2026-10-10. 3 route `/slow/*`: số đo do bạn chạy `bench.py` (5 request song song mỗi route,
`fastapi dev`). Cột "Đoán trước" để trống vì không ghi trước khi chạy. Dòng `/chat`: chưa đo)_

5 request song song (`bench.py`):

| Route                                                     | Đoán trước | Tổng thời gian đo | Vì sao                                                                                   |
| --------------------------------------------------------- | ---------- | ----------------- | ---------------------------------------------------------------------------------------- |
| `/slow/def` (`def` + `time.sleep`)                        |            | **1.03 s**        | `def` → FastAPI chạy trong **threadpool**: 5 thread ngủ cùng lúc, mỗi cái chặn thread của nó, không chặn loop |
| `/slow/async-block` (`async def` + `time.sleep`)          |            | **5.04 s**        | `async def` chạy **thẳng trên event loop** (1 thread). `time.sleep` chặn loop → 5 request xếp hàng 1 + 1 + 1 + 1 + 1 |
| `/slow/async-await` (`async def` + `await asyncio.sleep`) |            | **1.01 s**        | `await` trả quyền cho loop trong lúc chờ → loop nhận 4 request còn lại → chờ chồng lên nhau |
| `/chat` `def` + client `OpenAI()` sync                    |            | **2.84 s**        | Giống `/slow/def`: mỗi request 1 thread, chờ OpenAI không chặn loop. Mốc 1 request: 1.94–2.35 s |
| `/chat` `async def` + client `OpenAI()` sync (bản sai)    |            | **6.58 s**        | Giống `/slow/async-block`: `responses.create` sync chặn loop → xong **lần lượt** 1.20 / 2.50 / 3.92 / 5.34 / 6.58 s |
| `/chat` `async def` + `AsyncOpenAI` + `await`             |            | **1.78 s**        | Giống `/slow/async-await`: xong **lộn xộn** 1.19–1.78 s (req4 trước req0) = song song thật |

_(Dòng `/chat`: 2.84 s do bạn chạy `bench.py`. Mốc 1 request, 6.58 s và 1.78 s do Claude đo bằng script nháp in
thời điểm xong từng request, cùng câu "Xin chào", `gpt-6-luna`. Bạn cũng tự thấy bản sai bị xếp hàng. Thời gian
OpenAI đổi theo lúc gọi (~1.2–2.4 s / request) → so **tổng 5 request với mốc 1 request**, không so số tuyệt đối)_

- Bản sai **pyright 0 lỗi**: gọi client sync trong `async def` là code hợp lệ, chỉ đo mới thấy. (Ruff `ASYNC` có
  rule cho `time.sleep`, nhưng **không** bắt `OpenAI().responses.create` trong `async def`: đã thử
  `ruff check --select ASYNC` trên file nháp → `All checks passed!`. Không tool nào bắt được, chỉ đo mới thấy.)
- Ngược lại, `await` trên client **sync** → pyright báo `"Response" is not awaitable`. Client **async** mà quên
  `await` → nhận coroutine, `response.usage` lỗi → pyright báo `output_text is unknown`, chạy thì 500 ngay.
- `def` + sync vẫn **đúng**, nhưng mỗi request giữ 1 thread suốt 1–3 s chờ OpenAI → tối đa 40 user cùng lúc.
  `async def` + `AsyncOpenAI` không giới hạn đó, và Bài 4 (Depends) + Buổi 9 (stream) cần bản async.
- Lần bench đầu với bản sai ra 1.75 s (không xếp hàng): giả thuyết chạy `bench.py` khi server **chưa reload xong**,
  hoặc `n=1`. → Đợi dòng reload trong terminal server rồi mới đo, và in `status_code`.

- Gọi **1 request** mỗi route thì cả 3 đều ~1 s (1.04 / 1.15 / 1.01, lần chạy đầu khi `bench.py` mới bắn 1
  request). Chỉ khi có **nhiều request cùng lúc** mới thấy route bị chặn. → Test tay bằng curl / `/docs` từng cái
  một sẽ **không phát hiện** được lỗi này, phải bench song song.
- Threadpool không vô hạn: `anyio` mặc định **40** thread (đã kiểm `current_default_thread_limiter().total_tokens`).
  Request `def` thứ 41 cùng lúc phải chờ. `async def` + `await` không có giới hạn này.

```
async def + time.sleep (5.04 s):        async def + await asyncio.sleep (1.01 s):
event loop (1 thread):                   event loop (1 thread):
 req1 |█████|                             req1 |-await------|
 req2       |█████|                       req2 |-await------|   ← loop rảnh trong lúc chờ,
 req3             |█████|                 req3 |-await------|      chuyển sang request khác
 req4                   |█████|           req4 |-await------|
 req5                         |█████|     req5 |-await------|
 █ = loop bị CHẶN, không làm gì khác được

def + time.sleep (1.03 s):
 event loop đẩy mỗi request sang 1 thread → thread1 |█████|  thread2 |█████|  ...  thread5 |█████|
```

Khi nào dùng `def`, khi nào `async def`:

- Bên trong **toàn `await`** (client async: `AsyncOpenAI`, `httpx2.AsyncClient`, `asyncio.sleep`) → `async def`.
- Bên trong **có code sync chặn** (client `OpenAI()` sync, `requests`, `time.sleep`, `pd.read_csv` file lớn) →
  `def`, để FastAPI đẩy sang thread.
- **Không bao giờ** gọi code sync chặn trong `async def` (= `/slow/async-block`, trường hợp tệ nhất: chậm cả server,
  không chỉ route đó).
- Không chắc thì `def` an toàn hơn: chậm hơn một chút (tốn thread) nhưng không chặn loop.
- Ruff có rule bắt lỗi này: `uv run ruff check --select ASYNC` → `ASYNC251 Async functions should not call
  time.sleep` ở `/slow/async-block` (mặc định project chưa bật nhóm `ASYNC`).

Bên Node có chuyện "1 hàm chặn cả server" không:

- **Có**, và giống hệt `/slow/async-block`: Node chỉ có 1 event loop, mọi handler chạy trên đó. Code sync nặng
  (`while` tốn CPU, `fs.readFileSync` file lớn, `crypto.pbkdf2Sync`, `JSON.parse` chuỗi rất lớn) → mọi request
  khác đứng chờ.
- Khác: Node gần như không có `sleep` chặn, I/O mặc định là async (`fetch`, `fs/promises`) → khó lỡ tay hơn. Python
  có rất nhiều thư viện sync (`requests`, `OpenAI()`, `pandas`) → dễ đặt nhầm vào `async def`.
- FastAPI có "lối thoát" `def` → threadpool tự động. Node không tự làm, phải tự dùng `worker_threads`.
- `bench.py` ~ chạy `autocannon` / `Promise.all(fetch...)` vào server Express để thấy request bị xếp hàng.

Các lỗi đã gặp khi viết `bench.py`:

- `async with ... as client` thiếu `:` + khối `for` không thụt vào trong → `Expected ":"`, `Expected an indented
  block`. `:` + thụt lề = `{ }` bên TS.
- `gather(client.get(path))` chỉ **1** request → cả 3 route ~1 s, không thấy khác biệt (không lỗi cú pháp, không
  lỗi pyright, chỉ sai ý).
- `gather(client.get(path) for _ in range(5))` (thiếu `*`) → pyright: `Generator[...]` không `await` được. Generator
  là tham số duy nhất thì được bỏ ngoặc, có `*` thì phải `*( ... )`.
- `timeout=5000`: đơn vị httpx là **giây** (~83 phút), không phải ms như `setTimeout`. 30 là đủ dư.
- `if __name__:` luôn đúng (chuỗi khác rỗng) → phải `if __name__ == "__main__":`.

Lỗi:

_(Claude viết, 2026-10-10, gọi thật vào app: `fastapi dev` port 8000 + server tạm `fastapi run` port 8765 để đọc
log. OpenAI lỗi: tạm `MODEL = "gpt-khong-ton-tai"`, đã đổi lại `gpt-6-luna`)_

| Tình huống                                   | Mã      | Client thấy gì                                                         | Terminal in gì                                                                                        |
| -------------------------------------------- | ------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/orders/9999` (HTTPException)               | **404** | JSON `{"detail":"Order 9999 not found"}`                               | 1 dòng access log `GET /orders/9999 404 Not Found`, **không** traceback                               |
| OpenAI lỗi, **chưa bắt**                     | **500** | `text/plain` `Internal Server Error` (21 byte, không phải JSON)        | Traceback đầy đủ, cuối: `openai.NotFoundError: Error code: 404 - {... 'code': 'model_not_found'}`     |
| OpenAI lỗi (MODEL sai) → bắt, 502            | **502** | JSON `{"detail":"Something went wrong. Try it later"}`                 | `[openai error] NotFoundError \| model=gpt-khong-ton-tai \| Error code: 404 ...` + access log 502, không traceback |
| `raise ValueError` không bắt (`GET /boom`)   | **500** | `text/plain` `Internal Server Error`, giống hệt OpenAI lỗi chưa bắt    | `ERROR: Exception in ASGI application` + traceback ~66 dòng, cuối: `exercises.py, line 306, in boom` → `ValueError: Bug giả lập` |

- **Lỗi không bắt → client luôn nhận cùng 1 câu `Internal Server Error`**, dạng `text/plain`, không phân biệt được
  lỗi OpenAI hay bug code. Frontend gọi `res.json()` sẽ lỗi parse → phải kiểm `res.ok` / `content-type` trước.
- **Không lộ gì ra client** (không traceback, không `str(e)`), kể cả khi chạy `fastapi dev`. Chi tiết chỉ ở terminal.
- `HTTPException` = lỗi **đã xử lý**: FastAPI không in traceback, chỉ access log. → Muốn biết lỗi gốc phải **tự log**
  trước khi `raise` (`print` chỉ lặp lại câu cho client thì vô ích). `raise ... from e` không tự in lỗi gốc ra
  terminal, chỉ giữ chuỗi nguyên nhân nếu có ai in traceback.
- Bên Express: lỗi không bắt trong handler sync → error handler mặc định trả **500**. Dev (`NODE_ENV` khác
  `production`) trả **HTML có stack trace**, production chỉ trả "Internal Server Error". Lỗi trong handler `async`
  ở Express 4 không tự bắt (request treo / `unhandledRejection`), Express 5 mới tự bắt. _(Theo hiểu biết, chưa
  chạy thử trong buổi này)_

`/orders/{order_id}` không tìm thấy → 404 (so với Bài 1):

- Trước: `return None` → **200** + body `null`, client không biết là "không có". Sau: `raise HTTPException(404,
  detail=f"Order {order_id} not found")`.
- Trả lỗi bằng **`raise`**, không phải `return` (FastAPI không có `res`). Giống `throw new NotFoundException()` bên
  NestJS, khác `return res.status(404).json(...)` bên Express.
- `raise` không trả giá trị → pyright không báo `must return value`. Hàm chỉ còn 2 lối ra (`return order` / `raise`)
  → có thể bỏ `| None` ở `-> OrderItem | None`. Còn để `| None` thì `/openapi.json` vẫn ghi response 200 "hoặc
  `null`" (sai so với thực tế).
- `detail` có `order_id` thì ổn (do client gửi lên). Không đưa chi tiết nội bộ (tên file CSV, đường dẫn).

Bắt lỗi OpenAI, các bước đã sửa:

| Lần | Code                                                    | Vấn đề                                                                                         |
| --- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | không `try`                                             | 500 `text/plain`, client không biết là lỗi upstream                                            |
| 2   | `except:` (bare) bọc cả hàm, không log                  | Ruff `E722`, `B904`. Bắt cả bug code (`KeyError` của `PRICES[MODEL]`) + `CancelledError` / Ctrl+C. Terminal không còn dấu vết lỗi |
| 3   | `except openai.APIError:` bọc cả hàm                    | Hết `E722`, còn `B904`, vẫn không log                                                          |
| 4   | `try` chỉ bọc `await client.responses.create(...)`, `except openai.APIError as e`, `raise ... from e` | Ruff sạch, nhưng `print` lặp lại câu gửi client → log vô ích |
| 5   | `print(f"[openai error] {type(e).__name__} \| model={MODEL} \| {e}")` | ✅ dev thấy loại lỗi + model + chi tiết, client chỉ nhận câu gọn |

- Cây lỗi SDK `openai` (đã kiểm `__mro__`): `NotFoundError → APIStatusError → APIError → OpenAIError → Exception`,
  `APITimeoutError → APIConnectionError → APIError → ...`. Bắt `APIStatusError` **sót** timeout / mất mạng → bắt
  `APIError` (hoặc `OpenAIError`).
- `try` hẹp: sau khối `try/except`, pyright biết `response` chắc chắn có giá trị (nhánh `except` luôn `raise`).
- Terminal (dev) in `str(e)` được, client thì không. Không log API key, header `Authorization`.

404 / 422 / 500 / 502 khác nhau thế nào, ai trả mã nào:

| Mã      | Nghĩa                                                  | Ai trả trong app này                                                      | Lỗi của ai          |
| ------- | ------------------------------------------------------ | ------------------------------------------------------------------------- | ------------------- |
| **404** | Không tìm thấy tài nguyên                              | **Code mình** chủ động `raise HTTPException(404)` (`/orders/9999`). Route không tồn tại thì FastAPI tự trả 404 | Client (hỏi cái không có) |
| **422** | Request đúng cú pháp HTTP nhưng **giá trị không hợp lệ** | **FastAPI + Pydantic** tự trả, trước khi vào hàm (Bài 1, Bài 2)          | Client (gửi sai)    |
| **500** | Server lỗi, không biết xử lý                           | **FastAPI / uvicorn** khi exception **không được bắt** (`/boom`, OpenAI lỗi chưa bắt) | Server (bug của mình) |
| **502** | Server vẫn ổn, nhưng **dịch vụ phía sau** lỗi           | **Code mình** bắt lỗi upstream rồi `raise HTTPException(502)`            | Upstream (OpenAI)   |

- 4xx = lỗi phía client (sửa request là được). 5xx = lỗi phía server (client không tự sửa được, có thể thử lại sau).
- 500 là mã "mặc định khi không ai xử lý". Thấy 500 trong log = có chỗ chưa bắt lỗi hoặc có bug.
- 502 cho client biết thử lại sau có thể được. Vì 500 không cho biết điều đó, nên lỗi upstream nên đổi thành 502
  (hoặc 503 / 504 tuỳ trường hợp, chưa dùng trong bài).
- Body khác nhau: 404 / 502 từ `HTTPException` có `detail` là **chuỗi**, 422 có `detail` là **list** lỗi, 500 không
  có JSON. Client cần xử lý cả 3 dạng.

## Bài 4 — Dependency injection (Depends)

_(Claude viết, 2026-10-11, gọi thật vào `fastapi dev` port 8000. Key đúng đọc từ `.env` bằng
`$(grep '^APP_API_KEY=' .env | cut -d= -f2-)`, không in ra. Trường hợp thiếu `APP_API_KEY`: script nháp
`TestClient` import app rồi `os.environ.pop("APP_API_KEY")`)_

| Gọi `/chat`                              | Mã      | Body                                                                     |
| ---------------------------------------- | ------- | ------------------------------------------------------------------------ |
| không có `X-API-Key`                     | **401** | `{"detail":"Missing API Key"}`                                           |
| sai key                                  | **401** | `{"detail":"Invalid API Key"}`                                           |
| đúng key                                 | **200** | `{"reply":"Xin chào! Tôi có thể giúp gì cho bạn?","input_tokens":25,"output_tokens":16,"cost_usd":0.0000105}` |
| `/health` không key                      | **200** | `{"status":"ok"}`: dependency chỉ gắn `/chat`                            |
| không key + body hỏng (`message=""`)     | **401** | `Missing API Key`: lỗi dependency được trả, không phải 422 của body      |
| server thiếu `APP_API_KEY` (có/không header) | **500** | `{"detail":"Server misconfigured"}`: **fail closed**, không lộ lý do |

- 401 không gọi OpenAI (không có `Received message` trong log). Chặn trước khi tốn tiền, giống 422 ở Bài 2.
- Header không phân biệt hoa thường: `X-API-Key` hay `x-api-key` đều đọc được.

Code cuối (`verify_api_key`), thứ tự 3 bước kiểm, mỗi bước sai thì `raise` ngay (guard clause):

| Bước | Điều kiện                       | Mã  | Vì sao                                                                                  |
| ---- | ------------------------------- | --- | --------------------------------------------------------------------------------------- |
| 1    | `os.getenv("APP_API_KEY") is None` | 500 | Lỗi **server** (quên cấu hình). Không cho qua: nếu bỏ bước này, thiếu env + thiếu header thì `None == None` → lọt |
| 2    | `x_api_key is None`             | 401 | Client không gửi                                                                        |
| 3    | `not secrets.compare_digest(expected, x_api_key)` | 401 | Sai key. `compare_digest` tốn thời gian như nhau dù sai ở ký tự nào → không đo thời gian để đoán key được (khác `==`) |

- Bước 1 + 2 thu hẹp kiểu: tới bước 3 pyright biết cả 2 là `str` (`compare_digest` không nhận `None`).
- Gắn bằng `dependencies=[Depends(verify_api_key)]` ở decorator vì dependency **chỉ kiểm, không trả giá trị**.
- Không log / trả `APP_API_KEY` ở đâu cả, kể cả trong `detail`.

Các lỗi đã gặp khi viết `verify_api_key`:

| Code                                         | Hậu quả                                                                                           |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `x_api_key: str` (không `Header()`)          | FastAPI coi là **query param** (quy tắc Bài 1). Header bị bỏ qua → 422 `loc: ["query","x_api_key"]`. Chỉ `?x_api_key=...` trên URL mới tới được dependency → key nằm trong URL, bị ghi vào access log (lộ key như Buổi 7). `/openapi.json` hiện `('x_api_key','query')` |
| `x_api_key: str` + `if x_api_key is None`    | Dòng `if` là **code chết** (kiểu `str` không bao giờ `None`), pyright không cảnh báo              |
| Xoá `if x_api_key is None`, tham số `str \| None` | `compare_digest(expected, None)` → pyright báo, chạy thì `TypeError` → 500 thay vì 401       |
| Đúng: `Annotated[str \| None, Header()] = None` | `/openapi.json`: `('x-api-key', 'header')`. FastAPI đổi `_` → `-`                              |

- Chữ "missing" trong 422 là của **FastAPI** (`type: missing`), không phải `"Missing API Key"` của mình. Nhìn `loc`
  để biết FastAPI đang tìm ở đâu (`query` / `header` / `body`).
- `default=None` → `/openapi.json` ghi header là `required: False`, `/docs` hiện như tuỳ chọn dù thiếu là 401. Project #1:
  dùng `APIKeyHeader` (`fastapi.security`) → `/docs` có nút "Authorize". _(chưa thử)_

Client OpenAI qua Depends (`get_openai_client`):

- `def get_openai_client() -> AsyncOpenAI: return client`, `chat(..., openai_client: Annotated[AsyncOpenAI,
  Depends(get_openai_client)])`.
- Gắn làm **tham số** (không phải `dependencies=[...]`) vì dependency **trả giá trị** cho hàm route.
- `openai_client` **không** xuất hiện trong `/openapi.json`: FastAPI biết nó đến từ dependency, client không gửi.
- Đặt tên khác `client` (global) cho khỏi nhầm.

Phân trang (`PaginationParams` + `Depends()`, gắn `GET /orders`):

| Request                          | Kết quả                                    |
| -------------------------------- | ------------------------------------------ |
| `?limit=3`                       | 1001, 1002, 1003, total=15                 |
| `?limit=3&offset=3`              | 1004, 1005, 1006, total=15                 |
| `?customer=An&limit=2`           | 1001, 1003, total=5                        |
| `?customer=An&limit=2&offset=2`  | 1006, 1011, total=5                        |
| `?status=pending&limit=10`       | 1009, 1011, 1015, total=3                  |
| `?offset=60`                     | `[]`, total=15, **200** (slice vượt độ dài không lỗi) |
| `?limit=0` / `51` / `offset=-1` / `limit=abc` | **422**                       |

- `limit: int = Field(10, ge=1, le=50)`, `offset: int = Field(0, ge=0)`. Giới hạn trên cho `limit` (chống
  `?limit=1000000` kéo cả bảng, cùng tư duy 500 ký tự ở `/chat`), **không** cho `offset`.
- Thứ tự: **lọc → `total = len(đã lọc)` → cắt trang `[offset : offset + limit]` → trả**. `total` đếm trước khi cắt,
  client mới biết còn trang sau.
- `Depends()` không truyền hàm → FastAPI dùng **chính class** làm dependency, trải field thành query param.

Các lỗi đã gặp khi viết phân trang:

| Lần | Code                                                       | Kết quả                                                                          |
| --- | ---------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 1   | `params: Annotated[...]` đặt **sau** `customer = None`     | `Non-default argument follows default argument` (~ TS: required sau optional)    |
| 2   | `Annotated[FilterParams, Query()]` + `customer`, `status`  | **Mọi** request 422 `missing params`. Query model chỉ được trải ra khi là **query param duy nhất** của route (đã thử bằng `TestClient`, FastAPI 0.143, chưa đối chiếu docs) |
| 3   | Đổi `Depends()`, nhưng cắt trang **trước** lọc            | `?customer=An&limit=2` → 1001, **1002 (Bình)**. Kết quả lọc nằm trong `orders` nhưng không ai dùng |
| 4   | `total = len(orders_filtered)`                             | `total` = số đơn **trong trang**, lọc vẫn không có tác dụng                      |
| 5   | `ge=0` cho `limit`, `le=50` cho `offset`                   | `limit=0` → 200 trang rỗng; `offset=60` → 422                                    |
| 6   | Đúng thứ tự + `ge=1` + bỏ `le` của offset                  | 13/13 trường hợp đúng                                                             |

- `offet` (gõ thiếu `s`): với `extra="ignore"` mặc định, `?offset=3` không lỗi, chỉ **không có tác dụng**.
- 3 cách khai phân trang:

  | Cách                                   | Dùng lại nhiều route | Thay được khi test |
  | -------------------------------------- | -------------------- | ------------------ |
  | `Query()` từng param (`limit: Annotated[int, Query(ge=1)] = 10`) | ❌ | ❌ |
  | Model gộp **mọi** query param + `Query()` | ❌ (dính `customer`, `status`) | ❌ |
  | **Model phân trang + `Depends()`** (đã chọn) | ✅              | ✅                 |

Depends giống / khác middleware Express thế nào:

- **Giống middleware gắn cho từng route**: `app.post("/chat", requireApiKey, handler)` ~
  `@app.post("/chat", dependencies=[Depends(verify_api_key)])`. Chạy **trước** handler, `raise HTTPException` ~
  `return res.status(401)...` (không gọi `next()`). `/health` không gắn thì không bị kiểm.
- **Khác 1: trả giá trị thẳng vào tham số.** Middleware Express phải nhét vào `req.user` / `req.pagination` (không có
  type, dễ quên). Depends trả về đúng kiểu, pyright kiểm được (`params.limit`, `openai_client.responses`).
- **Khác 2: tự đọc input.** Dependency khai `Header()`, `Query()` như route → FastAPI tự parse + validate + đưa vào
  `/docs`. Middleware Express tự đọc `req.header(...)`, tự validate, docs không biết.
- **Khác 3: lồng nhau + cache.** Dependency có thể phụ thuộc dependency khác, FastAPI tự gọi đúng thứ tự, và trong
  1 request cùng dependency chỉ chạy 1 lần. _(theo docs, chưa thử)_
- `app.use(...)` toàn cục ~ `FastAPI(dependencies=[...])` hoặc middleware thật của FastAPI (`@app.middleware("http")`,
  `CORSMiddleware` ở Bài 5). _(chưa thử)_

Lấy client qua Depends thay vì import thẳng biến global, lợi gì:

- **Thay được khi test** (Bài 5): `app.dependency_overrides[get_openai_client] = lambda: FakeClient()` → test `/chat`
  không gọi OpenAI thật, không tốn tiền, không cần mạng, kết quả cố định. Biến global thì phải monkeypatch module.
- **Đổi 1 chỗ**: muốn đổi client (model khác, timeout, client riêng mỗi user) chỉ sửa `get_openai_client`.
- **Hàm route khai rõ nó cần gì** (đọc chữ ký hàm là biết), giống DI qua constructor bên NestJS thay vì `import`
  instance.

## Bài 5 — CORS + TestClient

_(Claude viết, 2026-10-11, `curl -i` vào `fastapi dev` port 8000. Dòng `evil.example` GET là output bạn chạy)_

Cấu hình cuối:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,          # thừa: app không dùng cookie → nên bỏ
    allow_methods=["GET", "POST"],
    allow_headers=["content-type", "x-api-key"],
)
```

CORS (`curl -i`):

| Request                                         | Mã      | Header CORS trả về                                                                                 | Ghi chú |
| ----------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------- | ------- |
| `GET /health`, `Origin: http://localhost:3000`  | 200     | `access-control-allow-origin: http://localhost:3000`, `vary: Origin`                               | Trình duyệt cho JS đọc |
| `GET /health`, `Origin: http://evil.example`    | 200     | **không có** `access-control-allow-origin` (chỉ `vary: Origin`, `allow-credentials: true`)          | **Vẫn chạy route, vẫn trả body** `{"status":"ok"}`. Trình duyệt chặn JS đọc |
| Preflight `OPTIONS /chat` từ `localhost:3000`   | 200     | `allow-origin: http://localhost:3000`, `allow-methods: GET, POST`, `allow-headers: ... content-type, x-api-key`, `max-age: 600` | Trình duyệt được phép gửi POST thật |
| Preflight `OPTIONS /chat` từ `evil.example`     | **400** | không có `allow-origin`, body `Disallowed CORS origin`                                             | Trình duyệt **không gửi** POST thật |

Lỗi đã gặp: `allow_origins=["localhost:3000"]` (thiếu `http://`)

- Kết quả: origin **hợp lệ** cũng không có `access-control-allow-origin`, preflight trả **400**. Không origin nào
  dùng được.
- `Origin` trình duyệt gửi luôn đủ **scheme + host + port** (`http://localhost:3000`), so khớp **nguyên chuỗi**.
  `localhost` ≠ `127.0.0.1`, không có `/` cuối.
- `allow_methods=["*"]`, `allow_headers=["*"]` lúc đầu: preflight báo cho phép cả `DELETE, PATCH, PUT...`. Thu hẹp
  còn đúng cái cần. Ghi rõ `x-api-key` vì thiếu nó thì trình duyệt chặn `POST /chat` dù key đúng.

CORS do ai chặn, vì sao curl / Postman không bị:

- **Trình duyệt chặn, server không chặn.** Server chỉ thêm / không thêm header `access-control-allow-origin`. Thiếu
  header → trình duyệt nhận response nhưng **không đưa cho JS**, console báo đúng câu:
  `blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource`. Câu đó mô tả
  đúng cái curl thấy: response thiếu header.
- Request có header lạ (`x-api-key`) hoặc method khác GET/POST đơn giản → trình duyệt gửi **preflight `OPTIONS`**
  trước. Origin lạ → 400 → trình duyệt **không gửi request thật**, route không chạy.
- **curl / Postman không phải trình duyệt** → không kiểm header CORS, đọc được hết.
- Vì sao server không tự trả 403 theo `Origin`: header `Origin` do client gửi, curl giả được
  (`-H "Origin: http://localhost:3000"`) hoặc bỏ đi. Chỉ trình duyệt gửi `Origin` trung thực (JS không sửa được) →
  việc kiểm CORS giao cho trình duyệt. Muốn server chặn sớm thì tự viết dependency / middleware trả 403 khi `Origin`
  **có mà không hợp lệ** (không chặn khi thiếu `Origin`, nếu không curl / `TestClient` hỏng). Chỉ là lớp phụ.
- CORS bảo vệ **người dùng trong trình duyệt** (trang lạ không dùng được phiên / cookie của họ để đọc dữ liệu). Bảo
  vệ **API** khỏi bị gọi trực tiếp là việc của `X-API-Key` (Bài 4) + rate limit (Buổi 10–11).

  | Lớp           | Chống ai                                           |
  | ------------- | -------------------------------------------------- |
  | CORS          | Trang lạ dùng trình duyệt của user để đọc dữ liệu  |
  | `X-API-Key`   | Bất kỳ ai gọi trực tiếp (curl, script)             |
  | Rate limit    | Spam (Buổi 10–11)                                  |

- `allow_credentials=True` chỉ cần khi frontend gửi **cookie** (`fetch(..., { credentials: "include" })`). App dùng
  header key → không cần. Khi bật thì không được dùng `allow_origins=["*"]`. _(theo spec CORS, chưa thử)_
- `vary: Origin`: báo cache (CDN / proxy) rằng response khác nhau theo `Origin`, đừng trả nhầm.
- Bên Express: `app.use(cors({ origin: "http://localhost:3000" }))`. Cùng hành vi: thiếu scheme cũng hỏng, server
  cũng không chặn.

Test (`uv run pytest weeks/week02/session08`):

_(`test_health` bạn viết, 5 test còn lại Claude viết theo yêu cầu, 2026-10-11)_

```
test_health                     PASSED   GET /health → 200 {"status":"ok"}
test_orders_filter_by_customer  PASSED   GET /orders?customer=An → 200, total == 5, mọi đơn là của An
test_order_invalid_id           PASSED   GET /orders/abc → 422, loc == ["path","order_id"]
test_order_not_found            PASSED   GET /orders/9999 → 404 {"detail":"Order 9999 not found"}
test_chat_missing_api_key       PASSED   POST /chat không header → 401 {"detail":"Missing API Key"}
test_chat_empty_message         PASSED   POST /chat có key đúng, message "" → 422 string_too_short
6 passed in 1.60s
```

- `TestClient(app)` gọi app **trong cùng process**, không cần bật server (~ `supertest(app)` bên Express). Pyright +
  ruff sạch, `from exercises import app` chạy được vì pytest tự thêm thư mục chứa file test vào `sys.path`.
- **Không test nào gọi OpenAI**: 401 / 422 bị chặn trước hàm `chat`. Chạy nhanh, không tốn tiền, không cần mạng.
- Kiểm cả **nội dung lỗi** (`loc`, `type`, `detail`), không chỉ mã → biết 422 đến từ đúng chỗ.
  - `test_orders_filter_by_customer` kiểm thêm "mọi đơn là của An": `total == 5` đúng mà `orders` lẫn khách khác vẫn
    bị bắt (đúng bug cắt trang trước khi lọc ở Bài 4).
- `test_chat_empty_message` **phải gửi key đúng**: không key thì dependency trả 401 trước, không bao giờ thấy 422.
  Key đọc bằng `os.getenv("APP_API_KEY")` (`exercises.py` gọi `load_dotenv()` lúc import). Thiếu env thì test báo
  rõ "APP_API_KEY chưa có trong .env" thay vì lỗi khó hiểu.
- `client.get("/orders", params={...})` ~ `axios.get(url, { params })`. `def test_...` ~ `it(...)`,
  `assert a == b` ~ `expect(a).toBe(b)`.
- Chưa làm (tuỳ chọn): test `/chat` **thành công** không gọi OpenAI bằng `app.dependency_overrides[get_openai_client]`.

## So sánh FastAPI vs Express / Next API routes

_(Bản tham khảo do Claude viết, 2026-10-11, gom từ Bài 1–5. Phần Express / Next theo hiểu biết, buổi này không
chạy Express)_

| Chủ đề                  | Express / Next API routes                                                                 | FastAPI (đã làm trong buổi)                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Khai báo route          | `app.get("/orders/:id", handler)`. Next: file `app/api/orders/[id]/route.ts` export `GET` | Decorator `@app.get("/orders/{order_id}")` trên hàm. **Thứ tự khai báo** quyết định route nào khớp trước (Bài 1)    |
| Path / query params     | `req.params.id`, `req.query.x` luôn là **string**, tự `Number(...)`                      | **Tham số hàm + type hint**: có trong `{...}` → path, không có → query, có default → tuỳ chọn. Tự ép kiểu (`int`, `Literal`) |
| Validate body           | Tự gọi Zod `schema.parse(req.body)` trong handler                                         | Tham số kiểu `BaseModel` → tự parse + validate (`Field(min_length, max_length)`, `extra="forbid"`) **trước** khi vào hàm |
| Lỗi validate            | Tự viết: thường `400` + format tự chọn                                                    | Tự động **422**, body `{"detail": [{type, loc, msg, input}]}`. Kể cả JSON hỏng (`json_invalid`), không phải 400     |
| Trả JSON                | `res.json(obj)` / `Response.json(obj)`. Lỗi: `return res.status(404).json(...)`           | `return` dict / Pydantic. Lỗi: **`raise HTTPException(404, detail=...)`**. `response_model` lọc field thừa ở đầu ra |
| Docs API                | Viết tay (`swagger-jsdoc`) hoặc sinh từ Zod → dễ lệch code                                | `/docs` + `/openapi.json` **tự sinh** từ type hint, luôn khớp code                                                  |
| Middleware / DI         | `app.use(mw)` toàn cục, `app.get(path, mw, handler)` từng route, gắn giá trị lên `req.xxx` | `Depends(...)` từng route (`dependencies=[...]` nếu chỉ kiểm, tham số nếu trả giá trị). Middleware thật (`add_middleware`) cho toàn app (CORS) |
| Lỗi không bắt           | Dev: 500 + **HTML có stack trace**. Prod: "Internal Server Error". Express 4: lỗi `async` không tự bắt | **500** `text/plain` "Internal Server Error", không lộ gì kể cả khi dev. Traceback chỉ ở terminal. `HTTPException` = lỗi đã xử lý, không traceback |
| Async / chặn event loop | 1 event loop, mọi handler chạy trên đó. Code sync nặng → chặn cả server                    | `async def` chạy trên loop (chặn được, 5 req → 5.04 s). **`def` chạy threadpool** (40 thread, 5 req → 1.03 s). Trộn `async def` + client sync = xếp hàng (6.58 s) |
| CORS                    | `app.use(cors({ origin }))`. Next: tự set header trong route / middleware                 | `CORSMiddleware(allow_origins=["http://localhost:3000"], ...)`. Server không chặn, chỉ thêm header, trình duyệt chặn |
| Test                    | `supertest(app)` + Jest / Vitest                                                          | `TestClient(app)` + pytest, cùng process, không bật server. `dependency_overrides` thay dependency khi test          |
| Dev server reload       | `nodemon` / `next dev`                                                                    | `fastapi dev file.py` (tự tìm biến `app`, tự reload). Đo / test thì **đợi reload xong** mới chạy                     |

Bản của mình (3 điểm khác lớn nhất, viết lại bằng lời của mình):

-

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

_(Bản tham khảo do Claude viết, 2026-10-11, dựa trên số đo trong buổi. Dưới mỗi câu có "Bản của mình")_

### 1. Trong FastAPI, `async def` và `def` khác nhau thế nào? Viết sai thì bị gì?

> `async def` chạy **thẳng trên event loop** (1 thread), hợp với code toàn `await` (client async). `def` được FastAPI
> đẩy sang **threadpool** (mặc định 40 thread), hợp với code sync chặn (thư viện sync, `pandas`). Sai nguy hiểm nhất
> là gọi code **sync chặn trong `async def`**: nó chặn cả event loop, mọi request khác xếp hàng. Đo 5 request song
> song: `async def` + `time.sleep(1)` mất 5.04 s, `def` 1.03 s, `async def` + `await asyncio.sleep(1)` 1.01 s.
> `/chat` dùng `async def` + client `OpenAI()` sync mất 6.58 s (xong lần lượt), đổi `AsyncOpenAI` + `await` còn 1.78 s.

- Pyright và ruff không bắt được lỗi trộn client sync (ruff `ASYNC251` chỉ bắt `time.sleep`) → chỉ **đo song song**
  mới thấy. Test tay từng request một thì route nào cũng ~1 s.
- Không chắc thì dùng `def` (an toàn, chỉ tốn thread). Cần stream / nhiều user chờ I/O lâu → `async def` + client async.
- Liên hệ Node: Node chỉ có kiểu `async def`, cũng bị chặn bởi code sync (`while` nặng, `readFileSync`), nhưng Node
  ít thư viện sync nên khó lỡ tay hơn.

Bản của mình:

-

### 2. FastAPI khác Express ở điểm nào quan trọng nhất?

> **Type hint là nguồn sự thật duy nhất.** Khai kiểu trên tham số hàm là FastAPI tự parse, ép kiểu, validate (sai →
> 422, chưa vào hàm), đọc đúng chỗ (path / query / header / body), và sinh docs OpenAPI. Bên Express mỗi việc đó là
> 1 bước tự làm (`req.query` là string, Zod parse, viết Swagger tay) và dễ lệch nhau. Đi kèm là `Depends` (DI có
> kiểu, thay được khi test) thay cho middleware gắn giá trị lên `req`. Điểm khác thứ hai là mô hình chạy: Express 1
> event loop, FastAPI có cả `async def` (loop) lẫn `def` (threadpool), viết nhầm là chặn server.

- Mặt trái: khai sai chỗ là đọc sai chỗ mà không báo. Ví dụ đã gặp: `x_api_key: str` thiếu `Header()` thành **query
  param**, key bị đẩy lên URL. Query model trộn với query param khác → mọi request 422.
- Body lỗi đã có format chuẩn (`detail` + `loc`), client Next.js xử lý 1 kiểu cho mọi route (trừ `HTTPException` tự
  viết có `detail` là chuỗi, 500 không phải JSON).

Bản của mình:

-

### 3. CORS là gì, ai chặn, cấu hình thế nào cho frontend Next.js gọi backend?

> CORS là cơ chế của **trình duyệt**: JS ở origin A (`http://localhost:3000`) chỉ đọc được response từ origin B
> (`http://127.0.0.1:8000`) nếu B trả header `access-control-allow-origin` cho phép A. **Server không chặn**: request
> từ origin lạ vẫn chạy route và trả body, chỉ thiếu header → trình duyệt không đưa response cho JS. Request có
> header lạ (`x-api-key`) thì trình duyệt gửi **preflight `OPTIONS`** trước, bị từ chối thì không gửi request thật.
> curl / Postman không kiểm nên không bị. Cấu hình FastAPI: `CORSMiddleware` với `allow_origins=["http://localhost:3000"]`
> (đủ `http://`, không `/` cuối), `allow_methods=["GET","POST"]`, `allow_headers=["content-type","x-api-key"]`.

- Lỗi đã gặp: thiếu `http://` → không origin nào được phép, preflight 400.
- CORS bảo vệ **user trong trình duyệt**, không bảo vệ API. API được bảo vệ bằng `X-API-Key` (+ rate limit Buổi 10–11):
  `Origin` giả được bằng curl.
- Không dùng `allow_origins=["*"]` cho API có key. `allow_credentials=True` chỉ khi dùng cookie.
- Production: thêm domain thật của frontend (vd `https://app.example.com`), đọc từ env thay vì hard-code.

Bản của mình:

-
