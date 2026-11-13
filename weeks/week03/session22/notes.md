# Buổi 22 — Phase 02 Buổi 10: Reranking (2h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 rerank() · [x] Bài 2 pipeline 37 câu · [x] Bài 3 latency + chi phí · [x] Bài 4 model thứ 2 ·
  [ ] 3 câu phỏng vấn

## Handoff — dừng ở đây (cập nhật 2026-11-13)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Xong Setup + Bài 1–4** (Claude viết code theo "write for me"). Rerank sửa q02; từ chối nhầm 3 → 2 (bge) / 1 (mmarco,
nhưng q25 bị cắt ngang); `fact_recall` 0.89 → 0.95; leak 0/5. Đề xuất `mmarco` (+13% độ trễ vs +86%).

**Việc tiếp theo**: user xác nhận chọn model → điền 2 câu tự trả lời Bài 1 + 3 câu phỏng vấn → ghi `eval-results.md` →
commit (user chạy). Tải model: nếu treo, dùng `HF_HUB_DISABLE_XET=1`.

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nhờ); user tự làm git + `uv add`;
hôm nay chỉ đọc DB; mỗi lần đo đổi 1 thứ; notes tiếng Việt, có bảng + nguồn.

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-13.)_

- Git: Buổi 21 đã commit (`ccdb098`). `sentence_transformers.CrossEncoder` import được.
- Mốc so sánh: dieu-300 **hybrid tách từ**, không rewrite — từ chối nhầm 3/27 (q02, q20, q25), `fact_recall` 0.89, leak
  0/5 (`runs/dieu300-hybrid-seg.jsonl`).
