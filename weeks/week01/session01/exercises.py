# Buổi 1 — Port TS sang Python
#
# Luật chơi: tự viết code Python dưới mỗi đề bài, KHÔNG search lời giải trước khi thử.
# Import cần gì tự thêm ở đầu file (cũng là một phần bài tập).
#
# Chạy test:   uv run pytest weeks/ -v
# Vệ sinh:     uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Vấp bẫy gì khác TS thì ghi ngay vào notes/ts-to-python-traps.md


# ============================================================================
# Bài 1 — .filter().map() → list comprehension
# ============================================================================
#
#   function evenSquares(nums: number[]): number[] {
#     return nums.filter(n => n % 2 === 0).map(n => n * n);
#   }
#
# Yêu cầu:
#   - Tên hàm: even_squares, có type hints đầy đủ (list[int] -> list[int])
#   - Body đúng 1 dòng comprehension, không dùng map()/filter() của Python

# TODO: viết code ở đây
# Cách 1: Hàm thông thường
def even_squares(nums: list[int]) -> list[int]:
    return [value ** 2 for value in nums if value % 2 == 0]



# ============================================================================
# Bài 2 — reduce → dict + generics
# ============================================================================
#
#   function groupBy<T>(items: T[], keyFn: (item: T) => string): Record<string, T[]> {
#     return items.reduce((acc, item) => {
#       const key = keyFn(item);
#       (acc[key] ??= []).push(item);
#       return acc;
#     }, {} as Record<string, T[]>);
#   }
#
# Yêu cầu:
#   - Tên hàm: group_by, dùng generics syntax mới của Python 3.12: def group_by[T](...)
#   - Type cho keyFn: Callable[[T], str] (import từ collections.abc)
#   - Gợi ý: tương đương ??= là dict.setdefault() (hoặc collections.defaultdict)

# TODO: viết code ở đây


# ============================================================================
# Bài 3 — interface + optional fields → TypedDict / dataclass / Literal
# ============================================================================
#
#   interface RawUser {                  // dữ liệu thô từ API, field có thể thiếu
#     name: string;
#     age?: number;
#     role?: "admin" | "member";
#   }
#
#   interface User {                     // dữ liệu đã chuẩn hóa
#     name: string;
#     age: number;                       // default 0
#     role: "admin" | "member";          // default "member"
#     isAdult: boolean;                  // age >= 18
#   }
#
#   function parseUser(raw: RawUser): User { ... }
#
# Yêu cầu:
#   - Khai báo type alias: Role = Literal["admin", "member"]
#   - RawUser: class kế thừa TypedDict với total=False (nghĩa là mọi key optional)
#   - User: @dataclass với 4 field đúng type (isAdult -> is_adult theo naming Python)
#   - parse_user(raw) -> User: đọc field có thể thiếu bằng raw.get(key, default),
#     tính is_adult từ age

# TODO: viết code ở đây


# ============================================================================
# Bài 4 — Promise.all → asyncio.gather
# ============================================================================
#
#   async function fetchAll(ids: string[]): Promise<string[]> {
#     return Promise.all(ids.map(id => fakeFetch(id)));
#   }
#
# Yêu cầu:
#   - fake_fetch(item_id: str) -> str: async, giả lập network bằng
#     await asyncio.sleep(0.05), return f"data:{item_id}"
#   - fetch_all(ids: list[str]) -> list[str]: các call chạy SONG SONG (gather),
#     không await tuần tự trong vòng for
#   - Tự kiểm bằng test đo thời gian (time.perf_counter()):
#     5 call × 0.05s phải xong trong < 0.15s; ~0.25s nghĩa là đang chạy tuần tự
#   - Lưu ý khi viết test: hàm test thường không async được, gọi bằng
#     asyncio.run(fetch_all([...]))

# TODO: viết code ở đây


# ============================================================================
# Bài 5 — context manager (`with`) — thứ TS không có
# ============================================================================
#
# Viết class Timer dùng được như sau:
#
#   with Timer() as t:
#       ...  # làm gì đó
#   print(t.elapsed)   # số giây đã trôi qua (float, > 0)
#
# Yêu cầu:
#   - Implement __enter__: ghi lại time.perf_counter(), return self
#   - Implement __exit__: tính self.elapsed
#   - Đây chính là pattern with open(...), with httpx.Client() dùng suốt các buổi sau

# TODO: viết code ở đây




if __name__ == "__main__":
    print(even_squares([1, 2, 3, 4, 5]))
