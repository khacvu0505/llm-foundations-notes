import json
from pathlib import Path
from typing import Any

LOG_FILE = Path(__file__).parent.parent / "logs" / "cost.jsonl"


def write_cost_log(record: dict[str, Any]) -> None:
  LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
  with LOG_FILE.open("a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")
  # Claude sửa (2026-10-18) theo yêu cầu: in nội dung cost của request, dùng .get để thiếu key
  # cũng không văng lỗi (hàm này chạy trong finally của chat_events)
  ttft = record.get("ttft_ms")
  print(
    f"[cost] {record.get('status')} steps={record.get('steps')} "
    f"tools={','.join(record.get('tools', [])) or '-'} "
    f"in={record.get('input_tokens')} out={record.get('output_tokens')} "
    f"${record.get('cost_usd', 0):.6f} "
    f"ttft={f'{ttft}ms' if ttft is not None else '-'} total={record.get('latency_ms')}ms"
  )
