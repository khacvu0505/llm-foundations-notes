import re
import sys
from pathlib import Path

import docx

LAW_FILE = Path("projects/p2-labor-law-rag/data/raw/18-VBHN-VPQH-2026.docx")
PARAS = [p.text.strip() for p in docx.Document(str(LAW_FILE)).paragraphs]


def show_dieu(n: int) -> None:
  start = next(i for i, p in enumerate(PARAS) if p.startswith(f"Điều {n}."))
  end = next(
    (
      i
      for i in range(start + 1, len(PARAS))  # tìm Điều/Chương KẾ TIẾP, bắt đầu sau dòng tiêu đề
      if re.match(r"^(Điều \d+\.|Chương [IVXLC]+$)", PARAS[i])
    ),
    len(PARAS),  # không có Điều nào sau (Điều 220) → đọc tới cuối
  )
  print("\n".join(p for p in PARAS[start:end] if p))


if __name__ == "__main__":
  if len(sys.argv) != 2:
    sys.exit("Cách dùng: uv run python weeks/week03/session17/exercises.py <số Điều>, vd. 25")
  show_dieu(int(sys.argv[1]))
