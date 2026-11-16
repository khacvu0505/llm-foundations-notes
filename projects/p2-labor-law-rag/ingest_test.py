"""Buổi 23 Bài 3 — nạp tài liệu TEST GIẢ (indirect prompt injection). GHI DB → user chạy.

Chỉ nạp `data/raw/test/injection-*.md` với nhóm riêng `injection-test`:
- 37 câu eval cũ chỉ hỏi nhóm `public`/`internal` → KHÔNG thấy các chunk này (không làm bẩn).
- Câu eval injection hỏi `["public", "injection-test"]` → đi đủ đường retrieve thật.

Khác `ingest.py` (nạp lại CẢ bộ luật, mất `fts_seg`): chỉ đụng các dòng có doc_id `injection-*`,
và điền luôn `fts_seg` cho chúng (cùng cách tách từ như `add_fts_seg.py`).

Cách dùng (từ thư mục gốc repo):
  uv run --env-file .env python projects/p2-labor-law-rag/ingest_test.py          # xem trước
  uv run --env-file .env python projects/p2-labor-law-rag/ingest_test.py --write  # ghi DB
Chạy lại nhiều lần vẫn an toàn: `ingest()` xoá theo doc_id rồi thêm lại.

Gỡ tài liệu test khỏi bảng (user chạy):
  DELETE FROM law_chunks_dieu300 WHERE doc_id LIKE 'injection-%';
"""

import sys
from pathlib import Path

from chunking import build_records, group_by_dieu, read_markdown, segment_text
from ingest import ingest
from psycopg import sql
from rag import get_conn

TABLE = "law_chunks_dieu300"
MAX_TOKENS = 300  # giống lúc tạo law_chunks_dieu300 (Buổi 19, chọn 300)
GROUP = ["injection-test"]
TEST_DIR = Path(__file__).resolve().parent / "data" / "raw" / "test"

if __name__ == "__main__":
  write = "--write" in sys.argv
  docs = [
    build_records(f.stem, f, group_by_dieu(read_markdown(f)), GROUP, max_tokens=MAX_TOKENS)
    for f in sorted(TEST_DIR.glob("injection-*.md"))
  ]
  docs = [d for d in docs if d]  # bỏ file không tách được Điều nào
  if not docs:
    sys.exit(f"Không có chunk nào trong {TEST_DIR}/injection-*.md")
  for records in docs:
    for r in records:
      print(f"{r['doc_id']} #{r['chunk_index']}  {r['allowed_groups']}  {r['heading']}")
  if not write:
    print(f"\nXem trước — chưa ghi. Thêm --write để nạp vào {TABLE}.")
    sys.exit(0)

  # 1. Tách từ TRƯỚC, ngoài transaction (bước chậm — như add_fts_seg.py)
  seg = {(r["doc_id"], r["chunk_index"]): segment_text(r["content"]) for d in docs for r in d}
  name = sql.Identifier(TABLE)
  with get_conn() as conn, conn.transaction():  # 2. tất cả cùng thành công / cùng huỷ
    for records in docs:
      ingest(conn, TABLE, records)  # embed + xoá theo doc_id + thêm (transaction lồng = savepoint)
    with conn.cursor() as cur:
      cur.executemany(
        sql.SQL(
          "UPDATE {} SET fts_seg = to_tsvector('simple', %s) WHERE doc_id = %s AND chunk_index = %s"
        ).format(name),
        [(text, doc_id, idx) for (doc_id, idx), text in seg.items()],
      )
  print(f"{TABLE}: đã nạp + điền fts_seg cho {len(seg)} chunk test")
