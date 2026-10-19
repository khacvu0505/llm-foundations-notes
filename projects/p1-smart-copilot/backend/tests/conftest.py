# Claude viết (2026-10-18), theo yêu cầu — Bài 5.
# pytest tự nạp file này; fixture autouse chạy quanh MỌI test (~ beforeEach + afterEach).
from collections.abc import Iterator
from pathlib import Path

import pytest

from app import cost_log, rate_limit
from app.main import app


@pytest.fixture(autouse=True)
def isolate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
  """Cô lập state dùng chung giữa các test, trả về đường dẫn file cost log tạm."""
  rate_limit._hits.clear()  # bộ đếm rate limit (dict cấp module) không cộng dồn qua test
  log_file = tmp_path / "cost.jsonl"
  monkeypatch.setattr(cost_log, "LOG_FILE", log_file)  # không ghi vào logs/cost.jsonl thật
  yield log_file
  app.dependency_overrides.clear()  # chạy cả khi test fail
  rate_limit._hits.clear()
