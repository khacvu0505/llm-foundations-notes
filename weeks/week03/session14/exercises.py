import os

import psycopg
from dotenv import load_dotenv
from openai import OpenAI
from pgvector import Vector
from pgvector.psycopg import register_vector

load_dotenv()
client = OpenAI()

# 14 câu của Buổi 13 Bài 3 (BAI3_PAIRS, weeks/week03/session13/exercises.py:95-112), chỉ lấy text.
# Con số trong câu chỉ để so độ giống, KHÔNG phải trích luật.
TEXTS = [
  "Nghỉ phép năm 12 ngày",
  "Mỗi năm được nghỉ 12 ngày có lương",
  "Thời gian thử việc tối đa 60 ngày",
  "The probation period is at most 60 days",
  "Bàn gỗ trong phòng họp",
  "Bàn kế hoạch tăng lương",
  "Người lao động được làm thêm giờ",
  "Người lao động không được làm thêm giờ",
  "Trợ cấp thôi việc",
  "tro cap thoi viec",
  "Hợp đồng lao động",
  "Công thức nấu phở bò",
  "Thử việc được bao lâu?",
  "Thời gian thử việc không quá 60 ngày đối với công việc cần trình độ cao đẳng trở lên",
]


def get_conn() -> psycopg.Connection:
  url = os.environ["DATABASE_URL"]
  conn = psycopg.connect(url, autocommit=True)
  conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
  register_vector(conn)
  conn.execute("""
    CREATE TABLE IF NOT EXISTS chunks(
      id  bigserial PRIMARY KEY,
      content text NOT NULL,
      embedding vector(1536) NOT NULL
    )
  """)
  return conn


def embed(texts: list[str]) -> list[list[float]]:
  response = client.embeddings.create(input=texts, model="text-embedding-3-small")
  return [item.embedding for item in response.data]


def insert_chunks(conn: psycopg.Connection, texts: list[str]):
  # bước 1: xoá dữ liệu cũ (chạy lại không bị trùng)
  conn.execute("TRUNCATE chunks RESTART IDENTITY")

  # bước 2: embed cả 14 câu trong 1 request
  vecs = embed(texts)

  # bước 3a + 3b: ghép cặp + bọc vector
  rows = [(t, Vector(v)) for t, v in zip(texts, vecs, strict=True)]

  # bước 3c: insert 14 dòng
  with conn.cursor() as cur:
    cur.executemany("INSERT INTO chunks (content, embedding) VALUES (%s, %s)", rows)

  print(f"Đã insert {len(rows)} dòng")


def search(conn: psycopg.Connection, query: str, k: int = 3) -> list[tuple[str, float]]:
  q = Vector(embed([query])[0])  # embed nhận list → lấy vector đầu tiên

  rows = conn.execute(
    """
    SELECT content, 1 - (embedding <=> %(q)s) AS similarity
    FROM chunks
    ORDER BY embedding <=> %(q)s
    LIMIT %(k)s
    """,
    {"q": q, "k": k},
  ).fetchall()
  return rows


if __name__ == "__main__":
  with get_conn() as conn:  # "with" → tự đóng kết nối khi xong
    for i, (content, sim) in enumerate(search(conn, "Thử việc được bao lâu?"), start=1):
      print(f"{i}. {sim:.4f}  {content}")
