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

`instructions` vs message role `"system"` trong lịch sử:

-

Đổi `/system` giữa chừng thì sao:

-

## Bài 3 — Token / cost tracker

| Lượt | Input token | Output token | Cost lượt | Tổng cost |
| ---- | ----------- | ------------ | --------- | --------- |
| 1    |             |              |           |           |
| 2    |             |              |           |           |
| 3    |             |              |           |           |
| 4    |             |              |           |           |
| 5    |             |              |           |           |
| 6    |             |              |           |           |

Input token tăng thế nào, vì sao:

-

Ước tính 100 lượt / khi nào tràn context window:

-

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
