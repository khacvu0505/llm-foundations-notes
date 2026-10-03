# Buổi 4 — Ghi chú quan sát

## Setup

- Không cần cài thêm thư viện: `openai` và `python-dotenv` đã có từ Buổi 3, `asyncio` và `time` có sẵn trong Python.
- Dùng lại file `.env` ở thư mục gốc.

## Bài 1 — AsyncOpenAI khác OpenAI thế nào

- API y hệt nhau (`client.responses.create(model=..., input=...)`, `response.output_text`), chỉ khác client và chữ `await`.
- Hàm dùng `AsyncOpenAI` phải là `async def`, và code thường gọi nó bằng `asyncio.run(...)`.
- Vẫn tạo 1 client ở cấp module rồi dùng lại, như Buổi 3.
- Khác TS: SDK Node vốn đã async (mọi lời gọi trả Promise). Python có 2 client riêng, phải chọn sync hay async.

## Bài 2 — Tuần tự vs song song

| Cách chạy | Thời gian |
|---|---|
| Tuần tự, 3 prompt | 8.61 s |
| Song song (gather), 3 prompt | 2.64 s |

Model `gpt-4o-mini`, chạy ngày 2026-09-30. Song song nhanh hơn ~3.3 lần, xấp xỉ đúng số prompt.

Vì sao:

- Tuần tự: `await` từng lời gọi trong vòng `for`, lời sau chỉ bắt đầu khi lời trước xong, nên thời gian ≈ tổng 3 lời gọi.
- Song song: `asyncio.gather` gửi cả 3 lời gọi cùng lúc. Trong lúc chờ server trả lời, event loop không bị chặn, nên thời gian ≈ lời gọi chậm nhất.
- Giống `Promise.all` bên TS.

## Bài 3 — Streaming

| Chỉ số | Giá trị |
|---|---|
| TTFT | 1.73 s |
| Tổng thời gian | 3.16 s |

Model: `gpt-6-luna`, prompt "Giới thiệu Đà Lạt trong 5 câu".
Usage: input 17 token, output 155 token (trong đó 22 reasoning token), tổng 172.

- TTFT chiếm hơn nửa tổng thời gian: người dùng chờ 1.73 s mới thấy chữ đầu tiên, phần text còn lại chảy ra trong ~1.4 s.
- Reasoning token nằm trong output token: model "nghĩ" 22 token trước khi ra chữ, nên góp phần làm TTFT dài. Reasoning token không hiện ra text nhưng vẫn tính tiền như output.

Các loại event thấy trong stream:

Xếp theo cấu trúc mở → đóng (model `gpt-6-luna`, số lần trong 1 lần chạy):

| Event | Số lần | Ý nghĩa |
|---|---|---|
| `response.created` | 1 | Server nhận request, tạo response |
| `response.in_progress` | 1 | Bắt đầu sinh |
| `response.output_item.added` | 2 | Thêm 1 item vào output |
| `response.content_part.added` | 1 | Bắt đầu 1 phần nội dung text |
| `response.output_text.delta` | 129 | Mỗi mảnh text mới |
| `response.output_text.done` | 1 | Text xong |
| `response.content_part.done` | 1 | Phần nội dung xong |
| `response.output_item.done` | 2 | Item xong |
| `response.completed` | 1 | Response đầy đủ, có `usage` |

- `output_item` xuất hiện 2 lần: có thể là 1 item reasoning + 1 item message chứa text (suy luận, chưa kiểm chứng bằng cách in `event.item.type`).
- Stream có cấu trúc lồng nhau: response → output item → content part → delta. Phần lớn event là delta (129/139).
- 2 loại dùng trong bài: `response.output_text.delta` (1 mảnh text, ở `event.delta`) và `response.completed` (response đầy đủ, có `usage`, ở `event.response`)

Bỏ `flush=True` thì sao:

- Text không còn hiện ra từng mảnh, mà đợi đến cuối mới hiện cả đoạn.
- Lý do: `print` ghi vào bộ đệm (buffer) của `sys.stdout`. Trên terminal, buffer chỉ được đẩy ra màn hình khi gặp `\n`. Vì dùng `end=""` nên các mảnh không có `\n`, cứ nằm trong buffer đến lúc `print()` xuống dòng ở event `response.completed`.
- `flush=True` ép đẩy buffer ra ngay sau mỗi lần print, nên mỗi mảnh hiện ra liền.
- Liên hệ: stream lên web (SSE, Buổi 9) cũng gặp chuyện tương tự. Nếu proxy/server buffer thì UI không thấy chữ chạy dần.

