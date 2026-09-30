# Buổi 5 — Ghi chú quan sát

## Setup (tự làm)

- [ ] **Khai báo pydantic trong `pyproject.toml`.** Pydantic đã có sẵn trong môi trường vì `openai` phụ thuộc vào nó,
      nhưng code của mình import trực tiếp thì nên khai báo trực tiếp. Dùng `uv add` như Buổi 3.
      Giống bên Node: dùng `zod` thì phải có `zod` trong `package.json`, không dựa vào việc thư viện khác kéo về.
- [ ] **Kiểm:** mở `pyproject.toml`, thấy `pydantic` trong mục `dependencies`. Chạy `uv tree --depth 1` để thấy nó
      đứng ngang hàng với `openai`.

## Bài 1 — Pydantic vs Zod

| Input | Kết quả | Ghi chú |
|---|---|---|
| dict hợp lệ | | |
| thiếu name | | |
| age = -5 | | |
| age = "25" | | |
| age = "hai lăm" | | |

Bật `strict=True` thì sao:

-

## Bài 2 — Schema đơn hàng

-

## Bài 3 — Structured output

Kết quả với tin nhắn mẫu:

Tin nhắn không phải đơn hàng thì model trả gì:

-

## Bài 4 — Retry + fallback

Chọn fallback nào, vì sao:

-

## Bài 5 — 10 tin nhắn

| Chỉ số | Giá trị |
|---|---|
| Pass ngay lần đầu | |
| Pass sau retry | |
| Fallback | |
| Đúng thật (tự kiểm bằng mắt) | |
| Tổng token | |
| Tổng cost | |

Tin nào khó nhất, vì sao:

-
