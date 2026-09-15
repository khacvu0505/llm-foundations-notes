# Câu lệnh tooling hằng ngày (uv / ruff / pyright / pytest)

Điểm chung: mọi tool đều chạy qua `uv run <tool>` — tool nằm trong `.venv/` của
project chứ không cài global. `uv run` giống `npx` / `pnpm exec` bên TS.

## ruff — lint & format (ESLint + Prettier gộp một)

```bash
uv run ruff check .            # lint toàn project (như eslint .)
uv run ruff check . --fix      # lint + tự sửa lỗi sửa được (import thừa, sort import...)
uv run ruff format .           # format code (như prettier --write)
uv run ruff format . --check   # chỉ kiểm tra format, không sửa (dùng cho CI)
```

## pyright — type check (tsc --noEmit của Python)

```bash
uv run pyright                 # check toàn project
uv run pyright weeks/          # chỉ check 1 folder/file cụ thể
```

## pytest — test

```bash
uv run pytest                  # chạy toàn bộ test (tự tìm file test_*.py)
uv run pytest -v               # verbose: hiện tên + kết quả từng test
uv run pytest weeks/week01/    # chỉ chạy test trong 1 folder
uv run pytest -k group_by      # chỉ chạy test có tên chứa "group_by"
```

## Chạy code thường

```bash
uv run python file.py          # chạy 1 file
uv run python                  # mở REPL (thử nhanh syntax rất tiện)
```

## Workflow điển hình

Sửa code → `uv run pytest -v` xem đỏ/xanh → trước khi chốt, chạy 3 lệnh vệ sinh:

```bash
uv run ruff format . && uv run ruff check . --fix && uv run pyright
```