## Bài 4 — Streaming bất đồng bộ

Khác Bài 3 ở đâu:

- Client `AsyncOpenAI()` thay cho `OpenAI()`.
- Lời gọi `create(..., stream=True)` phải `await` mới nhận được stream.
- Duyệt bằng `async for event in stream` thay cho `for`. Bên TS tương đương `for await (const event of stream)`.
- Vừa in từng mảnh, vừa gom vào chuỗi rồi `return` sau vòng lặp, để hàm luôn trả về `str` kể cả khi stream không có event `response.completed`.

Vì sao async không làm 1 lời gọi nhanh hơn:

- Thời gian chủ yếu là chờ server OpenAI sinh token, sync hay async đều phải chờ như nhau.
- Lợi ích của async: trong lúc chờ, event loop làm việc khác được, ví dụ chạy nhiều lời gọi cùng lúc (Bài 2, Bài 5) hoặc phục vụ nhiều request trên web server (nền cho Buổi 9, SSE về Next.js).

## Bài 5 — 3 model song song

Giá tra ngày: 2026-09-30, nguồn developers.openai.com/api/docs/pricing (USD / 1M token)

| Model | Input | Output |
|---|---|---|
| `gpt-4.1-nano` | 0.10 | 0.40 |
| `gpt-4o-mini` | 0.15 | 0.60 |
| `gpt-6-luna` | 0.10 | 0.50 |

Kết quả, prompt "Giới thiệu Đà Lạt trong 5 câu":

| Model | Latency | Input token | Output token | Cost |
|---|---|---|---|---|
| `gpt-4.1-nano` | 3.14 s | 18 | 190 | $0.000078 |
| `gpt-4o-mini` | 3.42 s | 18 | 182 | $0.000112 |
| `gpt-6-luna` | 2.96 s | 17 | 169 | $0.000086 |

Tổng thời gian khi chạy song song: 3.46 s

- ≈ model chậm nhất (`gpt-4o-mini` 3.42 s), đúng dự đoán. Nếu chạy tuần tự sẽ ≈ tổng 3 latency = 9.52 s, nên song song nhanh gần gấp 3.
- Chênh 0.04 s so với model chậm nhất là overhead của event loop / tạo request.

Model nhanh nhất / rẻ nhất / trả lời tốt nhất:

- **Nhanh nhất:** `gpt-6-luna` (2.96 s), nhưng 3 model chỉ chênh nhau ~0.5 s trong 1 lần chạy. Mức này nằm trong nhiễu mạng, cần chạy nhiều lần mới kết luận được.
- **Rẻ nhất:** `gpt-4.1-nano` ($0.000078). Đắt nhất là `gpt-4o-mini`, gấp ~1.4 lần, do giá output cao nhất (0.60).
- `gpt-6-luna` không chậm/đắt như dự đoán ở đề: với prompt đơn giản này, reasoning token ít (Bài 3 thấy 22 token), và giá niêm yết rẻ ngang model nhỏ.
- **Chất lượng:** cả 3 đều đúng 5 câu, đúng tiếng Việt, nội dung tương đương nhau.
  - `gpt-4.1-nano`: nhiều chi tiết cụ thể nhất (thác Prenn, chùa Linh Phước, đặc sản dâu tây, bánh căn).
  - `gpt-4o-mini`: có số liệu (độ cao 1.500 m), giọng văn du lịch.
  - `gpt-6-luna`: ngắn gọn nhất, có thông tin hành chính (tỉnh Lâm Đồng) nhưng ghi "miền Trung" hơi mơ hồ, thường gọi là Tây Nguyên.
- **Kết luận:** với việc đơn giản như giới thiệu ngắn, `gpt-4.1-nano` là lựa chọn hợp lý nhất: rẻ nhất, nhanh ngang, chất lượng không thua. Model đắt hơn chỉ đáng dùng khi việc cần suy luận nhiều hơn.
- Lưu ý: output token của `gpt-6-luna` gồm cả reasoning token, nên cost thực cao hơn phần text nhìn thấy.
