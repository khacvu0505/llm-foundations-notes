import asyncio
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

load_dotenv()  # load .env, có OPENAI_API_KEY

# Buổi 4 — Async + Streaming
#
# Luật chơi: tự viết code dưới mỗi đề bài, tra docs chính thức của SDK khi cần.
# Import cần gì tự thêm ở đầu file.
#
# Chuẩn bị: không cần cài thêm thư viện. Dùng lại .env và openai từ Buổi 3.
#   - Client đồng bộ:    OpenAI()       (Buổi 3)
#   - Client bất đồng bộ: AsyncOpenAI()  (buổi này) — cùng API, nhưng mọi lời gọi phải await
#
# Chạy:     uv run python weeks/week01/session04/exercises.py
# Vệ sinh:  uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Quan sát ghi vào notes.md cùng thư mục.
# Mỗi lần chạy là tốn tiền thật: prompt ngắn, model rẻ (gpt-4o-mini), chạy từng bài một.
#
# Nhắc lại từ Buổi 1 bài 4: coroutine không tự chạy khi tạo (khác Promise);
# asyncio.gather(*list) chạy song song; code thường gọi hàm async bằng asyncio.run(...).


# ============================================================================
# Bài 1 — Gọi LLM bằng client bất đồng bộ
# ============================================================================
#
# Yêu cầu:
#   - async def achat(prompt: str, model: str = "gpt-4o-mini") -> str
#     Dùng AsyncOpenAI (tạo 1 client ở cấp module, như Buổi 3), await responses.create(...),
#     trả về output_text.
#   - Gọi thử 1 lần trong main bằng asyncio.run(...).
#   - So sánh với Buổi 3: code gần như y hệt, chỉ khác client và chữ await.
#     Bên TS: SDK Node vốn đã là async, nên đây là chỗ Python khác TS.

# TODO: viết code ở đây


client = AsyncOpenAI()  # tạo 1 client bất đồng bộ ở cấp module


async def achat(prompt: str, model: str = "gpt-4o-mini") -> str:
    response = await client.responses.create(model=model, input=prompt)
    return response.output_text


# ============================================================================
# Bài 2 — Gọi song song vs tuần tự (Promise.all của LLM)
# ============================================================================
#
# Yêu cầu:
#   - 3 prompt ngắn khác nhau, ví dụ: đặt tên quán cà phê / trà sữa / tiệm bánh.
#   - async def run_sequential(prompts: list[str]) -> list[str]: await từng cái trong vòng for.
#   - async def run_parallel(prompts: list[str]) -> list[str]: dùng asyncio.gather.
#   - Đo thời gian cả hai bằng time.perf_counter() (hoặc chép class Timer từ Buổi 1 bài 5).
#   - Ghi vào notes.md: tuần tự mất bao lâu, song song mất bao lâu, vì sao.
#   - Dự đoán trước khi chạy: song song ≈ thời gian của lời gọi CHẬM NHẤT, không phải tổng.


# TODO: viết code ở đây
async def run_sequential(prompts: list[str]) -> list[str]:
    results: list[str] = []
    for prompt in prompts:
        result = await achat(prompt)
        results.append(result)
    return results


