import asyncio
import time

import httpx2


async def bench(client: httpx2.AsyncClient, path: str) -> float:
    start = time.perf_counter()
    await asyncio.gather(*(client.get(path) for _ in range(5)))
    return time.perf_counter() - start


async def bench_chat(client: httpx2.AsyncClient, n: int = 5) -> float:
    start = time.perf_counter()
    await asyncio.gather(*(client.post("/chat", json={"message": "Xin chào"}) for _ in range(n)))
    return time.perf_counter() - start


ROUTES = ["/slow/def", "/slow/async-block", "/slow/async-await"]


async def main() -> None:
    async with httpx2.AsyncClient(base_url="http://127.0.0.1:8000", timeout=30) as client:
        for path in ROUTES:
            res = await bench(client, path)
            print(f"Path: {path}, Duration: {res}")

        seconds = await bench_chat(client, 5)
        print(f"Path: {"/chat"}, Duration: {seconds}")


if __name__:
    asyncio.run(main())
