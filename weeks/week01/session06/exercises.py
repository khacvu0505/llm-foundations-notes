from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import ResponseInputParam

load_dotenv()  # load .env, có OPENAI_API_KEY

# Buổi 6 — CLI Chatbot (phần code của buổi; phần lý thuyết ở notes.md cùng thư mục)
#
# Luật chơi: tự viết code dưới mỗi đề bài, tra docs chính thức của SDK khi cần.
# Import cần gì tự thêm ở đầu file.
# Code thuần tay, KHÔNG framework (không LangChain...). Đây là nền cho mọi thứ sau này.
#
# Chuẩn bị: không cần cài thêm thư viện. openai, tiktoken, python-dotenv đã có từ Buổi 3.
#
# Chạy:     uv run python weeks/week01/session06/exercises.py
# Vệ sinh:  uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Quan sát ghi vào notes.md cùng thư mục.
# Mỗi lượt chat là tốn tiền thật: dùng gpt-4o-mini, câu ngắn. Muốn thấy sliding window
# chạy sớm thì hạ ngưỡng token xuống thấp (ví dụ 300) thay vì gõ thật nhiều lượt.
#
# Nhắc lại từ các buổi trước:
#   - API không nhớ gì giữa các lần gọi, "trí nhớ" là do mình gửi lại lịch sử (Buổi 3 bài 2).
#   - Lịch sử: ResponseInputParam, xen kẽ role "user" / "assistant" (Buổi 3, Buổi 5 bài 4).
#   - Token + cost: response.usage, PRICES + cost_usd (Buổi 4 bài 5, Buổi 5 bài 5).
#   - Đếm token offline: tiktoken, encoding "o200k_base" (Buổi 3 bài 4).
#   - Streaming: stream=True, event response.output_text.delta, print(..., flush=True) (Buổi 4).
#
# Gợi ý thiết kế: tách phần "1 lượt chat" ra hàm riêng, nhận lịch sử + câu của user, trả câu
# trả lời (và usage). Vòng lặp input() chỉ gọi hàm đó. Nhờ vậy test được bằng list câu viết sẵn,
# không phải gõ tay mỗi lần.


# ============================================================================
# Bài 1 — Vòng lặp chat có lịch sử
# ============================================================================
#
# Yêu cầu:
#   - Vòng lặp: input("Bạn: ") → gửi CẢ lịch sử lên API → in "Bot: <trả lời>" → lặp lại.
#   - Sau mỗi lượt, thêm cả câu user lẫn câu trả lời của bot vào lịch sử.
#   - Gõ /exit (hoặc Ctrl+D / Ctrl+C) thì thoát gọn, không in traceback.
#     Gợi ý: input() ném EOFError khi Ctrl+D, KeyboardInterrupt khi Ctrl+C.
#   - Tự kiểm: lượt 1 "Tên mình là An", vài lượt sau hỏi "Mình tên gì?" → bot phải nhớ.
#   - (Tùy chọn) In câu trả lời bằng streaming như Buổi 4 bài 3.

client = OpenAI()
MODEL = "gpt-6-luna"


def chat_turn(history: ResponseInputParam, user_input: str) -> str:
    # Biến dùng để tích lũy toàn bộ câu trả lời từ stream
    full_response = ""
    stream = client.responses.create(
        model=MODEL,
        input=history + [{"role": "user", "content": user_input}],
        stream=True,
    )
    print("Bot: ", end="", flush=True)
    for event in stream:
        if event.type == "response.output_text.delta":
            content = event.delta  # Lấy nội dung text vừa đổ về
            print(content, end="", flush=True)
            full_response += content
    print()
    return full_response


def bai1_run() -> None:
    history: ResponseInputParam = []
    print("Bắt đầu trò chuyện với OpenAI Responses API (Gõ '/exit' để thoát)")
    try:
        while True:
            user_msg = input("Bạn: ").strip()
            if user_msg == "/exit":
                break
            if user_msg == "":
                continue
            reply = chat_turn(history, user_msg)
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": reply})

    except (EOFError, KeyboardInterrupt):
        print()

    print("Kết thúc trò chuyện với OpenAI Responses API")


# ============================================================================
# Bài 2 — System prompt tùy chỉnh + lệnh điều khiển
# ============================================================================
#
# Yêu cầu:
#   - System prompt mặc định (ví dụ "Bạn là trợ lý trả lời ngắn gọn bằng tiếng Việt").
#   - Lệnh trong lúc chat:
#       /system <nội dung>   đổi system prompt
#       /reset               xóa lịch sử, giữ system prompt
#       /history             in lịch sử hiện tại (mỗi lượt 1 dòng, cắt ngắn nếu dài)
#   - Câu bắt đầu bằng "/" mà không phải lệnh đã biết → báo "lệnh không hợp lệ", KHÔNG gửi lên API.
#   - Câu hỏi để tự trả lời (ghi notes.md): Responses API có tham số instructions riêng.
#     Đặt system prompt ở instructions hay làm 1 message role "system" trong lịch sử thì khác gì?
#     Đổi /system giữa chừng thì những lượt cũ có bị ảnh hưởng không?
#   - Thử: /system "Trả lời như cướp biển" giữa cuộc hội thoại, xem giọng văn đổi ngay không.

