# Cập nhật roadmap — Production RAG + Evals

> Soạn ngày 28/09/2026. Bổ sung các kỹ năng "prod gặp ngay, phỏng vấn hay hỏi" mà roadmap hiện chưa có.
> Nguyên tắc: gộp vào buổi có sẵn, không tạo buổi mới, không đổi lịch 12 tuần. Mỗi tuần thêm tối đa ~1–2h, lấy từ buffer Chủ nhật.

## 1. Tổng quan — thêm gì, vì sao

| # | Chủ đề | Vấn đề thực tế | Làm ngay hay để sau |
|---|---|---|---|
| 1 | Phân quyền tài liệu (permission-aware RAG) | Nhân viên sales hỏi bot → bot trả lời lương của HR | Ngay (bản tối thiểu) |
| 2 | Dữ liệu cá nhân (PII) | CCCD/SĐT/lương bị gửi sang LLM provider và nằm nguyên văn trong log Langfuse | Ngay |
| 3 | Vòng đời tài liệu | Tài liệu sửa/xoá nhưng bot vẫn trả lời theo bản cũ, vẫn trích tài liệu đã xoá | Ngay |
| 4 | Hỏi nối tiếp (multi-turn) | "Thế còn trường hợp kia?" → retrieval trượt vì câu hỏi thiếu ngữ cảnh | Ngay |
| 5 | Full-text tiếng Việt | Postgres không có text search config tiếng Việt → hybrid search có thể không cải thiện | Ngay (chỉ 1 lưu ý) |
| 6 | Feedback 👍/👎 → evals | Có user thật nhưng không biết câu nào bot trả lời tệ | Ngay |
| 7 | Agent evals | Roadmap đo kỹ RAG nhưng agent thì 0 eval → sửa agent không biết tốt lên hay tệ đi | Ngay (~2.5h) |
| 8 | Kiểm tra độ tin cậy RAGAS | Điểm RAGAS do LLM chấm, có thể lệch (nhất là tiếng Việt) → cả bảng "0.62 → 0.85" chưa chắc đáng tin | Ngay (~1h) |
| 9 | Nâng cao (sync quyền từ Drive/SharePoint, RLS/ABAC, đổi embedding model, OCR, text-to-SQL…) | Phụ thuộc hệ thống thật của công ty | Để sau lộ trình |

Vì sao làm ngay: (a) câu E.1 trong bộ 20 câu ("thiết kế chatbot nội bộ… → security") cần đến; (b) chi phí thấp, dùng lại kỹ thuật đã học (metadata filter); (c) phân quyền + vòng đời tài liệu thêm sau thì phải ingest lại toàn bộ.

## 2. Lịch chèn (theo tuần)

| Tuần | Trang | Buổi | Nội dung | Thêm thời gian |
|---|---|---|---|---|
| T3 | Phase 02 | Buổi 3 | Metadata thêm `doc_id`, `content_hash`, `allowed_groups` | ~15ph |
| T3 | Phase 02 | Buổi 6 | Chấm tay 20 câu, so với RAGAS | ~1h (buổi 4h) |
| T4 | Phase 02 | Buổi 8 | Filter theo quyền + 5 câu test rò rỉ | +1h |
| T4 | Phase 02 | Buổi 9 | 📌 Lưu ý full-text tiếng Việt | ~0 |
| T5 | Phase 02 | Buổi 13–15 | Multi-turn + cập nhật/xoá tài liệu | ~2h trong 6h project |
| T5 | Phase 02 | Exit criteria | Leak rate = 0 | — |
| T6 | Phase 03 | Buổi 6 (+ Buổi 4) | Bộ 10–15 task agent evals; dùng số cho so sánh RAG vs agent ở Buổi 4 | ~2h (buổi 4h; tràn thì dùng Buổi 12 Buffer) |
| T8 | Phase 04 | Buổi 3 | Ingest có doc_id + hash (+ nhãn quyền nếu dữ liệu cần) | ~15ph |
| T9 | Phase 04 | Buổi 9 | Che PII trong trace Langfuse | ~30ph |
| T9 | Phase 04 | Buổi 11 | CI chạy cả agent evals | ~30ph |
| T9 | Phase 04 | Buổi 12 | Che PII trước khi gửi sang LLM | ~1h |
| T10 | Phase 04 | Buổi 14–15 | Test rò rỉ quyền; auth + role | trong buổi |
| T10 | Phase 04 | Buổi 17 | Nút 👍/👎 → Langfuse score | ~30ph |
| T11 | Phase 04 | Buổi 19–20 | Trace 👎 → eval case mới | ~30ph |
| — | Bộ 20 câu | B.5, D.3 | Thêm ý kiểm tra RAGAS và agent evals | — |
| — | Bộ 20 câu | E.1 | Viết rõ phần "security" | — |
| — | Trang chính | Sau lộ trình | Bullet "Production RAG nâng cao" | — |

