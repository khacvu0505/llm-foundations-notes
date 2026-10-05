# Buổi 6 — Lý thuyết #2 + CLI Chatbot (4h, T7)

Buổi dài, chia 2 phần:

| Phần                                                                                | Thời lượng | Làm ở đâu      |
| ----------------------------------------------------------------------------------- | ---------- | -------------- |
| A. Xem Karpathy "Intro to Large Language Models" (hoặc đọc bài Chip Huyen ~30–40ph) | ~1h        | mục A bên dưới |
| B. Đọc nhanh: fine-tune vs RAG vs prompt (LoRA)                                     | ~30ph      | mục B bên dưới |
| C. Build CLI chatbot (Bài 1–3)                                                      | ~1h45      | `exercises.py` |
| D. Sliding window + so với tóm tắt (Bài 4–5)                                        | ~45ph      | `exercises.py` |

## Setup

- Không cần cài thêm thư viện: `openai`, `tiktoken`, `python-dotenv` đã có từ Buổi 3.
- Dùng lại file `.env` ở thư mục gốc.

## Tóm tắt lý thuyết (bản tham khảo — Claude viết)

Xem trang ôn bài: https://claude.ai/artifact/Hv1mCw3KpNRo9UV8yaaZFL
(file gốc: `ly-thuyet.html` cùng thư mục; sửa file rồi nhờ Claude đăng lại, link giữ nguyên)

Gồm: 3 bước Pretraining → SFT → RLHF, chọn Prompt / RAG / Fine-tune, liên hệ Buổi 5–6.

Thuật ngữ viết tắt:

| Viết tắt | Tên đầy đủ | Nghĩa | Ý chính |
|---|---|---|---|
| **SFT** | Supervised Fine-Tuning | Tinh chỉnh có giám sát | **Người viết** câu trả lời mẫu, model bắt chước |
| **RLHF** | Reinforcement Learning from Human Feedback | Học tăng cường từ phản hồi của con người | **Model viết** vài câu trả lời, **người chọn** câu tốt hơn → huấn luyện reward model ("máy chấm điểm") |

- Supervised = có đáp án mẫu; Fine-Tuning = train thêm trên model có sẵn, không train lại từ đầu.
- Reinforcement Learning = học bằng cách thử, nhận điểm thưởng rồi điều chỉnh.
Mục "Bản của mình" ở A vẫn tự viết lại bằng lời của mình, viết từ trí nhớ.

## A. Karpathy — Intro to Large Language Models

Chọn 1 trong 2 cách:

- [ ] Xem: "[1hr Talk] Intro to Large Language Models" — https://www.youtube.com/watch?v=zjkBMFhNj_g
- [ ] Hoặc đọc (~30–40ph, lướt phần công thức toán):
  - Chip Huyen, "RLHF: Reinforcement Learning from Human Feedback" — https://huyenchip.com/2023/05/02/rlhf.html
    (bố cục đúng 3 phase: Pretraining → SFT → RLHF)
  - (thêm) Hugging Face, "Illustrating RLHF" — https://huggingface.co/blog/rlhf (sâu phần reward model, xếp hạng)
  - Đọc thay video thì thiếu 2 ý: LLM "là" gì về mặt file, và rủi ro bảo mật (jailbreak, prompt injection).
    Xem riêng đoạn cuối video về LLM security, hoặc ghi nợ tới Buổi 7.

Luật chơi giống Buổi 2: xem xong mới viết, viết bằng lời của mình, không chép câu chữ từ video.

**Câu hỏi dẫn đường** (để trong đầu trước khi bấm play):

- Một LLM "là" gì về mặt file trên máy? Chạy nó cần những gì?
- **Pretraining** học từ dữ liệu gì, ra được cái gì? Vì sao model sau pretraining chưa dùng làm trợ lý được?
- **SFT** (supervised fine-tuning) thêm vào cái gì? Dữ liệu trông ra sao?
- **RLHF** khác SFT ở chỗ nào? Vì sao "so sánh 2 câu trả lời" dễ hơn "tự viết câu trả lời mẫu"?
- Hallucination nối với pretraining thế nào? (Liên hệ Buổi 2: model đoán token tiếp theo.)
- Các rủi ro bảo mật được nhắc (jailbreak, prompt injection...): cái nào liên quan tới app mình sẽ build?

**Bỏ qua được:** số GPU, chi phí training cụ thể, tên các model đời cũ.

### Bản của mình (viết sau khi xem, 5–10 dòng)

- Pretraining:
- SFT:
- RLHF:
- Vì sao cần cả 3 bước:

