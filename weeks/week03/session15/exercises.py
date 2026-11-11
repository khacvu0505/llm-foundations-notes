import hashlib
import os
import re
import unicodedata
from pathlib import Path

import docx
import psycopg
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from pgvector import Vector
from pgvector.psycopg import register_vector

load_dotenv()
client = OpenAI()

DATA = Path("projects/p2-labor-law-rag/data/raw")
LAW_FILE = DATA / "18-VBHN-VPQH-2026.docx"

ENC = tiktoken.get_encoding("cl100k_base")
HEADING_RE = re.compile(r"^Điều \d+\.[^\n]*", re.MULTILINE)  # dòng bắt đầu bằng "Điều N."

INTERNAL_FILE = DATA / "internal" / "noi-quy-abc.md"

INSERT_SQL = """
  INSERT INTO law_chunks
    (doc_id, chunk_index, source, heading, content, content_hash, allowed_groups, embedding)
  VALUES
    (%(doc_id)s, %(chunk_index)s, %(source)s, %(heading)s,
     %(content)s, %(content_hash)s, %(allowed_groups)s, %(embedding)s)
"""


def read_docx(path: Path) -> list[str]:
  doc = docx.Document(str(path))
  return [p.text for p in doc.paragraphs]


def clean_paragraphs(paras: list[str]) -> list[str]:
  out = []
  for p in paras:
    p = unicodedata.normalize("NFC", p)
    p = " ".join(p.split())
    if not p:
      continue
    out.append(p)

  start = out.index("Chương I")
  return out[start:]


def chunk_tokens(text: str, size: int = 500, overlap: int = 50) -> list[str]:
  tokens = ENC.encode(text)  # text → list số token
  step = size - overlap  # bước nhảy (nhìn sơ đồ)
  chunks = []
  for start in range(0, len(tokens), step):
    window = tokens[start : start + size]  # cửa sổ dài bao nhiêu?
    chunks.append(ENC.decode_bytes(window).decode("utf-8", errors="ignore"))
    if start + size >= len(tokens):  # cửa sổ này đã chạm cuối → dừng
      break

  return chunks


def build_records(doc_id: str, source: Path, text: str, groups: list[str]) -> list[dict]:
  records = []
  current = None  # tiêu đề Điều gần nhất đã gặp
  for i, chunk in enumerate(chunk_tokens(text)):
    if chunk.lstrip().startswith("Điều "):  # chunk mở đầu đúng bằng 1 Điều
      m = HEADING_RE.match(chunk.lstrip())
      if m:
        current = m.group(0)
    records.append(
      {
        "doc_id": doc_id,
        "chunk_index": i,  # 1. chỉ số thứ tự của chunk
        "source": str(source),
        "heading": current,  # Điều đang "mở" ở đầu chunk
        "content": chunk,
        "content_hash": hashlib.sha256(chunk.encode()).hexdigest(),  # 2. ra chuỗi hex
        "allowed_groups": groups,  # 3. danh sách nhóm được phép truy cập
      }
    )
    found = HEADING_RE.findall(chunk)  # các tiêu đề Điều trong chunk này
    if found:
      current = found[-1]  # tiêu đề cuối → "mở" sang chunk sau
  return records


def embed_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
  vecs: list[list[float]] = []
  for start in range(0, len(texts), batch_size):  # 1. bước nhảy theo kích thước lô
    batch = texts[start : start + batch_size]  # 2. cắt lấy tối đa batch_size phần tử
    resp = client.embeddings.create(input=batch, model="text-embedding-3-small")
    vecs.extend(item.embedding for item in sorted(resp.data, key=lambda d: d.index))
  return vecs


def get_conn() -> psycopg.Connection:
  conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)
  register_vector(conn)
  return conn


def ingest(conn: psycopg.Connection, records: list[dict]) -> None:
  # 1. Embed TRƯỚC — bước dễ lỗi (mạng, API), chưa đụng DB
  vecs = embed_batch([r["content"] for r in records])
  rows = [{**r, "embedding": Vector(v)} for r, v in zip(records, vecs, strict=True)]

  # 2. Xoá bản cũ + thêm bản mới trong 1 transaction: cùng thành công hoặc cùng huỷ
  doc_id = records[0]["doc_id"]
  with conn.transaction():
    conn.execute("DELETE FROM law_chunks WHERE doc_id = %s", (doc_id,))
    with conn.cursor() as cur:
      cur.executemany(INSERT_SQL, rows)
  print(f"{doc_id}: {len(rows)} chunk")


def search(conn: psycopg.Connection, query: str, group: str | None = None, k: int = 3):
  q = Vector(embed_batch([unicodedata.normalize("NFC", query)])[0])  # NFC ở đầu hỏi (Bài 1 câu 2)
  where = "WHERE %(group)s = ANY(allowed_groups)" if group else ""
  return conn.execute(
    f"""
    SELECT doc_id, chunk_index, heading, 1 - (embedding <=> %(q)s) AS sim, left(content, 60)
    FROM law_chunks {where}
    ORDER BY embedding <=> %(q)s
    LIMIT %(k)s
    """,
    {"q": q, "group": group, "k": k},
  ).fetchall()


if __name__ == "__main__":
  # law_text = "\n".join(clean_paragraphs(read_docx(LAW_FILE)))
  # internal_text = unicodedata.normalize("NFC", INTERNAL_FILE.read_text(encoding="utf-8"))

  # law = build_records("bllđ-18-vbhn-2026", LAW_FILE, law_text, ["public"])
  # internal = build_records("noi-quy-abc", INTERNAL_FILE, internal_text, ["internal"])

  # with get_conn() as conn:
  #   ingest(conn, law)
  #   ingest(conn, internal)

  with get_conn() as conn:
    for question in ["Thử việc tối đa bao lâu?", "Mức thưởng hiệu suất quý là bao nhiêu?"]:
      for group in [None, "public"]:
        print(f"\n### {question} | lọc: {group}")
        for row in search(conn, question, group):
          print(row)
