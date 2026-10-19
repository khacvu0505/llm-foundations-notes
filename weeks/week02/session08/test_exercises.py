import os

from exercises import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health() -> None:
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "ok"}


# --- Claude viết (2026-10-11), theo yêu cầu ---


def test_orders_filter_by_customer() -> None:
  response = client.get("/orders", params={"customer": "An"})
  assert response.status_code == 200
  body = response.json()
  assert body["total"] == 5
  assert {order["customer"] for order in body["orders"]} == {"An"}


def test_order_invalid_id() -> None:
  response = client.get("/orders/abc")
  assert response.status_code == 422
  assert response.json()["detail"][0]["loc"] == ["path", "order_id"]


def test_order_not_found() -> None:
  response = client.get("/orders/9999")
  assert response.status_code == 404
  assert response.json() == {"detail": "Order 9999 not found"}


def test_chat_missing_api_key() -> None:
  response = client.post("/chat", json={"message": "hi"})
  assert response.status_code == 401
  assert response.json() == {"detail": "Missing API Key"}


def test_chat_empty_message() -> None:
  api_key = os.getenv("APP_API_KEY")
  assert api_key is not None, "APP_API_KEY chưa có trong .env"
  response = client.post("/chat", json={"message": ""}, headers={"X-API-Key": api_key})
  assert response.status_code == 422
  assert response.json()["detail"][0]["type"] == "string_too_short"
