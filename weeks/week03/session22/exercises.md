# Buổi 22 — Phase 02 Buổi 10: Reranking (2h)

Phase 02 — RAG + Evals, Tuần 4 "Cải tiến có đo lường". Nguồn: Notion "Phase 02 — RAG + Evals", page version 46 (Claude
đọc 2026-11-12).

Checklist Notion Buổi 10:

- Thêm **reranker** (Cohere Rerank API hoặc **cross-encoder local**): lấy **top-20 → rerank → top-5**
- **Đo lại + đo thêm latency/cost tăng bao nhiêu** — trade-off phải nói được **bằng số**

Câu exit Phase 02 liên quan: "**Rerank đổi lấy bao nhiêu latency?**"

Nối với buổi trước — vì sao cần rerank (bằng chứng của chính mình):

- **q24** (Buổi 20, có rewrite) và **q02** (Buổi 21, hybrid tách từ) hỏng **cùng kiểu**: đoạn đúng (Khoản 1 Điều 139,
  "06/07 tháng") **có trong top-20** nhưng các mảnh khác của Điều 137/139 chiếm hết **5 chỗ** → bot từ chối.
- Cấu hình mốc: **dieu-300 hybrid tách từ** (`law_chunks_dieu300`, cột `fts_seg`, không rewrite): từ chối nhầm 3/27 (q02,
  q20, q25), `fact_recall` 0.89, leak 0/5.

Claude kiểm trước (2026-11-13): `sentence_transformers.CrossEncoder` import được (đã có `sentence-transformers` từ Buổi
13). Ứng viên trên Hugging Face (API, read-only):

| Model | License | Ghi chú |
| --- | --- | --- |
| `BAAI/bge-reranker-v2-m3` | apache-2.0 | Đa ngữ, rất phổ biến (~14.6M lượt tải); **lớn** (**567.8M** tham số — HF API `safetensors.total`, kiểm 2026-11-13) → chậm trên CPU |
| `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | apache-2.0 | Đa ngữ, có tag **`vi`**; **nhỏ** (**117.6M** tham số — HF API, kiểm 2026-11-13) → nhanh |
| `jinaai/jina-reranker-v2-base-multilingual` | **cc-by-nc-4.0** | **Cấm dùng thương mại** → loại cho Project #2 |
| Cohere Rerank API | trả phí | Cần tài khoản + API key; dữ liệu gửi ra ngoài; _giá chưa kiểm_ |

| Phần                                                    | Thời lượng | Làm ở đâu      |
| ------------------------------------------------------- | ---------- | -------------- |
| Setup: chọn reranker                                     | ~10ph      | `notes.md`     |
| Bài 1: `rerank()` + thử tay q02, q24                      | ~25ph      | `rag.py`       |
| Bài 2: top-20 → rerank → top-5, chạy 37 câu              | ~30ph      | `run_eval.py`  |
| Bài 3: đo latency + chi phí                              | ~20ph      | `notes.md`     |
| Bài 4: thử model thứ 2, bảng chất lượng vs độ trễ         | ~25ph      | `eval-results` |

**Quy tắc DB:** hôm nay **chỉ đọc**. **Quy tắc đo:** so với **hybrid tách từ** (không rewrite), chỉ thêm bước rerank.

---

## Setup (~10ph)

- [ ] Chọn reranker (gợi ý: thử **cả 2 model local** — lớn và nhỏ — để có số "chất lượng vs độ trễ"). Lần đầu chạy sẽ
      **tải model** từ Hugging Face (vài trăm MB → vài GB).
- [ ] Local hay API? (local: miễn phí, dữ liệu không ra ngoài, tốn CPU/RAM; API: nhanh/ổn định, trả tiền, dữ liệu đi ra
      ngoài — nhớ tài liệu nội bộ, Buổi 16.)

## Bài 1 — `rerank()` (~25ph)

- [ ] `rerank(question, chunks, top_n=5)`: `CrossEncoder.predict([(question, c["content"]) for c in chunks])` → sắp theo
      điểm → giữ `top_n`. Nạp model **1 lần** (không nạp lại mỗi câu hỏi).
- [ ] Thử tay q02 ("Lao động nữ được nghỉ thai sản bao lâu?"): trong top-20, đoạn Khoản 1 Điều 139 đứng hạng mấy **trước**
      và **sau** rerank?

Tự trả lời:

1. Cross-encoder (đọc câu hỏi + đoạn **cùng lúc**) khác bi-encoder (embedding, mã hoá **riêng**) thế nào? Vì sao chính
   xác hơn nhưng chậm hơn?
2. Rerank có ảnh hưởng tới **lọc quyền** không?

## Bài 2 — Pipeline top-20 → rerank → top-5 (~30ph)

- [ ] `answer(…, rerank_model=…)`: lấy top-20 từ hybrid (tách từ) → rerank → top-5 → LLM. Chạy 37 câu.
- [ ] Chấm code: từ chối nhầm/đúng, câu sai, `fact_recall`, **leak**. q02 có được sửa không? Có câu nào tệ đi?

## Bài 3 — Đo latency + chi phí (~20ph)

- [ ] Tách thời gian: tải model (1 lần), rerank mỗi câu (20 cặp), tổng thời gian/câu so với không rerank.
- [ ] Chi phí: local = $0 tiền API nhưng tốn CPU/RAM; ước nếu dùng API.

## Bài 4 — Model thứ 2 + bảng đánh đổi (~25ph)

- [ ] Chạy lại Bài 2 với model kia → bảng: từ chối nhầm, `fact_recall`, ms/câu cho rerank, tổng s/câu.
- [ ] Chọn cấu hình mang sang Buổi 12 (tổng hợp) — ghi lý do bằng số.

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Rerank đổi lấy bao nhiêu latency? Đáng không? (câu exit Phase 02)
2. Cross-encoder khác bi-encoder thế nào? Vì sao không dùng cross-encoder để tìm ngay từ đầu?
3. Khi nào bạn **không** dùng rerank?
