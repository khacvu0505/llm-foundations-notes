import hashlib
import re
import unicodedata
from pathlib import Path

import docx
import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")
LAW_FILE = Path(__file__).resolve().parent / "data" / "raw" / "18-VBHN-VPQH-2026.docx"
INTERNAL_FILE = LAW_FILE.parent / "internal" / "noi-quy-abc.md"

DIEU_RE = re.compile(r"^Điều \d+\. ")  # dòng tiêu đề Điều: "Điều 25. Thời gian thử việc"
KHOAN_RE = re.compile(r"^\d+\. ")  # dòng mở đầu Khoản: "1. Không quá 180 ngày…"


def read_paragraphs(path: Path) -> list[str]:
  paras = []
  for p in docx.Document(str(path)).paragraphs:
    t = " ".join(unicodedata.normalize("NFC", p.text).split())  # NFC + gộp khoảng trắng (Buổi 15)
    if t:
      paras.append(t)
  return paras[paras.index("Chương I") :]  # bỏ đi phần đầu tiên (Chương]


def clean_line(p: str) -> str:
  return re.sub(r"^(\d+)\.\d+ ", r"\1. ", p)


def is_structure_line(p: str) -> bool:
  """Dòng Chương / Mục / tên chương (VIẾT HOA) — không thuộc nội dung Điều nào."""
  if re.match(r"^(Chương [IVXLC]+|Mục \d+)$", p):
    return True
  return p == p.upper() and any(ch.isalpha() for ch in p)


def group_by_dieu(paras: list[str]) -> list[tuple[str, list[str]]]:
  """[(tiêu đề Điều, [các dòng nội dung]), …]"""
  groups: list[tuple[str, list[str]]] = []
  for p in paras:
    p = clean_line(p)
    if is_structure_line(p):
      continue
    if DIEU_RE.match(p):
      groups.append((p, []))  # mở 1 Điều mới: tiêu đề + danh sách nội dung rỗng
    elif groups:
      groups[-1][1].append(p)  # thêm dòng vào nội dung của Điều đang mở
  return groups


def n_tokens(text: str) -> int:
  return len(ENC.encode(text))


def split_into_units(body: list[str]) -> list[str]:
  """Gom dòng thành Khoản: dòng '1.', '2.'… mở Khoản mới; điểm a), b)… đi theo Khoản đang mở."""
  units: list[list[str]] = []
  for line in body:
    if KHOAN_RE.match(line) or not units:  # dòng Khoản mới, hoặc dòng đầu tiên (phần mở đầu)
      units.append([line])
    else:
      units[-1].append(line)
  return ["\n".join(u) for u in units]


def split_dieu(heading: str, body: list[str], max_tokens: int = 500) -> list[str]:
  whole = heading + "\n" + "\n".join(body)
  if n_tokens(whole) <= max_tokens:
    return [whole]  # Điều ngắn: trọn 1 chunk
  chunks: list[str] = []
  current: list[str] = []
  for unit in split_into_units(body):
    candidate = heading + "\n" + "\n".join(current + [unit])
    if current and n_tokens(candidate) > max_tokens:  # thêm Khoản này thì vượt cỡ
      chunks.append(heading + "\n" + "\n".join(current))  # đóng chunk đang gom (có tiêu đề ở đầu)
      current = [unit]  # chunk mới bắt đầu bằng Khoản này
    else:
      current.append(unit)
  if current:
    chunks.append(heading + "\n" + "\n".join(current))
  return chunks


def read_markdown(path: Path) -> list[str]:
  """Nội quy giả (Buổi 15): bỏ '**', dòng tiêu đề '#', khung cảnh báo '>', dòng kẻ bảng '|---|'."""
  lines = []
  for raw in path.read_text(encoding="utf-8").splitlines():
    t = " ".join(unicodedata.normalize("NFC", raw).replace("**", "").split())
    if not t or t.startswith(("#", ">")) or set(t) <= set("|- "):
      continue
    lines.append(t)
  return lines


def build_records(
  doc_id: str,
  source: Path,
  groups: list[tuple[str, list[str]]],
  allowed_groups: list[str],
  max_tokens: int = 500,
) -> list[dict]:
  records: list[dict] = []
  for heading, body in groups:
    for content in split_dieu(heading, body, max_tokens):
      records.append(
        {
          "doc_id": doc_id,
          "chunk_index": len(records),  # 0, 1, 2… theo thứ tự trong tài liệu
          "source": str(source),
          "heading": heading,  # tiêu đề Điều ĐẦY ĐỦ (không còn cụt như Buổi 16)
          "content": content,
          "content_hash": hashlib.sha256(content.encode()).hexdigest(),
          "allowed_groups": allowed_groups,
        }
      )
  return records


def segment_text(text: str) -> str:
  """Buổi 21 Bài 3: tách từ tiếng Việt cho tìm từ khoá.

  underthesea gộp âm tiết thành từ ("lao_động"), nhưng parser 'simple' của Postgres coi '_'
  là DẤU TÁCH (ts_debug: lao | _ | động) → nối LIỀN ("laođộng") để giữ nguyên 1 từ.
  Áp dụng cho cả chunk lẫn câu hỏi.
  """
  from underthesea import word_tokenize  # import chậm (tải model) → chỉ khi thật sự dùng

  joined = word_tokenize(unicodedata.normalize("NFC", text), format="text")
  if not isinstance(joined, str):  # format="text" trả str; kiểu khai báo của thư viện là str | list
    joined = " ".join(joined)
  return joined.replace("_", "")


if __name__ == "__main__":
  chunks = [c for h, b in group_by_dieu(read_paragraphs(LAW_FILE)) for c in split_dieu(h, b)]
  lens = sorted(n_tokens(c) for c in chunks)
  print(
    "Số chunk:", len(chunks), "| token min/median/max:", lens[0], lens[len(lens) // 2], lens[-1]
  )
  print("Chunk vượt 500:", sum(n > 500 for n in lens))
