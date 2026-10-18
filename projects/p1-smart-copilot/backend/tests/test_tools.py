# Claude viết (2026-10-18), theo yêu cầu — Bài 5: test sales_summary thuần, không qua API.
from pathlib import Path

import pytest

from app import tools

CSV = """order_id,customer,product,quantity,unit_price,status,created_at,city
1,An,Cà phê,3,10000,delivered,2026-10-02,Hà Nội
2,Bình,Trà,1,30000,delivered,2026-10-01,TP.HCM
3,Chi,Cà phê,1,10000,shipping,2026-10-01,Đà Nẵng
4,An,Trà,5,30000,cancelled,2026-10-02,Hà Nội
"""


@pytest.fixture
def small_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
  path = tmp_path / "orders.csv"
  path.write_text(CSV, encoding="utf-8")
  monkeypatch.setattr(tools, "ORDERS_CSV", path)


@pytest.mark.usefixtures("small_csv")
def test_sales_summary_by_product_excludes_cancelled() -> None:
  # status=None → mọi trạng thái TRỪ cancelled; sort doanh thu giảm dần
  assert tools.sales_summary("product", None) == [
    {"label": "Cà phê", "revenue_vnd": 40000, "order_count": 2},  # 3×10k + 1×10k
    {"label": "Trà", "revenue_vnd": 30000, "order_count": 1},  # đơn 4 (cancelled) bị loại
  ]


@pytest.mark.usefixtures("small_csv")
def test_sales_summary_by_day_sorted_ascending() -> None:
  assert tools.sales_summary("day", None) == [
    {"label": "2026-10-01", "revenue_vnd": 40000, "order_count": 2},  # đơn 2 + 3
    {"label": "2026-10-02", "revenue_vnd": 30000, "order_count": 1},  # đơn 1 (đơn 4 cancelled)
  ]


@pytest.mark.usefixtures("small_csv")
def test_sales_summary_only_cancelled() -> None:
  assert tools.sales_summary("product", "cancelled") == [
    {"label": "Trà", "revenue_vnd": 150000, "order_count": 1},
  ]
