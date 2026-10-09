# Buổi 8 — FastAPI cơ bản (phần code; quan sát ghi ở notes.md cùng thư mục)
#
# Luật chơi: tự viết code dưới mỗi đề bài, tra docs chính thức khi cần:
#   https://fastapi.tiangolo.com/tutorial/first-steps/   (rồi đi lần lượt các trang tutorial)
#   https://fastapi.tiangolo.com/async/                  (async def vs def)
# Import cần gì tự thêm ở đầu file. Cả buổi dùng CHUNG 1 app trong file này, mỗi bài thêm route.
#
# Chuẩn bị: làm mục "Setup (tự làm)" trong notes.md trước (cài fastapi, copy orders.csv, .env).
#
# Chạy server:  uv run fastapi dev weeks/week02/session08/exercises.py
#               → http://127.0.0.1:8000/docs  (Swagger UI tự sinh, thử request ngay trên web)
#               fastapi dev tự reload khi lưu file (~ nodemon / next dev)
# Gọi thử:      curl -s http://127.0.0.1:8000/health
# Test (Bài 5): uv run pytest weeks/week02/session08
# Vệ sinh:      uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Nhắc lại từ các buổi trước:
#   - Pydantic BaseModel, Field(...), validate, lax vs strict (Buổi 5).
#   - AsyncOpenAI + await, asyncio.gather, đo thời gian tuần tự vs song song (Buổi 4, Buổi 7 bài 3).
#   - query_orders + orders.csv, Status Literal, TypedDict (Buổi 7 bài 2).
#   - PRICES + cost_usd, response.usage có thể None (Buổi 6, Buổi 7 bài 5).
#   - Lỗi gửi ra ngoài phải gọn, không lộ str(e) / stack trace / URL có key (Buổi 7 bài 4).
#   - Mỗi buổi 1 file độc lập: CHÉP code cần dùng, không import chéo từ session khác (Buổi 7 bài 5).
#
# Ý tưởng chính (so với TS / Express):
#   Express:  app.get("/orders/:id", (req, res) => { const id = Number(req.params.id); ... })
#             req.params / req.query luôn là string, tự parse + tự validate (Zod), tự viết docs.
#   FastAPI:  @app.get("/orders/{order_id}")
#             def get_order(order_id: int): ...
#             Type hint trên tham số hàm = parse + validate + sinh docs OpenAPI cùng lúc.
#             Sai kiểu → 422 tự động, chưa chạy vào hàm.
#             Return dict / Pydantic → JSON (~ res.json()).
#   Khác lớn nhất: Node chỉ có event loop. FastAPI có 2 kiểu hàm route:
#             async def → chạy trên event loop (như Node);  def → chạy trong threadpool.
#             Viết sai kiểu là server "đứng hình" (Bài 3).
#
# Hướng tới: Buổi 9 (SSE stream về Next.js) và Buổi 10–11 (Project #1: endpoint chat + tools +
#   stream + cost log + chống spam) đều xây trên app này. Viết sạch thì buổi sau đỡ vất.


# ============================================================================
# Bài 1 — App đầu tiên: routes, path params, query params
# ============================================================================
#
# Yêu cầu:
#   - Tạo app FastAPI (đặt title cho dễ nhận ra trên /docs). Route GET /health → {"status": "ok"}.
#     Chạy server, mở /docs, gọi thử bằng curl. So /docs với việc tự viết Swagger bên Express.
#   - Chép query_orders + Status + OrderItem từ Buổi 7 (đọc orders.csv cùng thư mục session08).
#   - GET /orders?customer=An&status=pending
#       customer, status là query param TUỲ CHỌN (không truyền = không lọc, như Buổi 7).
#       status khai kiểu Status (Literal) → thử status=abc: server trả gì, mã mấy? Đọc body lỗi.
#   - GET /orders/{order_id} → trả 1 đơn. order_id khai kiểu int.
#       Thử /orders/1003, /orders/abc, /orders/9999. Tạm thời không tìm thấy thì trả gì cũng được
#       (Bài 3 sẽ đổi sang 404 chuẩn).
#   - Thêm route GET /orders/summary (tổng số đơn + tổng tiền mọi khách) và đặt nó SAU
#     /orders/{order_id} trong file. Gọi /orders/summary → chuyện gì xảy ra, vì sao? Sửa thế nào?
#
# Gợi ý:
#   - Tham số hàm có trong path "{...}" → path param; không có → query param; có default → tuỳ chọn.
#   - Đọc kỹ trang docs "Path Parameters", mục "Order matters".
#   - curl -s "http://127.0.0.1:8000/orders?customer=An" | python -m json.tool  (in JSON đẹp)
#
# Câu hỏi ghi notes.md: query param bên Express là string, bên FastAPI là gì? 422 nghĩa là gì, khác
#   400 chỗ nào? Lỗi validate xảy ra trước hay sau khi chạy vào hàm của mình?

