# Cải tiến RAG tra cứu Bộ luật Lao động — cái gì đáng, cái gì không

_Phase 02 Buổi 12 (repo: session 24), 2026-11-16. Số liệu: `eval/eval-results.md` + `runs/*.jsonl`. Bản nháp Claude
viết theo yêu cầu, user duyệt._

## Bối cảnh

Bot hỏi–đáp **Bộ luật Lao động** (văn bản hợp nhất 18/VBHN-VPQH), trả lời kèm trích dẫn, phải **từ chối** khi tài
liệu không có câu trả lời và **không được lộ** tài liệu nội bộ. Đo trên bộ eval tự viết: 25–27 câu **có đáp án**
(single + multi), 5 câu **không có trong tài liệu**, 5 câu **thử rò rỉ** (+2 câu injection ở cuối). Chấm chủ yếu
**bằng code**, không dùng LLM: _từ chối nhầm_ (câu có đáp án mà bot nói "không tìm thấy"), _từ chối đúng_,
`fact_recall` (tỷ lệ dữ kiện bắt buộc có trong 5 đoạn đưa cho LLM), leak, trích dẫn đúng chỗ.
Mỗi bước **chỉ đổi 1 thứ** rồi đo lại.

## Bảng trước/sau

| Bước | Từ chối nhầm | `fact_recall` | Trả lời sai | Chi phí / độ trễ | Vì sao nhảy số |
| --- | --- | --- | --- | --- | --- |
| **Naive** (fixed 500 token, vector, k=5) | 9/25 (36%) | 0.69 | ≥ 1 (q13) | $0.0068 · 3.55 s | — |
| **+ Chunk theo Điều/Khoản** (≤ 300 token) | **4/25** | **0.87** | **0** | **$0.0044** · 3.07 s | Chunk cố định cắt rời tiêu đề "Điều N" khỏi thân → mảnh đúng không giống câu hỏi. Theo cấu trúc luật + lặp tiêu đề ở mọi mảnh → q03, q09, q16, q17, q22 sửa; q13 hết sai; hỏng q23 (câu nhiều Điều) |
| **+ Hybrid** (vector + từ khoá tách từ, RRF) | 4/27 → **3/27** | 0.88 → 0.89 | 0 | 3.18 s | Từ khoá "nghỉ việc" kéo đúng Điều 35–36 (q05), sửa q23; nhưng làm hỏng q02 |
| **+ Rerank** cross-encoder `mmarco` (top-20 → 5) | **1/27** | **0.95** | 0 | 3.58 s (**+13%**) | Lấy rộng 20 rồi chấm lại từng cặp câu hỏi–đoạn → sửa q02; q25 hết bị từ chối (nhưng thiếu 1/3 dữ kiện, câu trả lời bị cắt) |
| **+ Citation Khoản + guard + delimiter** (cuối) | 1/27 (**thật 2/27**) | 0.95 | 0 | 3.38 s | Trích tới Khoản đúng **55/55**; guard chặn **10/39** câu trước LLM, **0 chặn nhầm**; injection 0/2 |
| _(Rewrite câu hỏi — thử, **không giữ**)_ | _1/25_ | _0.96_ | _0_ | _+66% $, ×2 độ trễ_ | _Sửa câu không dấu/diễn đạt lạ, nhưng kết quả **dao động**: lần 1 hỏng q24, lần 2 hỏng q17_ |

Suốt chuỗi: **từ chối đúng 5/5** và **leak 0/5** giữ nguyên — không đánh đổi an toàn lấy điểm.

## Đáng nhất: chunking

Bước nhảy lớn nhất (**−5 câu từ chối nhầm**, `fact_recall` +0.18) và lại **rẻ hơn** (−35% tiền bot, ít token vào
hơn). Chỉ đổi cách **nạp dữ liệu**, không tốn thêm gì mỗi câu hỏi. Bài học: baseline hỏng **36%** gần như toàn bộ do
**retrieve**, không phải do LLM — sửa dữ liệu đầu vào trước khi đụng tới model. Đứng thứ hai là **rerank**: thêm 2
câu đúng, `fact_recall` lên 0.95, đổi lại **+13% độ trễ** với model nhỏ (`bge` lớn hơn cho kết quả tương tự nhưng
+86%).

## Không như kỳ vọng

- **Hybrid chỉ +1 câu.** Từ khoá mạnh nhất với mã số, thuật ngữ hiếm; bộ eval chủ yếu câu đời thường, và chunk
  theo Điều đã có tiêu đề rõ nên vector đã tìm tốt. Lợi ích thật có thể lớn hơn với câu hỏi kiểu "Điều 113" hay mã
  văn bản — bộ eval chưa đo được.
- **Rewrite hiệu quả nhưng không ổn định.** Cùng cấu hình, 2 lần chạy hỏng 2 câu khác nhau; tiền ×1.66, độ trễ ×2.
  Không giữ — rerank cho kết quả tương đương mà ổn định và rẻ hơn.
- **Test injection quá yếu.** Không có lớp phòng thủ nào, bot vẫn không bị lừa (0/6). Vì vậy **chưa đo được** delimiter
  có giúp gì. Giữ delimiter vì không tốn thêm, nhưng 0/2 không có nghĩa là an toàn.

## Lỗi còn lại

- **q20 — câu không dấu** ("thu viec toi da bao lau?"): không có đoạn đúng trong top-20 → guard chặn. Cần chuẩn hoá
  dấu hoặc rewrite **có điều kiện**.
- **q25 — câu nhiều Điều**: chạm giới hạn 600 token ra, trả lời **rỗng** (3/4 lần Buổi 23); bộ chấm còn đếm câu rỗng
  là "có trả lời" → con số 1/27 đẹp hơn thật.
- **Trích dẫn**: chỉ kiểm Khoản **có trong** đoạn được trích, chưa kiểm ý nằm đúng dòng Khoản đó.

## Hạn chế của phép đo

- Các dòng đo trên bộ câu **khác cỡ** (30 → 37 → 39) và prompt đổi ở bước cuối → đọc **xu hướng**, đừng đọc % chính xác.
- 37 câu là ít; ngưỡng guard chọn trên chính bộ test (dễ overfit).
- Không có cột faithfulness/relevancy cho các bước sau baseline: ở baseline, giám khảo LLM cho faithfulness **0.96**
  kể cả câu **sai mà tự tin** (q13) → số đo bằng code đáng tin hơn cho dữ liệu này.

## Nếu chỉ giữ 1 cải tiến

**Chunk theo cấu trúc văn bản.** Nhiều điểm nhất, rẻ đi chứ không đắt lên, và là nền để mọi bước sau có tác dụng.