# TODO: viết code ở đây


def chat_turn_with_system(
    history: ResponseInputParam,
    user_input: str,
    system: str,
) -> str:

    stream = client.responses.create(
        model=MODEL,
        instructions=system,
        input=history + [{"role": "user", "content": user_input}],
        stream=True,
    )
    full_response = ""
    print("Bot: ", end="", flush=True)
    for event in stream:
        if event.type == "response.output_text.delta":
            content = event.delta
            full_response += content
            print(content, end="", flush=True)
    print()
    return full_response


def bai2_run() -> None:
    history: ResponseInputParam = []
    print(
        "Bắt đầu trò chuyện với OpenAI Responses API"
        " (Gõ '/exit' để thoát)\n"
        " (Gõ '/system <nội dung>' để đổi system prompt)\n"
        " (Gõ '/reset' để xóa lịch sử)\n"
        " (Gõ '/history' để in lịch sử)\n"
    )

    system: str = "Bạn là trợ lý trả lời chính xác và ngắn gọn bằng tiếng Việt"
    cmd = {"/reset", "/history", "/exit"}
    try:
        while True:
            user_msg = input("Bạn: ").strip()
            if not user_msg:
                continue
            if user_msg.startswith("/") and user_msg not in cmd:
                if user_msg.startswith("/system "):
                    system = user_msg[len("/system ") :].strip()
                    print("Đã đổi system prompt.")
                else:
                    print("lệnh không hợp lệ, thử lệnh khác ")
                continue

            match user_msg:
                case "/exit":
                    break
                case "/reset":
                    history = []
                    print("Đã xóa lịch sử.")
                case "/history":
                    if not history:
                        print("(lịch sử trống)")
                    for i, m in enumerate(history, start=1):
                        text = str(m.get("content", "")).replace("\n", " ")
                        if len(text) > 60:
                            text = text[:60] + "..."
                        print(f"{i}. {m.get('role')}: {text}")
                case _:
                    reply = chat_turn_with_system(history, user_msg, system)
                    history.append({"role": "user", "content": user_msg})
                    history.append({"role": "assistant", "content": reply})

    except (EOFError, KeyboardInterrupt):
        print()

    print("Kết thúc trò chuyện với OpenAI Responses API")


# ============================================================================
# Bài 3 — Token / cost tracker
# ============================================================================
#
# Yêu cầu:
#   - Sau mỗi lượt in 1 dòng: input token, output token, cost của lượt đó, tổng cost từ đầu phiên.
#     Lấy số từ response.usage. Giá: chép PRICES + cost_usd từ Buổi 5 (tra giá theo model).
#   - Lệnh /stats: in số lượt, tổng input token, tổng output token, tổng cost.
#   - Gõ 6–8 lượt, ghi bảng "lượt → input token" vào notes.md.
#     Input token tăng thế nào qua từng lượt? Vì sao? Lượt thứ 20 sẽ tốn bao nhiêu so với lượt 1?
#   - Ước tính: nếu không làm gì, hội thoại 100 lượt tốn bao nhiêu? Bao giờ thì tràn context window?


# TODO: viết code ở đây

# Giá USD / 1M token (input, output), tra ngày 2026-09-30 (chép từ Buổi 5)
# Nguồn: developers.openai.com/api/docs/pricing
PRICES: dict[str, tuple[float, float]] = {
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-6-luna": (0.10, 0.50),
}


def cost_usd(
    input_tokens: int, output_tokens: int, price_in_per_mtok: float, price_out_per_mtok: float
) -> float:
    return (input_tokens / 1_000_000) * price_in_per_mtok + (
        output_tokens / 1_000_000
    ) * price_out_per_mtok


@dataclass
class TurnResult:
    reply: str
    input_tokens: int
    output_tokens: int


def chat_turn_with_usage(
    history: ResponseInputParam,
    user_input: str,
    system: str,
) -> TurnResult:
    stream = client.responses.create(
        model=MODEL,
        instructions=system,
        input=history + [{"role": "user", "content": user_input}],
        stream=True,
    )
    print("Bot: ", end="", flush=True)
    full_response = ""
    input_tokens = 0
    output_tokens = 0

    for event in stream:
        if event.type == "response.output_text.delta":
            content = event.delta
            full_response += content
            print(content, end="", flush=True)
        elif event.type == "response.completed":
            usage = event.response.usage
            input_tokens = usage.input_tokens if usage else 0
            output_tokens = usage.output_tokens if usage else 0

    print()

    return TurnResult(reply=full_response, input_tokens=input_tokens, output_tokens=output_tokens)


