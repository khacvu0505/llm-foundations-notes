"""Buổi 21 Bài 3 — điền cột fts_seg (chữ đã tách từ) cho bảng chunk. GHI DB → user chạy.

Cần chạy trước (DBeaver/psql):
  ALTER TABLE law_chunks_dieu300 ADD COLUMN fts_seg tsvector;
  CREATE INDEX law_chunks_dieu300_fts_seg_idx ON law_chunks_dieu300 USING gin (fts_seg);

Cách dùng: uv run python projects/p2-labor-law-rag/add_fts_seg.py [tên bảng]
  (mặc định law_chunks_dieu300)
"""

import sys

from chunking import segment_text
from psycopg import sql
from rag import get_conn

TABLE = sys.argv[1] if len(sys.argv) > 1 else "law_chunks_dieu300"

if __name__ == "__main__":
  name = sql.Identifier(TABLE)
  with get_conn() as conn:
    rows = conn.execute(sql.SQL("SELECT id, content FROM {}").format(name)).fetchall()
    # 1. Tách từ TRƯỚC, ngoài transaction (bước chậm — như "embed trước" ở Buổi 15)
    updates = [(segment_text(content), row_id) for row_id, content in rows]
    # 2. Ghi trong 1 transaction: cùng thành công hoặc cùng huỷ
    with conn.transaction(), conn.cursor() as cur:
      cur.executemany(
        sql.SQL("UPDATE {} SET fts_seg = to_tsvector('simple', %s) WHERE id = %s").format(name),
        updates,
      )
  print(f"{TABLE}: đã điền fts_seg cho {len(updates)} chunk")
