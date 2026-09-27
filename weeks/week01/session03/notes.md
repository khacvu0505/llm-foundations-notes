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

| Câu | Token (Việt) | Token (Anh) | Tỉ lệ |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

Không dấu thì sao:

Vì sao tiếng Việt tốn token hơn:

-

## Bài 5 — Cost

- Model và giá (ngày tra):
- Cost 1 request:
- Ước tính 1000 user × 20 tin/ngày × 30 ngày:
- Input hay output đắt hơn:
