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

_(Claude viết, 2026-10-06, chạy thật `bai4_run` với `gpt-6-luna`)_

Ngưỡng dùng khi test: `MAX_HISTORY_TOKENS = 300`

Kịch bản: "Tên mình là An." → 4 câu "Giải thích list / dict / tuple / set trong 4-5 câu" → "Mình tên gì?".
"Lịch sử" = token tiktoken của `history` trước / sau khi cắt (chưa tính câu mới và system prompt).

| Lượt | Lịch sử trước → sau | Bỏ   | Input (API) | tiktoken | Lệch |
| ---- | ------------------- | ---- | ----------- | -------- | ---- |
| 1    | 0 → 0               | 0    | 31          | 21       | 10   |
| 2    | 18 → 18             | 0    | 67          | 47       | 20   |
| 3    | 145 → 145           | 0    | 204         | 174      | 30   |
| 4    | 293 → 293           | 0    | 362         | 322      | 40   |
| 5    | 420 → 275           | 2    | 334         | 304      | 30   |
| 6    | 402 → 254           | 1    | 305         | 275      | 30   |

- Input **ngừng tăng**: lên tới 362 ở lượt 4 rồi dao động quanh ~300–330, thay vì tăng mãi như Bài 3.
- Ngưỡng chỉ chặn **phần lịch sử**, nên input thật có lúc vẫn > 300 (lượt 4: lịch sử 293 + câu mới
  + system prompt 16 token + phần khung = 362).
- Lượt 5 bỏ liền 2 cặp ("Tên mình là An" + "list") vì bỏ 1 cặp vẫn còn > 300.

tiktoken đếm vs `usage.input_tokens`: lệch bao nhiêu, vì sao:

- Lệch 10 → 40 token, và khớp **đúng** công thức `lệch = 10 + 5 × số message cũ` ở cả 6 lượt.
  Lượt 5–6 sau khi cắt còn 4 message cũ nên lệch quay về 30.
- Suy ra (chưa có tài liệu xác nhận): mỗi message tốn thêm ~5 token "khung" (đánh dấu role, ranh giới
  message) mà tiktoken không thấy vì mình chỉ đếm phần `content`. ~10 token cố định còn lại là khung của
  câu hỏi mới + phần `instructions`.
- Phần chữ thì tiktoken `o200k_base` có vẻ đếm khớp (lệch tròn theo số message, không lệch lung tung),
  dù tiktoken không biết `gpt-6-luna` (`encoding_for_model` báo KeyError).
- Hệ quả: muốn ước lượng sát API thì cộng thêm ~5 token mỗi message. Lệch nhỏ (~10% ở đây), đủ dùng để
  quyết định cắt, không cần chính xác tuyệt đối.

Bỏ theo cặp, vì sao:

- Lịch sử phải xen kẽ user → assistant. Bỏ lẻ thì lịch sử bắt đầu bằng 1 câu trả lời không có câu hỏi,
  hoặc 2 câu user đứng liền nhau, model đọc mất mạch. (Chưa thử xem API có báo lỗi không.)
- Bỏ lẻ còn làm "quên nửa vời": nếu chỉ bỏ câu user "Tên mình là An." mà giữ câu bot
  "Chào An! Mình sẽ gọi bạn là An nhé." thì bot vẫn biết tên qua câu trả lời → không còn rõ đã cắt
  cái gì, khó dự đoán bot nhớ gì.
- Đếm "số lượt bị bỏ" mới có nghĩa khi bỏ trọn cặp.

Sau khi lượt "Tên mình là An" bị cắt, bot có nhớ tên không:

- **Không.** Cặp "Tên mình là An" bị bỏ ở lượt 5 (`/history` lúc đó bắt đầu từ "dict"). Lượt 6 hỏi
  "Mình tên gì?" → "Mình chưa biết tên bạn — bạn chưa cho mình biết."
- Đáng chú ý: bot **không biết là nó đã quên**. Nó khẳng định "bạn chưa cho mình biết", trong khi thật ra
  có nói, chỉ là bị cắt. Sliding window xóa vĩnh viễn (`del history[:2]`), model không có dấu hiệu nào
  cho thấy từng có lượt cũ.
- Đây là điểm yếu Bài 5 xử lý: tóm tắt các lượt cũ thay vì bỏ hẳn, để giữ lại thông tin như tên.