async def run_parallel(prompts: list[str]) -> list[str]:
    tasks = [achat(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return results


async def main():
    prompts = [
        "Đặt tên quán cà phê ở Đà Lạt. Chỉ cần tên quán",
        "Đặt tên quán trà sữa ở Đà Lạt. Chỉ cần tên quán",
        "Đặt tên tiệm bánh ở Đà Lạt. Chỉ cần tên tiệm",
    ]
    start_time = time.perf_counter()
    await run_sequential(prompts)
    end_time = time.perf_counter()
    print(f"Sequential time: {end_time - start_time:.2f} seconds")

    start_time2 = time.perf_counter()
    await run_parallel(prompts)
    end_time2 = time.perf_counter()
    print(f"Parallel time: {end_time2 - start_time2:.2f} seconds")


# ============================================================================
# Bài 3 — Streaming: in từng mảnh text ra terminal
# ============================================================================
#
# Yêu cầu:
#   - def stream_chat(prompt: str) -> None, dùng client ĐỒNG BỘ OpenAI() cho dễ trước.
#   - Truyền stream=True vào responses.create(...). Kết quả là một stream các SỰ KIỆN (event),
#     không phải một response. Duyệt bằng vòng for.
#   - Mỗi event có field type. Hai loại cần dùng:
#       "response.output_text.delta" → event.delta là 1 mảnh text mới
#       "response.completed"         → event.response là response đầy đủ, có usage
#   - In từng mảnh liền nhau trên cùng 1 dòng: print(..., end="", flush=True).
#     Thử bỏ flush=True xem có khác gì không.
#   - Đo 2 con số:
#       TTFT (time to first token): từ lúc gọi đến lúc nhận mảnh text đầu tiên
#       Tổng thời gian: đến lúc nhận event "response.completed"
#   - Dùng prompt dài vừa phải để thấy rõ, ví dụ "Giới thiệu Đà Lạt trong 5 câu".
#   - Gợi ý: in thử event.type của mọi event 1 lần để xem stream có những loại nào.

# TODO: viết code ở đây
client2 = OpenAI()


def stream_chat(prompt: str) -> None:
    ttft: float | None = None  # chưa nhận mảnh nào
    start = time.perf_counter()
    stream = client2.responses.create(model="gpt-6-luna", input=prompt, stream=True)
    for event in stream:
        if event.type == "response.output_text.delta":
            if ttft is None:  # chỉ mảnh đầu tiên mới gán
                ttft = time.perf_counter() - start
            print(event.delta, end="", flush=True)
        elif event.type == "response.completed":
            total = time.perf_counter() - start
            print()  # xuống dòng sau đoạn text
            print(f"TTFT: {ttft:.2f} seconds")
            print(f"Total time: {total:.2f} seconds")
            print(f"Usage: {event.response.usage}")


# ============================================================================
# Bài 4 — Streaming bất đồng bộ
# ============================================================================
#
# Yêu cầu:
#   - async def astream_chat(prompt: str) -> str: như Bài 3 nhưng dùng AsyncOpenAI.
#     Lời gọi create phải await, và duyệt stream bằng "async for" thay cho "for".
#   - Vừa in từng mảnh, vừa gom lại thành chuỗi đầy đủ rồi return.
#   - Bên TS: giống for await (const chunk of stream). Đây là nền cho Buổi 9 (SSE về Next.js).


# TODO: viết code ở đây
async def astream_chat(prompt: str) -> str:
    stream = await client.responses.create(model="gpt-6-luna", input=prompt, stream=True)
    text = ""
    async for event in stream:
        if event.type == "response.output_text.delta":
            text += event.delta
            print(event.delta, end="", flush=True)
    print()  # xuống dòng sau đoạn text
    return text


# ============================================================================
# Bài 5 — Mini exercise: 3 model song song, so sánh latency + cost
# ============================================================================
#
# Yêu cầu:
#   - Chọn 3 model, ví dụ gpt-4.1-nano, gpt-4o-mini, gpt-4.1-mini (đều nhận temperature).
#     Có thể thay 1 model bằng gpt-6-luna để thấy model có suy luận chậm/đắt thế nào.
#   - Tra giá input/output từng model (USD / 1M token), khai báo thành dict hằng số,
#     comment ghi ngày tra. Nguồn: developers.openai.com/api/docs/pricing
#   - async def measure(model: str, prompt: str) -> dict (hoặc dataclass, như Buổi 1):
#     đo latency của 1 lời gọi, lấy input/output token từ usage, tính cost bằng công thức Buổi 3.
#   - Chạy cả 3 model cùng lúc bằng asyncio.gather, cùng 1 prompt.
#   - In bảng: model | latency | input token | output token | cost.
#   - (Tùy chọn) đo TTFT từng model bằng streaming, vì TTFT quyết định cảm giác "nhanh" trên UI.
#   - Ghi bảng vào notes.md: model nào nhanh nhất, rẻ nhất, câu trả lời nào tốt nhất?

# TODO: viết code ở đây

# Giá USD / 1M token (input, output), tra ngày 2026-09-30
# Nguồn: developers.openai.com/api/docs/pricing
PRICES: dict[str, tuple[float, float]] = {
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-6-luna": (0.10, 0.50),
}


@dataclass
class Measurement:
    model: str
    latency: float
    input_tokens: int
    output_tokens: int
    cost: float
    text: str


def cost_usd(
    input_tokens: int, output_tokens: int, price_in_per_mtok: float, price_out_per_mtok: float
) -> float:
    return (input_tokens / 1_000_000) * price_in_per_mtok + (
        output_tokens / 1_000_000
    ) * price_out_per_mtok


async def measure(model: str, prompt: str) -> Measurement:
    start = time.perf_counter()
    response = await client.responses.create(model=model, input=prompt)
    latency = time.perf_counter() - start

    usage = response.usage
    input_tokens = usage.input_tokens if usage else 0
    output_tokens = usage.output_tokens if usage else 0
    price_in, price_out = PRICES[model]
    cost = cost_usd(input_tokens, output_tokens, price_in, price_out)

    return Measurement(model, latency, input_tokens, output_tokens, cost, response.output_text)


async def compare_models(prompt: str) -> None:
    start = time.perf_counter()
    results = await asyncio.gather(*[measure(model, prompt) for model in PRICES])
    total = time.perf_counter() - start

    print(f"{'model':<15} | {'latency':>8} | {'input':>6} | {'output':>6} | {'cost':>10}")
    print("-" * 57)
    for r in results:
        print(
            f"{r.model:<15} | {r.latency:>7.2f}s | {r.input_tokens:>6} | "
            f"{r.output_tokens:>6} | ${r.cost:>9.6f}"
        )
    print(f"\nTổng thời gian (gather): {total:.2f}s")

    for r in results:
        print(f"\n--- {r.model} ---\n{r.text}")


if __name__ == "__main__":
    # test bài 1
    # prompt = "Viết 1 khổ thơ lục bát ngắn về mùa xuân"
    # response_text = asyncio.run(achat(prompt))
    # print("Response:", response_text)

    # test bài 2
    # asyncio.run(main())

    # test bài 3
    # stream_chat("Giới thiệu Đà Lạt trong 5 câu")

    # test bài 4
    # full_text = asyncio.run(astream_chat("Giới thiệu Đà Lạt trong 5 câu"))
    # print(f"Returned: {len(full_text)} ký tự")

    # test bài 5
    asyncio.run(compare_models("Giới thiệu Đà Lạt trong 5 câu"))