Ghi chú: PII đặt ở tuần 9 (Buổi 12, buổi 4h "chạy thử, fix") thay vì Buổi 13 để giảm tải tuần 10 — tuần bắt đầu apply.
Không thêm gì vào 2 bài Rebuild test (giữ nguyên để đo năng lực nền).

## 3. Checklist áp dụng lên Notion

- [ ] Phase 02 — Buổi 3
- [ ] Phase 02 — Buổi 6
- [ ] Phase 02 — Buổi 8
- [ ] Phase 02 — Buổi 9
- [ ] Phase 02 — Buổi 13–15
- [ ] Phase 02 — Exit criteria
- [ ] Phase 03 — Buổi 4 + Buổi 6
- [ ] Phase 03 — Exit criteria
- [ ] Phase 04 — Buổi 3
- [ ] Phase 04 — Buổi 9
- [ ] Phase 04 — Buổi 11
- [ ] Phase 04 — Buổi 12
- [ ] Phase 04 — Buổi 14
- [ ] Phase 04 — Buổi 15
- [ ] Phase 04 — Buổi 17
- [ ] Phase 04 — Buổi 19–20
- [ ] Bộ 20 câu — B.5, D.3
- [ ] Bộ 20 câu — E.1
- [ ] Trang chính — Sau lộ trình

## 4. Nội dung chi tiết để dán

"SỬA" = xoá dòng cũ rồi dán dòng mới. "THÊM" = dán vào cuối buổi đó.

### Phase 02 — RAG + Evals

**Buổi 3 (T3) — Ingestion Pipeline** · SỬA dòng
`Embed + lưu kèm metadata (nguồn, trang, mục)` thành:

- [ ] Embed + lưu kèm metadata (nguồn, trang, mục, doc_id, content_hash, allowed_groups) — allowed_groups gán theo quyền tài liệu gốc (dữ liệu public thì tự chia 2 nhóm giả: public / internal), không để LLM tự đoán

**Buổi 6 (T3, 4h) — Đo Baseline** · THÊM

- [ ] Kiểm tra độ tin cậy của RAGAS (~1h): tự chấm tay 20 câu trả lời (bám nguồn: có/không), so với điểm faithfulness của RAGAS → ghi tỉ lệ khớp (vd. 17/20) vào eval-results.md. Lệch nhiều → xem lại judge model / prompt chấm trước khi tin bảng số

📌 Điểm RAGAS do LLM chấm (LLM-as-judge) — chưa kiểm tra thì chưa chắc con số phản ánh đúng chất lượng

**Buổi 8 (T4) — Query rewriting + Metadata filtering** · THÊM

- [ ] Permission-aware retrieval (+1h, dùng buffer CN): luôn thêm điều kiện allowed_groups && user.groups vào câu query vector — filter TRƯỚC khi đưa vào LLM, không nhờ prompt "đừng trả lời"
- [ ] Thêm 5 câu test rò rỉ vào eval set: user nhóm public hỏi nội dung internal → retrieval phải trả 0 chunk internal. Ghi "leak rate = 0/5" vào eval-results.md

📌 Filter theo độ liên quan (tối ưu chất lượng) ≠ filter theo quyền (bảo mật, sai 1 lần là lộ)

**Buổi 9 (T4) — Hybrid Search** · THÊM

📌 Postgres không có text search config tiếng Việt → dùng config 'simple' (tách theo âm tiết) hoặc tách từ trước bằng underthesea/pyvi. Đo cả 2 cách, ghi số vào eval-results.md (kiểm chứng khi làm)

**Buổi 13–15 (T5) — Project #2** · THÊM

- [ ] Hỏi nối tiếp (multi-turn): viết lại câu hỏi dựa trên lịch sử hội thoại trước khi retrieve ("thế còn trường hợp kia?" → câu hỏi đầy đủ). Thêm 3–5 câu hỏi nối tiếp vào eval set
- [ ] Vòng đời tài liệu: upload lại cùng doc_id → so content_hash, chỉ re-embed khi đổi; xoá tài liệu → xoá hết chunks của nó. Trên trang admin: nút cập nhật/xoá tài liệu. Test: hỏi nội dung tài liệu đã xoá → phải "không tìm thấy"

**Exit criteria (cổng qua Phase 03)** · THÊM

- [ ] Leak rate = 0 trong eval set (câu test rò rỉ quyền)

### Phase 03 — Agents + MCP

**Buổi 4 (T6) — Agent + RAG** · THÊM

