# Buổi 20 — Phase 02 Buổi 8: Query rewriting + Metadata filtering + Phân quyền (2h + 1h buffer)

Phase 02 — RAG + Evals, Tuần 4 "Cải tiến có đo lường". Nguồn: Notion "Phase 02 — RAG + Evals", page version 46 (Claude
đọc 2026-11-12).

Checklist Notion Buổi 8:

- LLM **rewrite câu hỏi** trước khi search (**multi-query / HyDE — chọn 1**)
- **Filter theo metadata** khi câu hỏi có phạm vi rõ → đo lại
- **Permission-aware retrieval** (+1h, dùng buffer CN): luôn thêm điều kiện `allowed_groups && user.groups` vào câu
  query vector — filter **TRƯỚC** khi đưa vào LLM, không nhờ prompt "đừng trả lời"
- Thêm **5 câu test rò rỉ** vào eval set: user nhóm `public` hỏi nội dung `internal` → retrieval phải trả **0 chunk
  internal**. Ghi "**leak rate = 0/5**" vào `eval-results.md`
- 📌 Filter theo độ liên quan (tối ưu chất lượng) ≠ filter theo quyền (bảo mật, sai 1 lần là lộ)

Nối với buổi trước — cấu hình hiện tại **dieu-300** (`law_chunks_dieu300`, Buổi 19): từ chối nhầm **4/25** (q05, q20,
q23, q25), sai **0**, từ chối đúng **5/5**, `fact_recall` **0.87**, bot $0.0044/30 câu. Lọc quyền hiện tại:
`WHERE %(group)s = ANY(allowed_groups)` (`projects/p2-labor-law-rag/rag.py:76`) — 1 user = 1 nhóm.

| Câu còn lỗi | Vì sao (Buổi 19) | Kỹ thuật hôm nay |
| --- | --- | --- |
| q05 | "nghỉ việc" bị hiểu là "nghỉ" (phép); luật viết "đơn phương chấm dứt hợp đồng" | Rewrite (đổi sang từ ngữ luật) |
| q20 | Gõ không dấu | Rewrite (thêm dấu) |
| q23, q25 | Cần 2–3 Điều, 1 vector chỉ kéo về 1 ý | Multi-query (tách câu hỏi) |

**Thứ tự hôm nay: bảo mật trước, chất lượng sau** — Bài 1–2 (quyền + leak test) làm trước để mọi thay đổi sau đều được
kiểm rò rỉ.

| Phần                                                        | Thời lượng | Làm ở đâu                 |
| ----------------------------------------------------------- | ---------- | ------------------------- |
| Setup: chọn multi-query hay HyDE                             | ~10ph      | `notes.md`                |
| Bài 1: lọc quyền theo **nhiều nhóm** (`&&`)                   | ~25ph      | `rag.py`                  |
| Bài 2: 5 câu test rò rỉ + chấm leak rate                      | ~30ph      | `eval_set.jsonl` + runner |
| Bài 3: query rewriting                                        | ~40ph      | `rag.py`                  |
| Bài 4: chạy eval, so với dieu-300                             | ~25ph      | `run_eval.py`             |
| Bài 5: metadata filtering                                     | ~20ph      | `rag.py`                  |

**Quy tắc DB:** hôm nay **chỉ đọc** (không cần bảng mới). **Quy tắc đo:** mỗi lần đổi 1 thứ, so với **dieu-300**.

---

## Setup (~10ph)

- [ ] **Multi-query hay HyDE?** (Notion: chọn 1)

  | | Multi-query | HyDE |
  | --- | --- | --- |
  | Cách làm | LLM viết 3–4 phiên bản câu hỏi → search từng bản → gộp | LLM viết 1 **câu trả lời giả** văn phong luật → search bằng nó |
  | Hợp với | Câu nhiều phần (q23, q25), lệch từ ngữ (q05), không dấu (q20) | Câu diễn đạt rất khác văn bản |
  | Rủi ro | Nhiều lần embed + gộp → chậm/tốn hơn chút | Câu trả lời giả **sai** → kéo về đoạn sai (vd. LLM "nhớ" luật cũ) |

- [ ] Model rewrite: dùng `gpt-6-luna` (rẻ, giống bot) hay khác? Ghi lý do.