## B. Khi nào fine-tune, khi nào RAG, khi nào chỉ cần prompt

Đọc nhanh (~30ph), chỉ cần mức "biết chọn", không cần biết cách train.
Nguồn gợi ý: docs fine-tuning của OpenAI, bài giới thiệu LoRA bất kỳ. Ghi nguồn đã đọc vào đây.

- [ ] Đã đọc: ...

**Câu hỏi để tự trả lời:**

- LoRA là gì, nói 1–2 câu? Vì sao nó rẻ hơn fine-tune toàn bộ model?
- Fine-tune dạy model được gì: kiến thức mới, hay cách trả lời (format, giọng văn)?
- Dữ liệu thay đổi hằng ngày (giá, tồn kho) thì fine-tune hay RAG? Vì sao?

Điền bảng:

| Tình huống                                               | Prompt | RAG | Fine-tune | Chọn gì, vì sao |
| -------------------------------------------------------- | ------ | --- | --------- | --------------- |
| Bot trả lời theo tài liệu nội bộ công ty (đổi hằng tuần) |        |     |           |                 |
| Luôn trả JSON đúng 1 format cố định                      |        |     |           |                 |
| Viết đúng giọng văn thương hiệu, hàng nghìn ví dụ mẫu    |        |     |           |                 |
| Trích đơn hàng từ tin nhắn (Buổi 5)                      |        |     |           |                 |

## Bài 1 — Vòng lặp chat có lịch sử

-

## Bài 2 — System prompt + lệnh

_(Claude viết, 2026-10-05, chạy thật với `gpt-6-luna`)_

`instructions` vs message role `"system"` trong lịch sử:

- Docstring SDK: `instructions` là "a system (or developer) message inserted into the model's context". Bản chất vẫn là system message, chỉ khác chỗ mình để nó.
- `instructions` nằm **ngoài** list `history`, mỗi lần gọi API gửi kèm riêng:
  - `/reset` xóa `history` mà system prompt vẫn còn, không phải thêm lại.
  - `/history` không hiện system prompt.
  - Đổi prompt chỉ là gán lại 1 biến, không phải tìm và sửa message trong list.
  - Bài 4 (sliding window) cắt lịch sử không bao giờ đụng vào system prompt.
- Để role `"system"` trong `history` thì nó là 1 phần tử của list:
  - `/reset` phải nhớ thêm lại, sliding window phải nhớ chừa nó ra.
  - Đổi giữa chừng thì phải thay `history[0]`, hoặc thêm system message mới vào giữa (lúc đó context có 2 system message mâu thuẫn).
- Dù để ở đâu thì system prompt vẫn được gửi lên **mỗi lượt**, nên vẫn tốn input token mỗi lượt (suy ra từ docstring, chưa đo; kiểm chứng ở Bài 3 bằng `usage.input_tokens`).

Đổi `/system` giữa chừng thì sao:

- Kịch bản: 2 lượt prompt mặc định (giới thiệu Hà Nội, kể món ăn) → `/system Trả lời như cướp biển` → 2 lượt nữa.
- Giọng văn đổi **ngay lượt đầu tiên** sau lệnh: "Bạn tên An đó, thuyền trưởng ạ! 🏴‍☠️", "Thuyền trưởng An hãy dạo quanh Hồ Gươm...".
- Vẫn nhớ tên An và vẫn hiểu "ở đó" là Hà Nội, vì `history` không bị đụng tới.
- Các lượt cũ **không bị viết lại**: câu trả lời cũ trong `history` vẫn giọng bình thường. Prompt mới chỉ áp cho những lần gọi API từ đó về sau, nhưng mỗi lần gọi model đọc lại toàn bộ lượt cũ dưới prompt mới.
- Giọng cướp biển khá nhẹ (gọi "thuyền trưởng", thêm emoji). Giả thuyết, chưa kiểm: prompt quá ngắn + các câu trả lời cũ giọng bình thường trong lịch sử kéo model về giọng cũ. Thử: viết prompt chi tiết hơn, hoặc `/reset` rồi mới hỏi, xem giọng có đậm hơn không.

## Bài 3 — Token / cost tracker

_(Claude viết, 2026-10-05, chạy thật `bai3_run` với `gpt-6-luna`, giá $0.10 / $0.50 mỗi 1M token,
context window 1,050,000 — tra developers.openai.com/api/docs/models/gpt-6-luna cùng ngày)_

Kịch bản 6 câu ngắn, cùng 1 chủ đề: "Tên mình là An, mình học Python" → hỏi thư viện gọi API → ví dụ
→ thư viện async → so sánh → "Mình tên gì và đang học gì?" (bot vẫn nhớ đúng).