📌 Sau khi có bộ agent evals (Buổi 6): chạy lại phép so sánh "RAG thẳng vs agent-with-RAG" bằng số thật (chất lượng + cost)

**Buổi 6 (T6, 4h) — Tổng ôn** · THÊM

- [ ] Agent evals (~2h; tràn thì dùng Buổi 12 Buffer): soạn 10–15 task, mỗi task ghi kết quả mong đợi + tool phải gọi. Viết script chạy agent qua bộ task, đo: tỉ lệ hoàn thành, tỉ lệ gọi đúng tool/tham số (so khớp chính xác, không cần LLM chấm), số bước + cost trung bình mỗi task. Ghi bảng vào eval-results.md

**Exit criteria (cổng qua Phase 04)** · THÊM

- [ ] Có bảng agent evals (tỉ lệ hoàn thành, gọi đúng tool, bước/cost mỗi task), giải thích được case fail

### Phase 04 — Capstone

**Buổi 3 (T8)** · THÊM

- [ ] Ingest có doc_id + content_hash (upsert/xoá như Project #2). Nếu dữ liệu có nhiều mức quyền: gắn allowed_groups cho từng tài liệu

**Buổi 9 (T9) — Langfuse** · THÊM

- [ ] Che PII (CCCD, SĐT, email, lương…) trước khi ghi vào trace — log không được chứa dữ liệu nhạy cảm nguyên văn

**Buổi 11 (T9) — Evals vào CI** · THÊM

- [ ] CI chạy cả agent evals (dùng lại script Phase 03): PR đổi prompt/tool/graph của agent → chạy bộ task, tỉ lệ hoàn thành tụt thì fail

**Buổi 12 (T9, 4h)** · THÊM

- [ ] PII guard đầu vào LLM (1h): phát hiện + che PII trước khi gửi sang LLM provider; ghi rõ trong README dữ liệu nào đi ra ngoài (tham khảo Nghị định 13/2023 về bảo vệ dữ liệu cá nhân)

**Buổi 14 (T10) — Test bảo mật thủ công** · THÊM

- [ ] (Nếu có phân quyền) Test rò rỉ: user role A hỏi dữ liệu role B, thử cả kèm prompt injection

**Buổi 15 (T10)** · SỬA dòng
`Buổi 15 (2h): Auth đơn giản + rate limiting (nếu public), error handling tử tế.` thành:

- [ ] Buổi 15 (2h): Auth + role (nối role của user vào bước retrieval nếu có phân quyền), rate limiting (nếu public), error handling tử tế. Nếu dư thời gian: Postgres Row-Level Security.

**Buổi 17 (T10) — Onboard user đầu tiên** · THÊM

- [ ] Nút 👍/👎 trên mỗi câu trả lời, gửi thành score vào Langfuse gắn với trace

**Buổi 19–20 (T11)** · THÊM

- [ ] Lọc trace 👎 → chọn 5–10 case đưa vào eval set (eval set lớn dần theo usage thật)

### Bộ 20 câu hỏi phỏng vấn cốt lõi

**Mục B, câu 5 (Đánh giá RAG bằng gì)** · THÊM vào cuối câu trả lời:

Kiểm tra lại chính judge: đã chấm tay 20 câu, so với RAGAS khớp X/20 — nên tin được bảng số.

**Mục D, câu 3 (Deploy prompt/model mới…)** · THÊM vào cuối câu trả lời:

Với agent: bộ 10–15 task chạy trong CI, đo tỉ lệ hoàn thành + gọi đúng tool + cost mỗi task.

**Mục E, câu 1** · SỬA phần `→ security` ở cuối câu trả lời thành:

→ security: (1) phân quyền theo tài liệu — gắn allowed_groups lúc ingest, filter theo quyền user lúc retrieve TRƯỚC khi vào LLM, không dựa vào prompt; (2) PII — che trước khi gửi LLM và trước khi ghi log/trace; (3) cẩn thận cache, tool của agent chạy bằng quyền admin; (4) leak test nằm trong eval set. Thêm vận hành: tài liệu cập nhật/xoá thì index đồng bộ thế nào (doc_id + hash).

### Trang chính — "Sau lộ trình — khi nào học ML/DL/build LLM"

THÊM bullet (trước dòng "Không có trigger → không học phòng hờ"):

- Production RAG nâng cao (khi làm hệ thống thật cần): đồng bộ quyền từ Drive/SharePoint/Confluence, RLS đầy đủ/ABAC, audit log; đổi/version embedding model (re-embed toàn bộ); prompt versioning (Langfuse prompt management); OCR + bảng biểu trong PDF scan; text-to-SQL; semantic cache; multi-provider fallback.
