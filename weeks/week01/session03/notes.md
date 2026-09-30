# Buổi 3 — Ghi chú quan sát

## Setup (tự làm)

- [ ] **Cài thư viện.** Dùng `uv add` với 3 package: openai, tiktoken, python-dotenv.
      Giống `pnpm add`: uv tự thêm vào `pyproject.toml` và cập nhật `uv.lock`.
      Chạy xong, mở `pyproject.toml` xem mục `dependencies` thay đổi thế nào.
- [ ] **Kiểm `.env` đã bị git bỏ qua.** Tìm dòng `.env` trong `.gitignore`. Có sẵn rồi thì thôi.
- [ ] **Tạo file `.env`** ở thư mục gốc repo, mỗi dòng một key theo dạng `TEN_BIEN=giá_trị`,
      không dấu nháy, không khoảng trắng quanh dấu `=`. Tên biến: `OPENAI_API_KEY`.
- [ ] (Tùy chọn) **Tạo `.env.example`** cùng tên biến nhưng để trống giá trị, để commit lên git
      làm mẫu. Đây là convention giống bên Node.
- [ ] **Chạy `git status`** để chắc `.env` không xuất hiện trong danh sách file thay đổi.
- [ ] **Kiểm cài đặt:** mở REPL bằng `uv run python`, thử import 3 thư viện. Lưu ý tên import của
      python-dotenv là `dotenv`, khác tên package.

## Bài 1 — Cấu trúc response của OpenAI

-

## Bài 3 — Params

> Điền từ kết quả chạy thật ngày 27/09/2026. 3.1, 3.2 do mình chạy; 3.3–3.5 Claude chạy lại 1 lần.

**Model:** `gpt-6-luna` báo lỗi 400 "Unsupported parameter: 'temperature'" vì là model có suy luận
(`gpt-5-mini` cũng vậy). Bài 3 đổi sang `gpt-4o-mini`, model không suy luận.
Prompt: "Đặt 1 tên cho quán cà phê ở Đà Lạt. Chỉ trả lời tên." (3.3 dùng "Giới thiệu Đà Lạt trong 3 câu").

| Thử | Kết quả | Quan sát |
|---|---|---|
| temperature=0, chạy 3 lần | "Cà Phê Đà Lạt Mộng Mơ" × 3, 13 token mỗi lần | Giống hệt nhau: luôn chọn token xác suất cao nhất. |
| temperature=1, chạy 3 lần | "Cà phê Đà Lạt Mộng Mơ", "Cà Phê Sương Mù.", "Hồn Đà Lạt Coffee" (13, 10, 8 token) | Mỗi lần một khác. Token phổ biến vẫn có thể thắng, nhưng không chắc chắn. Độ dài và chi phí khó đoán. |
| max_output_tokens=16 | "Đà Lạt, được mệnh danh là "Thành phố ngàn" | Bị cắt giữa câu. `status=incomplete`, `reason='max_output_tokens'`, đúng 16 token. |
| top_p=0.1 vs 1.0 (1 lần mỗi mức) | 0.1: "Cà Phê Đà Lạt Mộng Mơ". 1.0: "Cà Phê Sương Mờ" | 0.1 ra đúng tên của temperature=0: chỉ chọn trong nhóm rất ít token xác suất cao. Chỉ chạy 1 lần nên chưa so được độ dao động. |
| temperature + top_p cùng lúc | 0.5 + 0.5: "Cà Phê Đà Lạt Mộng Mơ". 1 + 1: "Cà Phê Ngàn Thông" | `gpt-4o-mini` không báo lỗi khi truyền cả hai. |

Temperature tác động lên bước nào trong quá trình sinh token (nối với Buổi 2)?

- Bước chọn token tiếp theo từ bảng xác suất, sau softmax. Temperature thấp làm bảng xác suất "nhọn" hơn
  nên token đứng đầu gần như luôn thắng. Temperature cao làm bảng "phẳng" hơn nên token khác có cơ hội.
  Top_p thì cắt bớt: chỉ giữ nhóm token đứng đầu có tổng xác suất bằng p, rồi mới chọn.
- Model có suy luận (gpt-5, gpt-6) cố định phần này. Thứ chỉnh được là `reasoning.effort` và `text.verbosity`.