## Bài 5 — Sliding window vs tóm tắt

_(Claude viết, 2026-10-06, chạy thật `bai5_run` với `gpt-6-luna`, `MAX_HISTORY_TOKENS = 300`,
`KEEP_LAST_PAIRS = 2`, cùng `SCRIPT` 10 câu: "Tên mình là An." → 8 câu "Giải thích … 4-5 câu" → "Mình tên gì?")_

| Chỉ số                          | Sliding window | Tóm tắt (prompt cũ)                 | Tóm tắt (prompt đã sửa) |
| ------------------------------- | -------------- | ----------------------------------- | ----------------------- |
| Tổng input token                | 2,292          | 5,137 (chat 3,207 + tóm tắt 1,930)  | 4,849                   |
| Tổng output token               | 919            | 2,152 (chat 1,114 + tóm tắt 1,038)  | 2,341                   |
| Tổng cost (gồm lời gọi tóm tắt) | $0.000689      | $0.001590 (x2.3; tóm tắt chiếm 45%) | $0.001655 (x2.4)        |
| Số lần gọi tóm tắt              | 0              | 6 (lượt 5 → 10, lượt nào cũng có)   | 6                       |
| Nhớ tên ở cuối?                 | Không          | **Không**                           | **Có**                  |
| Độ trễ (cả kịch bản)            | 23.3 s         | 40.4 s (x1.7)                       | 45.4 s (x1.9)           |

- Sliding window: "Mình chưa biết tên bạn vì bạn chưa cho mình biết." — giống Bài 4, bot không biết là mình đã quên.
- Tóm tắt, prompt cũ: "Mình chưa biết tên bạn." — **cũng quên**, dù đã tốn gấp 2.3 lần tiền.
- Tóm tắt, prompt đã sửa (thêm câu giữ thông tin từ bản tóm tắt trước): "Bạn tên An." — **nhớ đúng**.
  Cả 6 bản tóm tắt đều mở đầu "Người dùng tên An; chưa nêu sở thích hay mục tiêu cá nhân. …".
  Cost gần như không đổi so với prompt cũ (chỉ cột "Tóm tắt (prompt đã sửa)" là chạy lại riêng
  kịch bản tóm tắt; sliding window không chạy lại).

Vì sao cách tóm tắt cũng quên tên (tóm tắt cuốn chiếu làm rơi thông tin):

- Tóm tắt **lần 1** (lượt 5) vẫn có: "Người dùng tên An. Cuộc hội thoại gồm lời chào và phần giải thích về `list`…"
- Tóm tắt **lần 2** (lượt 6) mất tên: "Cuộc hội thoại đề cập đến `list` và `dict`…", và từ đó không bản nào có lại.
- Lần 2, tên chỉ còn nằm trong **bản tóm tắt cũ** (message role `assistant`), không còn câu user nào nói tên.
  Prompt dặn giữ "thông tin **người dùng nói** về bản thân" → model không coi đó là điều cần giữ.
- Kiểm chứng: gọi lại đúng tình huống lần 2, mỗi prompt 3 lần:
  - Prompt hiện tại: **0/3** giữ tên. Cả 3 bản chỉ tóm tắt lượt "dict", bỏ qua luôn bản tóm tắt cũ.
  - Thêm 1 câu "Nếu đầu vào có bản tóm tắt trước, phải chép lại nguyên văn mọi thông tin về người dùng
    trong đó.": **3/3** giữ tên ("Người dùng tên An. …").
- Bài học: mỗi lần tóm tắt là 1 lần có thể **rơi thông tin**, và tóm tắt cuốn chiếu nhân rủi ro đó lên
  qua từng lần. Prompt tóm tắt phải dặn rõ giữ cả thông tin từ bản tóm tắt trước.
- Đã sửa `SUMMARY_PROMPT` trong `exercises.py` (thêm câu trên) và chạy lại kịch bản tóm tắt: bot nhớ
  tên ở lượt 10 (xem cột "prompt đã sửa" ở bảng trên). Mới chạy 1 lần, chưa lặp lại nhiều lần.

Vì sao lượt nào cũng phải tóm tắt (từ lượt 5):