# TODO: viết code ở đây


# ============================================================================
# Bài 2 — Request body với Pydantic: POST /chat (1 lời gọi LLM, chưa tools, chưa stream)
# ============================================================================
#
# Yêu cầu:
#   - ChatRequest: message (str, không rỗng, tối đa 500 ký tự — dùng Field).
#     ChatResponse: reply, input_tokens, output_tokens, cost_usd.
#   - POST /chat nhận ChatRequest, gọi OpenAI 1 lần (instructions: trả lời ngắn, tiếng Việt),
#     trả ChatResponse. Khai response_model cho route. Chép PRICES + cost_usd từ Buổi 7.
#   - Thử bằng /docs hoặc curl, ghi lại mã + body trả về:
#       a) body đúng
#       b) thiếu field message
#       c) message = ""
#       d) message dài 600 ký tự
#       e) gửi thêm field lạ {"message": "hi", "foo": 1} → mặc định thế nào? Muốn từ chối thì sao?
#       f) gửi body không phải JSON (curl -d 'hello' -H "Content-Type: application/json")
#   - response_model lọc field: cho hàm return thêm 1 field nội bộ (vd tên model).
#     Client có thấy field đó không?
#
# Gợi ý:
#   - curl -s -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json"
#       -d '{"message": "Xin chào"}'
#   - Từ chối field lạ: model_config = ConfigDict(extra=...) (~ Zod .strict()).
#   - Bài này cứ dùng client OpenAI sync như các buổi trước. Bài 3 sẽ thấy vấn đề.
#
# Câu hỏi ghi notes.md: giới hạn 500 ký tự đặt ở model Pydantic thay vì if trong hàm thì lợi gì?
#   (liên hệ chống spam Buổi 10–11). Body hỏng bị chặn ở đâu, có tốn lời gọi OpenAI không?

# TODO: viết code ở đây


# ============================================================================
# Bài 3 — async def vs def + xử lý lỗi (HTTPException)
# ============================================================================
#
# Phần A — đo (quan trọng nhất buổi):
#   - 3 route giả lập việc chậm 1 giây:
#       GET /slow/def          → def,       time.sleep(1)
#       GET /slow/async-block  → async def, time.sleep(1)
#       GET /slow/async-await  → async def, await asyncio.sleep(1)
#   - Viết script nhỏ bench.py (cùng thư mục, chạy riêng khi server đang bật) bắn 5 request
#     SONG SONG vào từng route (asyncio.gather + httpx2.AsyncClient như Buổi 7 bài 3),
#     đo tổng thời gian.
#   - Đoán trước rồi đo: route nào ~1s, route nào ~5s? Vì sao?
#   - Liên hệ: /chat ở Bài 2 là async def hay def, đang dùng client OpenAI sync hay async?
#     Có giống route nào ở trên không? Nếu có vấn đề thì sửa (Buổi 4 đã dùng client nào?).
#     Đo lại 5 request /chat song song trước và sau khi sửa.
#
# Phần B — lỗi:
#   - GET /orders/{order_id} không tìm thấy → HTTPException 404, detail gọn. So với Bài 1.
#   - POST /chat khi OpenAI lỗi (tạm đổi MODEL thành tên sai): bắt lỗi của SDK openai, trả 502 với
#     detail gọn cho client, log chi tiết ra terminal. KHÔNG trả str(e) (nhớ Buổi 7 bài 4).
#   - Route cố tình raise ValueError (không bắt): client nhận gì, terminal in gì?
#     So với Express: lỗi không bắt trong route thì sao (dev vs production)?
#
# Gợi ý:
#   - Đọc trang docs "Concurrency and async / await" mục "In a hurry?".
#   - Lỗi SDK openai có class cha chung trong module openai (tra docs SDK / gõ openai. xem gợi ý).
#
# Câu hỏi ghi notes.md: khi nào dùng def, khi nào async def? Bên Node có chuyện "1 hàm chặn cả
#   server" không? 404 / 422 / 500 / 502 khác nhau thế nào, ai trả mã nào?

