import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # thư mục eval/
sys.path.insert(0, str(HERE.parent))  # để import rag.py ở thư mục cha
import rag  # noqa: E402
from deepeval.metrics import (  # noqa: E402
  AnswerRelevancyMetric,
  ContextualPrecisionMetric,
  ContextualRecallMetric,
  FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase  # noqa: E402

EVAL_SET = HERE / "eval_set.jsonl"
RUNS = HERE / "runs"
NOT_FOUND = rag.NOT_FOUND
JUDGE = "gpt-5.4-mini"  # Setup: rẻ, khác dòng với bot gpt-6-luna; Bài 6 quyết định có giữ không
THRESHOLD = 0.5  # giữ nguyên mọi lần chạy để so sánh công bằng
METRICS = {
  "recall": ContextualRecallMetric,
  "precision": ContextualPrecisionMetric,
  "faithfulness": FaithfulnessMetric,
  "relevancy": AnswerRelevancyMetric,
}


def load_jsonl(path: Path) -> list[dict]:
  return [
    json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
  ]


def run_bot(out: Path, table: str = "law_chunks") -> None:
  items = load_jsonl(EVAL_SET)
  out.parent.mkdir(parents=True, exist_ok=True)
  with rag.get_conn() as conn, out.open("w", encoding="utf-8") as f:
    for i, item in enumerate(items, start=1):
      r = rag.answer(conn, item["question"], item["group"], table=table)  # nhóm quyền của câu này
      f.write(json.dumps({"id": item["id"], **r}, ensure_ascii=False) + "\n")
      f.flush()  # ghi ngay, lỡ lỗi giữa chừng vẫn giữ được
      print(f"{i}/{len(items)} {item['id']}  {r['seconds']}s  ${r['cost'] or 0:.5f}")


def source_hit(source: str, chunks: list[dict]) -> bool:
  """'Điều 25' có trong top-5 không: so heading HOẶC nội dung chứa 'Điều 25.' (Buổi 17 Bài 1)."""
  m = re.search(r"\d+", source)
  if not m:
    return False
  n = m.group()
  return any(
    (c["heading"] or "").startswith(f"Điều {n}.") or f"Điều {n}." in c["content"] for c in chunks
  )


def fact_recall(chunks: list[dict], key_facts: list[str]) -> float | None:
  """Buổi 19: tỷ lệ key_facts (chuỗi y nguyên trong luật) có trong top-k chunk — không cần LLM."""
  if not key_facts:
    return None
  text = "\n".join(c["content"] for c in chunks)
  return sum(f in text for f in key_facts) / len(key_facts)


def grade_by_code(run_file: Path) -> None:
  """Bài 2: chấm không cần LLM — Điều nguồn có trong top-5 không, bot có từ chối không."""
  items = {e["id"]: e for e in load_jsonl(EVAL_SET)}
  answerable = hit_all = wrong_refusal = right_refusal = 0
  recalls: list[float] = []
  for r in load_jsonl(run_file):
    e = items[r["id"]]
    refused = r["answer"].strip() == NOT_FOUND
    hits = [source_hit(s, r["chunks"]) for s in e["sources"]]
    fr = fact_recall(r["chunks"], e.get("key_facts", []))
    fr_txt = "-" if fr is None else f"{fr:.2f}"
    print(f"{e['id']}  {e['type']:9}  refused={refused!s:5}  fact_recall={fr_txt}  hit={hits}")
    if fr is not None:
      recalls.append(fr)
    if e["type"] == "not_found":
      right_refusal += refused
    else:
      answerable += 1
      hit_all += all(hits)
      wrong_refusal += refused
  avg = sum(recalls) / len(recalls) if recalls else 0.0
  full = sum(x == 1.0 for x in recalls)
  print(f"\nfact_recall TB: {avg:.2f} | đủ 100% dữ kiện: {full}/{len(recalls)}")
  print(f"Hit đủ Điều nguồn (lạc quan): {hit_all}/{answerable}")
  print(f"Từ chối nhầm (câu có đáp án): {wrong_refusal}/{answerable}")
  print(f"Từ chối đúng (not_found): {right_refusal}/5")


def grade_deepeval(
  run_file: Path, out: Path, only: set[str] | None = None, judge: str = JUDGE
) -> None:
  """Bài 3: chấm 4 metric DeepEval cho câu có đáp án.

  Ghi nối vào `out`, bỏ qua câu đã chấm → chạy tiếp được, không trả tiền 2 lần.
  """
  items = {e["id"]: e for e in load_jsonl(EVAL_SET)}
  done = {r["id"] for r in load_jsonl(out)} if out.exists() else set()
  total = 0.0
  with out.open("a", encoding="utf-8") as f:  # "a" = ghi nối, không xoá kết quả cũ
    for r in load_jsonl(run_file):
      e = items[r["id"]]
      if e["type"] == "not_found" or r["id"] in done or (only and r["id"] not in only):
        continue  # not_found chấm riêng ở Bài 2
      case = LLMTestCase(
        input=e["question"],
        actual_output=r["answer"],
        expected_output=e["reference"],
        retrieval_context=[c["content"] for c in r["chunks"]],
      )
      row: dict = {"id": e["id"], "type": e["type"]}
      for name, Metric in METRICS.items():
        m = Metric(model=judge, threshold=THRESHOLD)
        m.measure(case)
        row[name] = {"score": m.score, "reason": m.reason, "cost": m.evaluation_cost}
        total += m.evaluation_cost or 0
      f.write(json.dumps(row, ensure_ascii=False) + "\n")
      f.flush()
      scores = {k: round(v["score"], 2) for k, v in row.items() if isinstance(v, dict)}
      print(e["id"], scores)
  print(f"Giám khảo {judge} — chi phí lần này: ${total:.4f}")


if __name__ == "__main__":
  # Buổi 18 (baseline, bảng law_chunks) — đã chạy xong, giữ lại để tham khảo:
  # run_bot(RUNS / "baseline.jsonl")
  # grade_by_code(RUNS / "baseline.jsonl")
  # grade_deepeval(RUNS / "baseline.jsonl", RUNS / "baseline_scores.jsonl")
  # grade_deepeval(RUNS / "baseline.jsonl", RUNS / "baseline_scores_gpt-5.4.jsonl", judge="gpt-5.4")

  # Buổi 19 Bài 4 — chunk theo Điều/Khoản, max 500 token (bảng law_chunks_dieu):
  RUN = RUNS / "dieu-500.jsonl"
  run_bot(RUN, table="law_chunks_dieu")  # gọi bot 30 câu (~$0.007) — chạy 1 lần rồi comment lại
  grade_by_code(RUN)  # miễn phí
