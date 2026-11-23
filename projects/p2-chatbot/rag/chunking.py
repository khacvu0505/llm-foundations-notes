import unicodedata
from pathlib import Path

from docx import Document

PROJECTS_DIR = Path(__file__).resolve().parents[2]
LAW_FILE = PROJECTS_DIR / "p2-labor-law-rag" / "data" / "raw" / "18-VBHN-VPQH-2026.docx"


def read_paragraphs(path: Path) -> list[str]:
  """Đọc .docx → danh sách dòng chữ (bỏ dòng rỗng)."""
  lines = []
  # 1. Document(path)
  doc = Document(str(path))

  for p in doc.paragraphs:
    text = unicodedata.normalize("NFC", p.text).strip()  # 2. duyệt doc.paragraphs → p.text
    if text:
      lines.append(text)
  return lines


if __name__ == "__main__":
  lines = read_paragraphs(LAW_FILE)
  print(len(lines))  # mong đợi 1377
  for line in lines[:20]:
    print(line[:80])