def bai3_run() -> None:
    history: ResponseInputParam = []
    print(
        "Bắt đầu trò chuyện với OpenAI Responses API"
        " (Gõ '/exit' để thoát)\n"
        " (Gõ '/system <nội dung>' để đổi system prompt)\n"
        " (Gõ '/reset' để xóa lịch sử)\n"
        " (Gõ '/history' để in lịch sử)\n"
        " (Gõ '/stats' để xem tổng token và cost)\n"
    )

    system: str = "Bạn là trợ lý trả lời chính xác và ngắn gọn bằng tiếng Việt"
    cmd = {"/reset", "/history", "/exit", "/stats"}
    price_in, price_out = PRICES[MODEL]
    turns = 0
    total_input = 0
    total_output = 0
    total_cost = 0.0
    try:
        while True:
            user_msg = input("Bạn: ").strip()
            if not user_msg:
                continue
            if user_msg.startswith("/") and user_msg not in cmd:
                if user_msg.startswith("/system "):
                    system = user_msg[len("/system ") :].strip()
                    print("Đã đổi system prompt.")
                else:
                    print("lệnh không hợp lệ, thử lệnh khác ")
                continue

            match user_msg:
                case "/exit":
                    break
                case "/reset":
                    # Chỉ xóa lịch sử, số liệu /stats tính từ đầu phiên nên giữ nguyên
                    history = []
                    print("Đã xóa lịch sử (số liệu /stats vẫn giữ).")
                case "/history":
                    if not history:
                        print("(lịch sử trống)")
                    for i, m in enumerate(history, start=1):
                        text = str(m.get("content", "")).replace("\n", " ")
                        if len(text) > 60:
                            text = text[:60] + "..."
                        print(f"{i}. {m.get('role')}: {text}")
                case "/stats":
                    print(
                        f"Số lượt: {turns} | Tổng input: {total_input} token"
                        f" | Tổng output: {total_output} token | Tổng cost: ${total_cost:.6f}"
                    )
                case _:
                    result = chat_turn_with_usage(history, user_msg, system)
                    history.append({"role": "user", "content": user_msg})
                    history.append({"role": "assistant", "content": result.reply})

                    turn_cost = cost_usd(
                        result.input_tokens, result.output_tokens, price_in, price_out
                    )
                    turns += 1
                    total_input += result.input_tokens
                    total_output += result.output_tokens
                    total_cost += turn_cost
                    print(
                        f"[lượt {turns}] in: {result.input_tokens} | out: {result.output_tokens}"
                        f" | cost: ${turn_cost:.6f} | tổng: ${total_cost:.6f}"
                    )

    except (EOFError, KeyboardInterrupt):
        print()

    print("Kết thúc trò chuyện với OpenAI Responses API")


# ============================================================================
# Bài 4 — Sliding window cho lịch sử
# ============================================================================
#
# Yêu cầu:
#   - Hằng số MAX_HISTORY_TOKENS (roadmap gợi ý 2000; lúc test hạ xuống ~300 cho nhanh thấy).
#   - Trước khi gửi: nếu tổng token của lịch sử vượt ngưỡng → bỏ lượt CŨ NHẤT, lặp lại tới khi
#     dưới ngưỡng. System prompt luôn được giữ.
#   - Bỏ theo CẶP (user + assistant), không bỏ lẻ 1 message. Tự nghĩ: bỏ lẻ thì hỏng gì?
#   - Đếm token bằng tiktoken (offline, trước khi gửi). So con số tiktoken đếm với
#     usage.input_tokens mà API báo: lệch bao nhiêu, vì sao lệch?
#   - Mỗi lượt in: token lịch sử TRƯỚC và SAU khi cắt, số lượt bị bỏ.
#   - Tự kiểm: "Tên mình là An" ở lượt 1, chat tiếp cho tới khi lượt 1 bị cắt, rồi hỏi
#     "Mình tên gì?". Bot còn nhớ không? Ghi lại.

# TODO: viết code ở đây


# ============================================================================
# Bài 5 — So sánh: tóm tắt lượt cũ thay vì bỏ hẳn
# ============================================================================
#
# Yêu cầu:
#   - Cách 2: khi vượt ngưỡng, gọi LLM tóm tắt các lượt cũ thành 1 đoạn ngắn, thay các lượt đó
#     bằng 1 message chứa bản tóm tắt; giữ nguyên vài lượt gần nhất.
#   - Chạy CÙNG một kịch bản (list câu viết sẵn, ~10 lượt, có "Tên mình là An" ở đầu và câu hỏi
#     lại ở cuối) cho cả 2 cách: sliding window và tóm tắt.
#   - So sánh và ghi bảng vào notes.md:
#       tổng token, tổng cost (nhớ tính cả lời gọi tóm tắt), bot có nhớ tên không, độ trễ.
#   - Câu hỏi: tóm tắt đặt ở đâu trong lịch sử, role gì? Khi nào nên dùng cách nào?

# TODO: viết code ở đây


if __name__ == "__main__":
    # bai1_run()

    # bai2_run()

    bai3_run()
