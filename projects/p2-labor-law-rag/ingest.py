import sys

import psycopg
from chunking import (
  INTERNAL_FILE,
  LAW_FILE,
  build_records,
  group_by_dieu,
  read_markdown,
  read_paragraphs,
)
from pgvector import Vector
from psycopg import sql
from rag import client, get_conn

INSERT = """
  INSERT INTO {}
    (doc_id, chunk_index, source, heading, content, content_hash, allowed_groups, embedding)
  VALUES (%(doc_id)s, %(chunk_index)s, %(source)s, %(heading)s, %(content)s,
          %(content_hash)s, %(allowed_groups)s, %(embedding)s)
"""


def embed_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
  vecs: list[list[float]] = []
  for start in range(0, len(texts), batch_size):
    resp = client.embeddings.create(
      input=texts[start : start + batch_size], model="text-embedding-3-small"
    )
    vecs.extend(d.embedding for d in sorted(resp.data, key=lambda d: d.index))
  return vecs


def ingest(conn: psycopg.Connection, table: str, records: list[dict]) -> None:
  vecs = embed_batch([r["content"] for r in records])  # 1. embed TRƯỚC (Buổi 15)
  rows = [{**r, "embedding": Vector(v)} for r, v in zip(records, vecs, strict=True)]
  name = sql.Identifier(table)  # tên bảng an toàn trong SQL
  with conn.transaction():  # 2. xoá + thêm: cùng thành công / cùng huỷ
    conn.execute(sql.SQL("DELETE FROM {} WHERE doc_id = %s").format(name), (records[0]["doc_id"],))
    with conn.cursor() as cur:
      cur.executemany(sql.SQL(INSERT).format(name), rows)
  print(f"{table}: {records[0]['doc_id']} → {len(rows)} chunk")


if __name__ == "__main__":
  # Cách dùng: uv run python projects/p2-labor-law-rag/ingest.py <tên bảng> <max_tokens>
  #   vd. ... ingest.py law_chunks_dieu 500   (mặc định nếu không truyền gì)
  TABLE = sys.argv[1] if len(sys.argv) > 1 else "law_chunks_dieu"
  MAX_TOKENS = int(sys.argv[2]) if len(sys.argv) > 2 else 500
  law = build_records(
    "bllđ-18-vbhn-2026",
    LAW_FILE,
    group_by_dieu(read_paragraphs(LAW_FILE)),
    ["public"],
    max_tokens=MAX_TOKENS,
  )
  internal = build_records(
    "noi-quy-abc",
    INTERNAL_FILE,
    group_by_dieu(read_markdown(INTERNAL_FILE)),
    ["internal"],
    max_tokens=MAX_TOKENS,
  )
  with get_conn() as conn:
    ingest(conn, TABLE, law)
    ingest(conn, TABLE, internal)
