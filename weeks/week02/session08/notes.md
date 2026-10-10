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

- [ ] **Cài FastAPI:** `uv add "fastapi[standard]"` (để trong ngoặc kép, zsh hiểu `[...]` là pattern).
      Kéo theo `uvicorn` (server, ~ Node http server), `fastapi-cli` (lệnh `fastapi dev`), `httpx` (bản
      gốc, `TestClient` cần). `httpx` này **khác** `httpx2` mà `openai` đang dùng (Buổi 7), 2 cái cùng tồn
      tại được.
- [ ] **Kiểm:** `uv tree --depth 1` thấy `fastapi` ngang hàng `openai`.
- [ ] **Dữ liệu:** copy `orders.csv` từ session07 sang session08 (mỗi buổi 1 thư mục độc lập).
- [ ] **`.env`:** thêm 1 dòng `APP_API_KEY=<tự đặt>` cho Bài 4. Không commit `.env`.
- [ ] **Chạy thử:** viết xong app + `/health` ở Bài 1 thì
      `uv run fastapi dev weeks/week02/session08/exercises.py` → mở http://127.0.0.1:8000/docs
- [ ] Đọc nhanh tutorial: First Steps, Path Parameters, Query Parameters, Request Body, Handling Errors,
      Dependencies, CORS, Testing (https://fastapi.tiangolo.com/tutorial/) + trang
      https://fastapi.tiangolo.com/async/ mục "In a hurry?".

## Nợ từ Buổi 7 (làm lúc rảnh, không chặn Buổi 8)

- [ ] Notion: tick Buổi 7 + ghi "Status dd/mm/yyyy" (học được gì / còn nợ gì)
- [ ] Code hàm cắt lịch sử theo lượt (ranh giới `user`, bỏ cặp tool ở lượt cũ) — notes Buổi 7 mục Bài 5
- [ ] Chạy lại Bài 4d sau khi sửa câu trả lời cố định khi chạm `MAX_STEPS` (chưa chạy lại)
- [ ] (Tuỳ chọn) Sinh tool schema từ Pydantic; tool `save_order`
- [ ] Nợ Buổi 6 vẫn còn (xem `session07/notes.md` mục "Nợ từ Buổi 6")
- [ ] Nhật ký Tuần 2 trên Notion (cuối tuần, 2–3 dòng "học được gì / vướng gì")

## Bài 1 — Routes, path params, query params

Lệnh / request đã thử và kết quả (mã + body):

| Request                         | Mã  | Body / ghi chú |
| ------------------------------- | --- | -------------- |
| `GET /health`                   |     |                |
| `GET /orders?customer=An`       |     |                |
| `GET /orders?status=abc`        |     |                |
| `GET /orders/1003`              |     |                |
| `GET /orders/abc`               |     |                |
| `GET /orders/summary` (đặt sau) |     |                |

Query param bên Express là string, bên FastAPI là gì:

-

422 là gì, khác 400 chỗ nào, lỗi validate xảy ra trước hay sau khi vào hàm:

-

Thứ tự route (`/orders/summary` vs `/orders/{order_id}`):

-

`/docs` so với tự viết Swagger bên Express:

-

## Bài 2 — Request body Pydantic, POST /chat

| Thử                                    | Mã  | Body / ghi chú | Có gọi OpenAI không |
| -------------------------------------- | --- | -------------- | ------------------- |
| a) body đúng                           |     |                |                     |
| b) thiếu `message`                     |     |                |                     |
| c) `message = ""`                      |     |                |                     |
| d) `message` 600 ký tự                 |     |                |                     |
| e) thêm field lạ `foo`                 |     |                |                     |
| e') thêm field lạ + `extra="forbid"`   |     |                |                     |
| f) body không phải JSON                |     |                |                     |

`response_model` lọc field nội bộ:

-

Giới hạn 500 ký tự ở model Pydantic thay vì `if` trong hàm, lợi gì (liên hệ chống spam Buổi 10–11):

-

## Bài 3 — async def vs def + xử lý lỗi

5 request song song (`bench.py`):

| Route                                      | Đoán trước | Tổng thời gian đo | Vì sao |
| ------------------------------------------ | ---------- | ----------------- | ------ |
| `/slow/def` (`def` + `time.sleep`)         |            |                   |        |
| `/slow/async-block` (`async def` + `time.sleep`) |      |                   |        |
| `/slow/async-await` (`async def` + `await asyncio.sleep`) | |                |        |
| `/chat` với client OpenAI sync             |            |                   |        |
| `/chat` với `AsyncOpenAI`                  |            |                   |        |

Khi nào dùng `def`, khi nào `async def`:

-

Bên Node có chuyện "1 hàm chặn cả server" không:

-

Lỗi:

| Tình huống                         | Mã  | Client thấy gì | Terminal in gì |
| ---------------------------------- | --- | -------------- | -------------- |
| `/orders/9999` (HTTPException)     |     |                |                |
| OpenAI lỗi (MODEL sai) → bắt, 502  |     |                |                |
| `raise ValueError` không bắt       |     |                |                |

404 / 422 / 500 / 502 khác nhau thế nào, ai trả mã nào:

-

## Bài 4 — Dependency injection (Depends)

| Gọi `/chat`            | Mã  | Body |
| ---------------------- | --- | ---- |
| không có `X-API-Key`   |     |      |
| sai key                |     |      |
| đúng key               |     |      |
| `/health` không key    |     |      |

Depends giống / khác middleware Express thế nào:

-

Lấy client qua Depends thay vì import thẳng biến global, lợi gì:

-

## Bài 5 — CORS + TestClient

CORS (`curl -i`):

| Request                                       | Header CORS trả về | Ghi chú |
| --------------------------------------------- | ------------------ | ------- |
| `Origin: http://localhost:3000`               |                    |         |
| `Origin: http://evil.example`                 |                    |         |
| Preflight `OPTIONS /chat`                     |                    |         |

CORS do ai chặn, vì sao curl / Postman không bị:

-

Test (`uv run pytest weeks/week02/session08`):

-

## So sánh FastAPI vs Express / Next API routes

| Chủ đề                         | Express / Next API routes | FastAPI |
| ------------------------------ | ------------------------- | ------- |
| Khai báo route                 |                           |         |
| Path / query params            |                           |         |
| Validate body                  |                           |         |
| Lỗi validate                   |                           |         |
| Trả JSON                       |                           |         |
| Docs API                       |                           |         |
| Middleware / DI                |                           |         |
| Lỗi không bắt                  |                           |         |
| Async / chặn event loop        |                           |         |
| CORS                           |                           |         |
| Test                           |                           |         |
| Dev server reload              |                           |         |

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

### 1. Trong FastAPI, `async def` và `def` khác nhau thế nào? Viết sai thì bị gì?

### 2. FastAPI khác Express ở điểm nào quan trọng nhất?

### 3. CORS là gì, ai chặn, cấu hình thế nào cho frontend Next.js gọi backend?
