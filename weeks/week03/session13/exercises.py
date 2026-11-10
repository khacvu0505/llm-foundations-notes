import json
import math
import time
from collections.abc import Sequence

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


BAI1_SENTENCES = [
  "Người lao động được nghỉ phép năm 12 ngày.",  # câu gốc (Việt)
  "Employees are entitled to 12 days of annual leave.",  # bản dịch (Anh) → cặp gần
  "Hôm nay trời Hà Nội mưa to.",  # không liên quan → cặp xa
]


def run_bai1() -> None:
  response = client.embeddings.create(
    input=BAI1_SENTENCES,
    model="text-embedding-3-small",
  )
  for item in response.data:
    data_dict = item.model_dump()  # Hoặc item.dict() với bản cũ hơn
    data_dict["text"] = BAI1_SENTENCES[item.index]  # câu gốc của vector này
    data_dict["dims"] = len(item.embedding)  # đo TRƯỚC khi cắt
    # Cắt bớt mảng embedding chỉ hiển thị 5 số đầu trong JSON cho gọn
    data_dict["embedding"] = data_dict["embedding"][:5] + ["... (đã rút gọn)"]

    print(json.dumps(data_dict, indent=2, ensure_ascii=False))

  # usage tính cho cả request (3 câu), nên in 1 lần sau vòng lặp
  print("usage:", response.usage)


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
  """Cosine = (a · b) / (|a| × |b|). Python thuần, không numpy."""
  # 1. Guard: 2 vector phải cùng số chiều (khác model / khác dimensions → so vô nghĩa)
  if len(a) != len(b):
    raise ValueError(f"Lengths must match: {len(a)} != {len(b)}")

  # 2. Tích vô hướng: a[0]*b[0] + a[1]*b[1] + ...
  dot = sum(x * y for x, y in zip(a, b, strict=True))

  # 3. Độ dài từng vector: sqrt(a[0]² + a[1]² + ...)
  norm_a = math.sqrt(sum(x * x for x in a))
  norm_b = math.sqrt(sum(y * y for y in b))

  # Vector toàn 0 → độ dài 0 → chia cho 0
  if norm_a == 0 or norm_b == 0:
    raise ValueError("Cosine is undefined for a zero vector")

  # 4. Ghép lại
  return dot / (norm_a * norm_b)


def run_bai2() -> None:
  # Test tay bằng vector 2 chiều (isclose vì số thực có thể lệch rất nhỏ)
  assert math.isclose(cosine_similarity([1, 0], [1, 0]), 1.0)  # cùng hướng
  assert math.isclose(cosine_similarity([1, 0], [-1, 0]), -1.0)  # ngược hướng
  assert math.isclose(cosine_similarity([1, 0], [0, 1]), 0.0, abs_tol=1e-12)  # vuông góc
  assert math.isclose(cosine_similarity([1, 0], [5, 0]), 1.0)  # cùng hướng, dài hơn → vẫn 1
  for bad in ([1, 2], [1, 2, 3]), ([0, 0], [1, 1]):
    try:
      cosine_similarity(*bad)
    except ValueError as e:
      print(f"OK raise ValueError: {e}")
    else:
      raise AssertionError(f"Expected ValueError for {bad}")
  print("4/4 test tay pass + 2 case lỗi đúng\n")

  # Dùng cho 3 câu của Bài 1
  response = client.embeddings.create(input=BAI1_SENTENCES, model="text-embedding-3-small")
  vecs = [item.embedding for item in response.data]
  vi, en, weather = vecs

  print(f"Việt ↔ Anh (cùng nghĩa):    {cosine_similarity(vi, en):.4f}")
  print(f"Việt ↔ thời tiết (khác):    {cosine_similarity(vi, weather):.4f}")
  print(f"Anh  ↔ thời tiết (khác):    {cosine_similarity(en, weather):.4f}")

  # Độ dài vector: docs nói đã chuẩn hoá về 1
  for text, v in zip(BAI1_SENTENCES, vecs, strict=True):
    print(f"|v| = {math.sqrt(sum(x * x for x in v)):.6f}  ← {text}")

  # So với numpy (có sẵn vì pandas kéo về)
  a, b = np.array(vi), np.array(en)
  np_cos = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
  print(f"Lệch so với numpy: {abs(np_cos - cosine_similarity(vi, en)):.2e}")