## Bài 1 — Lọc quyền theo nhiều nhóm (~25ph)

- [ ] Đổi `retrieve(…, group: str)` → `retrieve(…, groups: list[str])`, SQL `WHERE allowed_groups && %(groups)s` (`&&` =
      "2 mảng có phần tử chung không"). **Bắt buộc**, không mặc định (Buổi 16: fail closed). `groups=[]` → sao?
- [ ] Giữ được baseline: eval set có `group: "public"` → truyền `[e["group"]]`.
- [ ] Thử tay: user `["public"]` vs `["public", "internal"]` hỏi "Mức thưởng hiệu suất quý?" → khác nhau đúng như Buổi 16?

Tự trả lời:

1. Vì sao Notion nhấn "filter **TRƯỚC** khi đưa vào LLM, không nhờ prompt 'đừng trả lời'"?
2. `allowed_groups && groups` vs `'public' = ANY(allowed_groups)` — khác gì, khi nào cần cái mới?

## Bài 2 — 5 câu test rò rỉ (~30ph)

- [ ] Thêm q31–q35 vào `eval_set.jsonl`: `type: "leak"`, `group: "public"`, hỏi **đúng** nội dung chỉ có trong nội quy giả
      (thưởng quý, bảng lương bậc, quy trình KL-0429, phụ cấp, thử việc nội bộ…). `reference` = `NOT_FOUND`.
- [ ] Chấm bằng code, **2 lớp**: (1) **retrieve** — top-k có chunk `noi-quy-abc` nào không (phải 0); (2) **câu trả
      lời** — có chứa dấu rò rỉ nào không (`LEAK_MARKERS` Buổi 15/16). Leak rate = số câu rò / 5.
- [ ] Câu nào **gần chủ đề luật** (vd. thử việc, làm thêm giờ) → bot phải trả lời theo **luật** hoặc từ chối, không
      bao giờ ra số của nội quy.

## Bài 3 — Query rewriting (~40ph)

- [ ] Hàm `rewrite(question) -> list[str]` (multi-query) hoặc `-> str` (HyDE). Prompt: thêm dấu, đổi sang từ ngữ luật,
      tách câu nhiều ý. Dùng **structured output** (Phase 01 Buổi 5) để lấy list chắc chắn.
- [ ] Multi-query: search mỗi câu (k=5) → **gộp** (bỏ trùng theo `(doc_id, chunk_index)`, giữ sim cao nhất) → lấy
      top-k cuối. Bot vẫn trả lời **câu hỏi gốc**.
- [ ] Lọc quyền phải áp dụng cho **mọi** câu đã rewrite (rewrite không được mở cửa sau).

Tự trả lời:

1. Rewrite có thể làm hỏng câu `not_found` không (vd. "giá vàng" → LLM "sửa" thành câu luật)? Kiểm 5/5.
2. Chi phí + độ trễ tăng bao nhiêu (thêm 1 lần gọi LLM + nhiều lần embed)?

## Bài 4 — Chạy eval, so với dieu-300 (~25ph)

- [ ] `run_bot(…, table="law_chunks_dieu300", rewrite=True)` → `runs/dieu300-rewrite.jsonl` → chấm code (từ chối
      nhầm/đúng, câu sai, `fact_recall`, **leak rate**) → `eval-results.md`.
- [ ] q05, q20, q23, q25 có được sửa không? Có câu nào tệ đi?

## Bài 5 — Metadata filtering (~20ph)

- [ ] Khi câu hỏi nêu rõ phạm vi (vd. "theo **Điều 25**…", "trong **Chương X**…") → thêm điều kiện SQL theo `heading`.
      Eval set hiện **chưa có** câu kiểu này → thêm 1–2 câu, hoặc ghi lý do bỏ qua.
- [ ] Phân biệt rõ trong code: filter **độ liên quan** (có thể sai, không sao) vs filter **quyền** (không bao giờ được
      sai, luôn bật).

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Multi-query vs HyDE — chọn cái nào, vì sao? Cải thiện bao nhiêu, tốn thêm bao nhiêu?
2. Làm sao bảo đảm RAG không rò rỉ tài liệu nội bộ? Bạn test thế nào?
3. Filter theo độ liên quan khác filter theo quyền thế nào?