- Sau khi nén, lịch sử = bản tóm tắt (~100 token) + 2 lượt giữ nguyên. Mỗi câu trả lời "4-5 câu" dài
  ~120–150 token nên 2 lượt đã ~300 token → thêm 1 lượt là vượt ngưỡng, lại phải tóm tắt.
- Hệ quả: 6 lời gọi tóm tắt chiếm 45% cost và làm cả kịch bản chậm hơn ~17 giây.
- Ngưỡng phải lớn hơn hẳn phần giữ nguyên thì tóm tắt mới thưa. Ví dụ ngưỡng 2,000 (roadmap gợi ý)
  hoặc chỉ giữ 1 lượt.

Tóm tắt có tiết kiệm token không? (so thêm với "giữ nguyên toàn bộ lịch sử")

- Chạy thêm cùng `SCRIPT`, không cắt / không tóm tắt (như Bài 3): input 5,821, output 1,066,
  **$0.001115**, 30.4 s, nhớ tên ("Bạn tên là An.").
- Với 10 lượt, **tóm tắt đắt nhất** trong 3 cách: input có giảm so với giữ nguyên (4,849 vs 5,821, −17%)
  nhưng output gấp đôi (2,341 vs 1,066) vì 6 lời gọi tóm tắt cũng sinh output, mà output đắt gấp 5 input.
- Ước tính theo số lượt (ngoại suy từ số đo trên, chưa chạy thật các mốc dài):

  | Số lượt | Giữ nguyên lịch sử | Tóm tắt  | Rẻ hơn     |
  | ------- | ------------------ | -------- | ---------- |
  | 10      | $0.0011            | $0.0017  | giữ nguyên |
  | 20      | $0.0035            | $0.0039  | giữ nguyên |
  | 25      | $0.0051            | $0.0050  | hòa vốn    |
  | 50      | $0.0178            | $0.0107  | tóm tắt    |
  | 100     | $0.0663            | $0.0220  | tóm tắt    |

- Vì sao: giữ nguyên thì mỗi lượt gửi lại thêm ~122 token → cost mỗi lượt tăng dần (lượt 1 ~56 µ$, lượt 30
  ~412 µ$), tổng tăng theo bình phương. Tóm tắt thì từ lượt 5 mỗi lượt ~226 µ$, gần như cố định.
- Kết luận: tóm tắt **không** nhằm rẻ hơn ở hội thoại ngắn. Nó giữ chi phí mỗi lượt **không tăng theo độ
  dài** hội thoại và không bao giờ tràn context window → chỉ có lợi về tiền khi hội thoại đủ dài.
  Ngưỡng 300 khiến lượt nào cũng tóm tắt nên điểm hòa vốn đến muộn; ngưỡng 2,000 chưa đo.

Tóm tắt đặt ở đâu, role gì:

- Đặt ở **đầu** lịch sử (thay cho các lượt cũ), trước các lượt giữ nguyên → thứ tự thời gian vẫn đúng.
- Đang dùng role `assistant`, nội dung mở đầu "Tóm tắt các lượt trước: …": giữ được xen kẽ
  assistant → user → assistant. Role `system`/`developer` cũng được (SDK cho phép) nhưng sẽ nâng nội dung
  người dùng nói lên cấp "chỉ thị" → dễ bị prompt injection. Cách khác: nối bản tóm tắt vào `instructions`.
- Chưa thử so sánh các role với nhau.

Khi nào dùng cách nào:

- **Sliding window**: rẻ nhất, nhanh nhất, không gọi thêm LLM. Hợp với chat mà mỗi câu hỏi gần như độc
  lập (hỏi đáp tra cứu, FAQ), hoặc khi thông tin quan trọng không nằm ở đầu cuộc trò chuyện.
- **Tóm tắt**: tốn thêm (ở đây x2.3 cost, x1.7 thời gian) để đổi lấy khả năng giữ thông tin cũ (tên, sở
  thích, quyết định đã chốt). Chỉ đáng khi cuộc trò chuyện dài và thông tin đầu vẫn cần dùng về sau, và
  phải có prompt tóm tắt tốt + ngưỡng đủ lớn để không tóm tắt mỗi lượt.
- Thông tin **chắc chắn phải nhớ** (như tên) thì đừng phó mặc cho tóm tắt: tách riêng ra (ví dụ lưu
  vào 1 biến/`instructions` như "Người dùng tên An") để không bao giờ bị cắt hay tóm tắt rơi mất.