- Ứng viên reranker: `BAAI/bge-reranker-v2-m3` (apache-2.0, lớn), `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
  (apache-2.0, nhỏ, tag `vi`), `jinaai/jina-reranker-v2-base-multilingual` (**cc-by-nc** → loại), Cohere API (trả phí).

## Setup

| Mục | Quyết định + lý do |
| --- | --- |
| Reranker | Thử **cả 2 model local** (Hugging Face, đã huấn luyện sẵn, chạy qua `sentence_transformers.CrossEncoder`): **lớn** `BAAI/bge-reranker-v2-m3` + **nhỏ** `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` → có số "chất lượng vs độ trễ" (user đồng ý 2026-11-13) |
| Local hay API | **Local** — $0 tiền API, **dữ liệu không rời máy** (quan trọng với tài liệu nội bộ, Buổi 16); đổi lại tốn CPU/RAM, lần đầu tải model vào `~/.cache/huggingface/` |

## Bài 1 — rerank()

Code (Claude viết theo yêu cầu "write for me"): `rag.py` — `RERANKERS`, `get_reranker()` (nạp **1 lần**, lazy import
`sentence_transformers`), `rerank(question, chunks, top_n=5, model="bge")` → thêm khoá `"rerank"`, giữ `"sim"` (RRF).

**Thử q02** ("Lao động nữ được nghỉ thai sản bao lâu?"), top-20 hybrid tách từ (`law_chunks_dieu300`, `fts_seg`).
Đích = **chunk #273** (Khoản 1 Điều 139, "06 tháng … 07 tháng") — _chú ý: #276 cũng chứa "06 tháng" ("dưới 06 tháng
tuổi", Khoản 5) → đánh dấu theo `chunk_index`, không theo chữ_:

| | Hạng #273 | Top-5 |
| --- | --- | --- |
| Trước (RRF) | **6** → bị đẩy khỏi top-5 → bot từ chối (Buổi 21) | 137#270, 139#275, 139#276, 137#269, 139#274 |
| Sau rerank `bge` | **1** (0.9987) | 139#273, 139#275, 137#270, 139#276, 137#269 |
| Sau rerank `mmarco` | **1** (8.49) | 139#273, 137#270, 139#275, 139#276, 139#274 |

- Điểm RRF top-6 sát nhau (0.0313 → 0.0305) = RRF **không phân biệt được**; cross-encoder tách rõ (bge 0.9987 vs đoạn
  "rác" 0.02).
- **Không so điểm giữa 2 model**: `bge` ra 0–1, `mmarco` ra số thô (−8.9 → 8.5) — chỉ so **hạng** (bài học Buổi 13).
- Thời gian (lần gọi **đầu**, chưa đo kỹ — Bài 3 đo lại): nạp `bge` 9.8s, rerank 20 cặp **3117 ms**; nạp `mmarco` 7.6s,
  rerank **818 ms**.
- Sự cố tải model: tải qua backend **Xet** của HF bị **treo** (file `.incomplete`, 0% CPU, 2 lần). Tắt Xet
  (`HF_HUB_DISABLE_XET=1`) → tải 470 MB trong 7s. Đã có cả 2 model trong `~/.cache/huggingface/`.

Tự trả lời (user điền):

- Cross-encoder vs bi-encoder:
- Rerank và lọc quyền:

## Bài 2–4 — Kết quả

Chạy 2026-11-13, 37 câu, dieu-300 hybrid tách từ (`fts_seg`) → top-20 → rerank → top-5 → LLM. Code (Claude viết):
`answer(…, rerank_model, rerank_pool=20)` (chặn nếu không có hybrid — mỗi lần đổi 1 thứ), trả thêm `rerank_seconds`,
`rerank` từng chunk; `run_bot(…, rerank_model)` nạp model **trước** vòng lặp. File: `runs/dieu300-hybrid-seg-rerank-{bge,mmarco}.jsonl`.
Máy: Apple M2, cả 2 model chạy GPU `mps`.

| Cấu hình | Từ chối nhầm | Sai | `fact_recall` | Leak | Rerank ms/câu (TB / trung vị / max) | Tổng s/câu (TB) | Tiền LLM 37 câu |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hybrid tách từ (mốc) | 3/27 (q02, q20, q25) | 0 | 0.89 | 0/5 | — | 3.18 | $0.0055 |
| + rerank `bge` (568M) | **2/27** (q20, q25) | 0 | **0.95** | 0/5 | **3034** / 2947 / 5443 | 5.93 (**+86%**) | $0.0061 |
| + rerank `mmarco` (118M) | **1/27** (q20) ⚠️ | 0 | **0.95** | 0/5 | **559** / 463 / 1184 | 3.58 (**+13%**) | $0.0061 |

- Từ chối đúng not_found: 5/5 cả 3 cấu hình. "Sai" = chấm code: mọi câu trả lời (không từ chối) có `fact_recall`
  1.00, trừ q25 mmarco (0.67) — **chưa đọc tay** từng câu.
- **q02 được sửa** ở cả 2 model (Bài 1: #273 từ hạng 6 → 1). Không câu nào tệ đi so với mốc.
- ⚠️ **q25 mmarco không thật sự "đúng"**: câu trả lời **bị cắt ngang** ("…được liệt") — chạm trần
  `max_output_tokens=600` (tokens ra = 600; các cấu hình khác 144–374). Có Điều 125 (sa thải) + Điều 46, **thiếu Điều 34**
  → chỉ trả lời được nửa câu. Tính công bằng: 2 model **ngang nhau** (q20, q25 vẫn khó). _Giả thuyết, chưa kiểm_: phần lớn
  600 token là token suy luận của model.
- q20 (gõ không dấu) vẫn hỏng — rerank không cứu được vì đoạn đúng **không có trong top-20** (hit=False).
- q35 (leak) không từ chối — đúng: hỏi làm thêm giờ, trả lời từ **luật** Điều 98 (150%), 0 chunk nội bộ, giống mốc.

### Bài 3 — Latency + chi phí

| | `bge` | `mmarco` |
| --- | --- | --- |
| Nạp model (1 lần/khởi động) | 13.7–21.1 s | 7.6–8.4 s |
| Rerank 20 cặp / câu (TB) | 3.03 s | 0.56 s |
| Tổng / câu so với mốc 3.18 s | +2.75 s (+86%) | +0.40 s (+13%) |
| Tiền rerank | $0 (local) | $0 (local) |
| Tiền LLM | +11% ($0.0055 → $0.0061): top-5 sau rerank là đoạn **dài hơn** (input TB 1072 → ~1158 token) | như bge |
| Tải về đĩa | 2.1 GB | 470 MB |

- Độ trễ `bge` không do tải: model đã nạp trước vòng lặp; 568M tham số × 20 cặp, độ dài tối đa 8192 (mmarco 512).
- Nếu dùng API (Cohere…): $0 CPU nhưng **tài liệu nội bộ gửi ra ngoài** + giá/độ trễ mạng — _chưa kiểm giá_.

### Bài 4 — Chọn

- **Đề xuất (Claude)**: `mmarco` — chất lượng **ngang** `bge` trên bộ 37 câu (`fact_recall` 0.95 cả hai, cùng sửa q02),
  nhưng rerank **nhanh hơn ~5×** (0.56 s vs 3.03 s), tổng chỉ +13% thay vì +86%, model nhỏ hơn 4.5×.
- Lưu ý: mới **1 lần chạy**, bộ 37 câu nhỏ → khác biệt 1 câu chưa đủ kết luận `bge` tốt hơn/kém hơn.
- **Chọn: `mmarco`** (user xác nhận 2026-11-13) — mang sang Buổi 11–12: hybrid tách từ → top-20 → rerank `mmarco` → top-5.

## Câu phỏng vấn cuối buổi

### 1. Rerank đổi lấy bao nhiêu latency

### 2. Cross-encoder vs bi-encoder

### 3. Khi nào không dùng rerank