# Bài 3 — cặp câu chủ đề luật lao động. Con số trong câu chỉ để so độ giống, KHÔNG phải trích luật.
BAI3_PAIRS: list[tuple[str, str, str]] = [
  ("Diễn đạt lại", "Nghỉ phép năm 12 ngày", "Mỗi năm được nghỉ 12 ngày có lương"),
  ("Dịch Việt–Anh", "Thời gian thử việc tối đa 60 ngày", "The probation period is at most 60 days"),
  ("Cùng chữ, khác nghĩa", "Bàn gỗ trong phòng họp", "Bàn kế hoạch tăng lương"),
  (
    "Phủ định",
    "Người lao động được làm thêm giờ",
    "Người lao động không được làm thêm giờ",
  ),
  ("Không dấu", "Trợ cấp thôi việc", "tro cap thoi viec"),
  ("Không liên quan", "Hợp đồng lao động", "Công thức nấu phở bò"),
  # Thêm: đúng hình dạng RAG (câu hỏi ↔ đoạn trả lời)
  (
    "Câu hỏi ↔ đoạn",
    "Thử việc được bao lâu?",
    "Thời gian thử việc không quá 60 ngày đối với công việc cần trình độ cao đẳng trở lên",
  ),
]

E5_MODEL = "intfloat/multilingual-e5-small"


def ranks(scores: list[float]) -> list[int]:
  """Hạng của từng điểm: 1 = cao nhất (giống nhất)."""
  order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
  result = [0] * len(scores)
  for rank, i in enumerate(order, start=1):
    result[i] = rank
  return result


def run_bai3() -> None:
  # Import ở đây: torch nặng, không làm chậm Bài 1–2
  from sentence_transformers import SentenceTransformer

  texts = [t for _, a, b in BAI3_PAIRS for t in (a, b)]  # [a0, b0, a1, b1, ...]

  # OpenAI: 1 request cho cả 14 câu
  start = time.perf_counter()
  response = client.embeddings.create(input=texts, model="text-embedding-3-small")
  openai_ms = (time.perf_counter() - start) * 1000
  oa_vecs = [item.embedding for item in response.data]

  # e5 local. Model card: so độ giống (task đối xứng) → cả 2 câu đều tiền tố "query: "
  model = SentenceTransformer(E5_MODEL)  # lần đầu sẽ tải model về máy
  start = time.perf_counter()
  e5_vecs = model.encode([f"query: {t}" for t in texts], normalize_embeddings=True).tolist()
  e5_ms = (time.perf_counter() - start) * 1000

  oa_scores = [
    cosine_similarity(oa_vecs[2 * i], oa_vecs[2 * i + 1]) for i in range(len(BAI3_PAIRS))
  ]
  e5_scores = [
    cosine_similarity(e5_vecs[2 * i], e5_vecs[2 * i + 1]) for i in range(len(BAI3_PAIRS))
  ]
  oa_ranks, e5_ranks = ranks(oa_scores), ranks(e5_scores)

  print(f"\n{'Loại cặp':<22} {'OpenAI':>7} {'hạng':>4}   {'e5':>7} {'hạng':>4}")
  print("-" * 52)
  for i, (kind, a, b) in enumerate(BAI3_PAIRS):
    print(
      f"{kind:<22} {oa_scores[i]:>7.4f} {oa_ranks[i]:>4}   {e5_scores[i]:>7.4f} {e5_ranks[i]:>4}"
      f"   | {a} ↔ {b}"
    )

  print(f"\nSố chiều: OpenAI {len(oa_vecs[0])} · e5 {len(e5_vecs[0])}")
  print(f"Thời gian embed 14 câu: OpenAI {openai_ms:.0f}ms (qua mạng) · e5 {e5_ms:.0f}ms (local)")
  print(f"OpenAI usage: {response.usage}")


if __name__ == "__main__":
  run_bai3()