## Bài 4 — Token tiếng Việt vs tiếng Anh

> Kết quả chạy ngày 29/09/2026, bảng mã `o200k_base` (bảng mã của `gpt-4o-mini`).

| Câu | Token (Việt) | Token (Anh) | Tỉ lệ |
|---|---|---|---|
| Xin chào, hôm nay trời đẹp quá. | 10 | 9 | 1.11 |
| Tôi muốn đặt một bàn cho bốn người vào tối thứ Bảy. | 16 | 14 | 1.14 |
| Mô hình ngôn ngữ lớn dự đoán token tiếp theo dựa trên ngữ cảnh. | 21 | 11 | 1.91 |

Không dấu thì sao:

- Câu đặt bàn: có dấu 16 token, không dấu cũng 16 token. Bỏ dấu KHÔNG tiết kiệm token.
- Decode từng token:
  - Có dấu: `T` `ôi` ` muốn` ` đặt` ` một` ` bàn` ` cho` ` b` `ốn` ` người` ` vào` ` tối` ` thứ` ` B` `ảy` `.`
  - Không dấu: `To` `i` ` mu` `on` ` dat` ` mot` ` ban` ` cho` ` bon` ` ngu` `oi` ` vao` ` toi` ` thu` ` Bay` `.`
- Từ phổ biến có dấu ("muốn", "người", "thứ") là 1 token nguyên. Không dấu thì "muon", "nguoi" bị cắt đôi,
  còn "bon", "Bay" trùng từ tiếng Anh nên 1 token. Hai bên bù trừ nhau.
- Bỏ dấu còn làm model khó hiểu hơn: "ban" có thể là bàn / bạn / bán.

Vì sao tiếng Việt tốn token hơn:

- Bảng mã (tokenizer) học chủ yếu từ văn bản tiếng Anh, nên từ tiếng Anh thường là 1 token nguyên.
- Từ tiếng Việt ít gặp bị cắt thành nhiều mảnh; chữ có dấu ở vị trí lạ bị tách riêng ("B" + "ảy").
- Câu giao tiếp chỉ tốn hơn ~10% với `o200k_base`. Câu thuật ngữ tốn gần gấp đôi (1.91).
- tiktoken đếm tên quán "Cà Phê Đà Lạt Mộng Mơ" là 12 token, `usage` của API báo 13 → API thêm token đặc biệt.
  tiktoken dùng để ước tính, tính tiền thì lấy từ `usage`.

## Bài 5 — Cost

> Kết quả chạy ngày 29/09/2026.

- Model và giá (ngày tra): `gpt-4o-mini`, tra 29/09/2026 tại developers.openai.com/api/docs/pricing.
  Input $0.15, input đã cache $0.075, output $0.60 — tính theo 1 triệu token.
- Cost 1 request: prompt đặt tên quán cà phê → 30 token input, 6 token output → $0.000008
  (input $0.0000045 + output $0.0000036).
- Ước tính 1000 user × 20 tin/ngày × 30 ngày: $4.86/tháng.
- Input hay output đắt hơn: output đắt gấp 4 lần input (với `gpt-4o-mini`).

Quan sát thêm:

- Prompt ~17 token theo tiktoken nhưng `usage` báo 30 token input: API thêm token định dạng (role, ranh giới message).
- $4.86 là mức thấp nhất vì prompt quá ngắn. App thật: input mỗi request = system prompt + lịch sử hội thoại
  gửi lại (Bài 2) + context RAG + câu hỏi. Ví dụ ~4.000 input + 300 output → ~$0.00078/request → ~$468/tháng
  cho cùng 1000 user × 20 tin/ngày. Gấp ~100 lần, toàn bộ do token input.
- Yếu tố làm đổi chi phí: agent gọi nhiều request cho 1 tin nhắn; token suy luận tính giá output; chọn model khác;
  cache input giảm một nửa giá phần lặp lại; sliding window cắt lịch sử (Buổi 6).
- Ước tính đáng tin: log token của nhiều request thật rồi lấy trung bình (Langfuse, Phase 04 Buổi 10).
- Prompt tiếng Việt ảnh hưởng: câu thuật ngữ có thể tốn gần gấp đôi token so với tiếng Anh (Bài 4) → input đắt hơn.