# TODO: viết code ở đây


# ============================================================================
# Bài 4 — Dependency injection cơ bản (Depends)
# ============================================================================
#
# Yêu cầu:
#   - Dependency trả client AsyncOpenAI dùng chung → /chat nhận client qua Depends thay vì dùng
#     biến global trực tiếp.
#   - Dependency kiểm header X-API-Key so với APP_API_KEY trong .env: sai/thiếu → 401.
#     Gắn cho /chat (route tốn tiền) nhưng KHÔNG gắn /health. Thử: không header, sai key, đúng key.
#   - (Tuỳ chọn) Dependency phân trang limit/offset dùng chung, gắn vào GET /orders.
#
# Gợi ý:
#   - Docs khuyên viết kiểu Annotated[Kiểu, Depends(ham)] (đọc trang "Dependencies").
#   - Header param: tra "Header Parameters" trong tutorial.
#   - Không bao giờ in / trả APP_API_KEY ra response hay log.
#
# Câu hỏi ghi notes.md: Depends giống/khác middleware Express (app.use vs middleware từng route) thế
#   nào? Lấy client qua Depends thay vì import thẳng biến global thì được lợi gì? (gợi ý: Bài 5)

# TODO: viết code ở đây


# ============================================================================
# Bài 5 — CORS + test bằng TestClient + tổng kết so với Express
# ============================================================================
#
# Phần A — CORS (chuẩn bị cho Buổi 9, Next.js chạy ở http://localhost:3000):
#   - Thêm CORSMiddleware, chỉ cho origin http://localhost:3000.
#   - Thử bằng curl -i với header Origin: http://localhost:3000 và Origin: http://evil.example.
#     Header trả về khác nhau thế nào? curl có bị "chặn" không?
#   - Preflight: curl -i -X OPTIONS /chat với Origin + Access-Control-Request-Method: POST
#     + Access-Control-Request-Headers: content-type,x-api-key.
#
# Phần B — test (file test_exercises.py cùng thư mục, tự tạo):
#   - Dùng TestClient (không cần bật server): /health 200, /orders lọc đúng (An = 5 đơn như Buổi 7),
#     /orders/abc 422, /orders/9999 404, /chat thiếu X-API-Key 401, /chat message rỗng 422.
#   - (Tuỳ chọn) /chat thành công mà KHÔNG gọi OpenAI thật: thay dependency bằng bản giả qua
#     app.dependency_overrides. Gợi ý: dependency nào dễ làm giả hơn — trả client, hay trả 1 hàm
#     ask(message) gọn?
#
# Gợi ý:
#   - Trang docs "CORS (Cross-Origin Resource Sharing)" và "Testing".
#   - TestClient cần thư viện httpx (bản gốc, đi kèm fastapi[standard]), khác httpx2 của openai.
#
# Câu hỏi ghi notes.md: CORS do ai chặn — server hay browser? Vì sao Postman/curl không bị?
#   Điền bảng so sánh FastAPI vs Express / Next API routes trong notes.md.

# TODO: viết code ở đây