| Lượt | Input token | Output token | Cost lượt | Tổng cost |
| ---- | ----------- | ------------ | --------- | --------- |
| 1    | 35          | 45           | $0.000026 | $0.000026 |
| 2    | 70          | 103          | $0.000058 | $0.000084 |
| 3    | 145         | 44           | $0.000036 | $0.000121 |
| 4    | 180         | 90           | $0.000063 | $0.000184 |
| 5    | 254         | 37           | $0.000044 | $0.000228 |
| 6    | 306         | 12           | $0.000037 | $0.000264 |

`/stats`: 6 lượt, tổng input 990, tổng output 331, tổng cost $0.000264.

Input token tăng thế nào, vì sao:

- Tăng **mỗi lượt**, không bao giờ giảm: 35 → 70 → 145 → 180 → 254 → 306 (lượt 6 gấp ~9 lần lượt 1).
- Vì API không nhớ gì, mỗi lượt mình gửi lại **toàn bộ** `history` + câu mới. Lượt n tăng thêm so với
  lượt n-1 đúng bằng: câu trả lời lượt trước + câu hỏi mới (+ vài token khung message).
  Mỗi lượt tăng thêm 35–75 token, trung bình ~54.
- Phần tăng **không bằng** output token lượt trước (lượt 1 out 45 nhưng lượt 2 chỉ tăng 35), vì
  `gpt-6-luna` có **reasoning token**: gọi thử 1 lần thấy `output_tokens=59`, trong đó
  `reasoning_tokens=38`, chữ hiện ra chỉ ~15 token (tiktoken). Reasoning token vẫn bị tính tiền output
  nhưng không nằm trong `history`, nên không bị gửi lại lượt sau.
- Cost từng lượt **không** tăng đều như input, vì output (đắt gấp 5 lần input) lên xuống theo độ dài câu
  trả lời: lượt 6 input lớn nhất nhưng cost chỉ $0.000037 do bot trả lời rất ngắn (12 token).

Lượt 20 so với lượt 1 (ngoại suy tuyến tính, ~54 token/lượt, output trung bình ~55):

- Input lượt 20 ≈ 35 + 19 × 54 ≈ **1,065 token**, gấp ~30 lần lượt 1.
- Cost lượt 20 ≈ **$0.000134**, gấp ~5 lần lượt 1. Gấp ít hơn input vì giai đoạn đầu tiền chủ yếu nằm ở
  output, càng về sau phần input mới chiếm ưu thế.

Ước tính 100 lượt / khi nào tràn context window:

- Input mỗi lượt tăng tuyến tính, nên **tổng** input của cả cuộc hội thoại tăng theo bình phương số lượt
  (1 + 2 + … + n ≈ n²/2).
- 100 lượt: tổng input ≈ 271,790 token, output ≈ 5,500 → **≈ $0.03**. Nếu không gửi lịch sử (mỗi lượt
  độc lập) thì chỉ ≈ $0.003, tức gửi lịch sử đắt gấp ~10 lần, và tỉ lệ này còn tăng theo số lượt.
- Context window 1,050,000 token: với câu ngắn như trên (~54 token/lượt) phải tới **~19,000 lượt** mới tràn.
  Nhưng nếu mỗi lượt thêm ~2,000 token (dán code, tài liệu) thì **~526 lượt** đã tràn, và gần lúc đó
  mỗi lượt tốn ~$0.10 chỉ riêng tiền input.
- Kết luận: với câu ngắn, vấn đề đến trước là **tiền** tăng dần, chứ không phải tràn context
  (độ trễ có thể cũng tăng theo input, chưa đo).
  Đó là lý do Bài 4 làm sliding window: chặn input mỗi lượt dưới 1 ngưỡng cố định.

## Bài 4 — Sliding window

Ngưỡng dùng khi test: `MAX_HISTORY_TOKENS = `

- tiktoken đếm vs `usage.input_tokens`: lệch bao nhiêu, vì sao:
- Bỏ theo cặp, vì sao:
- Sau khi lượt "Tên mình là An" bị cắt, bot có nhớ tên không:

## Bài 5 — Sliding window vs tóm tắt

| Chỉ số                          | Sliding window | Tóm tắt |
| ------------------------------- | -------------- | ------- |
| Tổng input token                |                |         |
| Tổng output token               |                |         |
| Tổng cost (gồm lời gọi tóm tắt) |                |         |
| Nhớ tên ở cuối?                 |                |         |
| Độ trễ cảm nhận                 |                |         |

Khi nào dùng cách nào:

-
