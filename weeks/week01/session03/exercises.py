import tiktoken
from dotenv import load_dotenv
from openai import Omit, OpenAI, omit
from openai.types.responses import Response, ResponseInputParam

# Load env
load_dotenv()  # nạp biến môi trường từ .env, SDK tự đọc OPENAI_API_KEY
client = OpenAI()  # tạo client, dùng key từ biến môi trường OPENAI_API_KEY

# Buổi 3 — LLM API cơ bản
#
# Luật chơi: tự viết code dưới mỗi đề bài, tra docs chính thức của SDK khi cần.
# Import cần gì tự thêm ở đầu file.
#
# Chuẩn bị (tự làm, xem hướng dẫn chi tiết ở notes.md mục "Setup"):
#   1. Cài thư viện: openai, tiktoken, python-dotenv.
#   2. Tạo file .env ở thư mục gốc chứa OPENAI_API_KEY.
#   3. Nạp key bằng python-dotenv: load_dotenv() ở đầu file.
#      SDK tự đọc OPENAI_API_KEY từ biến môi trường.
#
# Buổi này chỉ dùng OpenAI. Các mục "(Tùy chọn, khi có key Anthropic)" để dành làm sau.
#
# Chạy:     uv run python weeks/week01/session03/exercises.py
# Vệ sinh:  uv run ruff format . && uv run ruff check . --fix && uv run pyright
#
# Quan sát ở Bài 3, 4, 5 ghi vào notes.md cùng thư mục.
# Mỗi lần chạy là tốn tiền thật: dùng model rẻ nhất, prompt ngắn, max_tokens nhỏ.


# ============================================================================
# Bài 1 — Gọi chat lần đầu
# ============================================================================
#
# Yêu cầu:
#   - chat_openai(system: str, user: str) -> str
#     Dùng openai.OpenAI(), tự tra docs chọn model rẻ nhất hiện có.
#   - Trả về đúng phần text của câu trả lời, không phải cả object response.
#   - Gợi ý: system prompt được truyền như một message có role "system".
#   - Gợi ý: in thử cả object response một lần để xem cấu trúc, rồi mới lấy text.
#   - (Tùy chọn, khi có key Anthropic) viết chat_anthropic cùng chữ ký, dùng
#     anthropic.Anthropic(). So sánh xem system prompt được truyền ở đâu. Chỗ này khác nhau.


# TODO: viết code ở đây
def chat_openai(system: str, user: str) -> str:
    response = client.responses.create(
        model="gpt-6-luna",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.output_text


# ============================================================================
# Bài 2 — Hội thoại nhiều lượt: system / user / assistant
# ============================================================================
#
# Yêu cầu:
#   - chat_history(system: str, messages: list[...]) -> str, dùng OpenAI SDK.
#   - messages là cả lịch sử, xen kẽ role "user" và "assistant".
#   - Tự kiểm: lượt 1 nói "Tên mình là An", lượt 2 hỏi "Mình tên gì?".
#     Truyền đủ lịch sử thì model trả lời đúng. Chỉ truyền lượt 2 thì nó không biết.
#   - Type cho messages: SDK có sẵn type, dùng nó thay vì dict trần.
#     Responses API: ResponseInputParam (cả list input) hoặc EasyInputMessageParam
#     (1 message), import từ openai.types.responses.
#     Chat Completions API: ChatCompletionMessageParam.
#   - Điểm cần hiểu: API không nhớ gì giữa các lần gọi. "Trí nhớ" là do mình gửi lại.


# TODO: viết code ở đây
def chat_history(system: str, messages: ResponseInputParam) -> str:
    response = client.responses.create(
        model="gpt-6-luna", input=[{"role": "system", "content": system}, *messages]
    )

    return response.output_text


# ============================================================================
# Bài 3 — Nghịch params: temperature, top_p, max_output_tokens
# ============================================================================
#
# Yêu cầu:
#   - Chọn 1 prompt mở, ví dụ "Đặt 1 tên cho quán cà phê ở Đà Lạt".
#   - Chạy 3 lần với temperature=0, rồi 3 lần với temperature=1. So sánh.
#   - Chạy với max_output_tokens nhỏ, ví dụ 16 (API có thể đòi tối thiểu 16).
#     Xem câu trả lời bị cắt ra sao. In response.status và
#     response.incomplete_details để biết lý do dừng.
#     (Chat Completions API: max_tokens và finish_reason.)
#   - Thử top_p, ví dụ 0.1 và 1.0. Chỉnh temperature HOẶC top_p mỗi lần,
#     không chỉnh cả hai cùng lúc. Một số model sẽ báo lỗi nếu truyền cả hai.
#   - Ghi quan sát vào notes.md. Nối với Buổi 2: temperature tác động lên bước nào?

# TODO: viết code ở đây
#
# Khung sườn: giữ nguyên chữ ký, tự viết phần thân (thay dấu ... bằng code).
# Import cần thêm ở đầu file:
#   from openai import Omit, omit
#   from openai.types.responses import Response
#
# Vì sao dùng omit thay vì None: SDK hiểu omit là "không gửi tham số này", API sẽ dùng
# giá trị mặc định. Truyền None thì SDK gửi null lên, ý nghĩa khác.
# Dấu * trong chữ ký: các tham số phía sau bắt buộc gọi bằng tên, ví dụ temperature=0.
#
# MODEL_BAI3 = "gpt-6-luna"  # đổi sang model không suy luận nếu bị từ chối temperature
# PROMPT_BAI3 = "Đặt 1 tên cho quán cà phê ở Đà Lạt. Chỉ trả lời tên."
#
#
MODEL_BAI3 = "gpt-4o-mini"
PROMPT_BAI3 = "Đặt 1 tên cho quán cà phê ở Đà Lạt. Chỉ trả lời tên."
PROMPT_LONG = "Giới thiệu Đà Lạt trong 3 câu"  # dùng cho 3.3: câu trả lời dài hơn 16 token


def ask(
    prompt: str,
    *,
    temperature: float | Omit = omit,
    top_p: float | Omit = omit,
    max_output_tokens: int | Omit = omit,
) -> Response:
    """Gọi API 1 lần, trả về NGUYÊN response (không chỉ text)."""
    response = client.responses.create(
        model=MODEL_BAI3,
        input=prompt,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
    )
    return response


def show(label: str, response: Response) -> None:
    output_text = response.output_text
    status = response.status
    incomplete_details = response.incomplete_details
    output_tokens = response.usage.output_tokens if response.usage else "N/A"
    print(f"{label}: {output_text}")
    print(f"    Status: {status}, Incomplete: {incomplete_details}, Tokens: {output_tokens}")


def run_bai3() -> None:
    # 3.1 temperature=0, chạy 3 lần
    for _ in range(3):
        response = ask(PROMPT_BAI3, temperature=0)
        show("Temp=0", response)

    # 3.2 temperature=1, chạy 3 lần
    for _ in range(3):
        response = ask(PROMPT_BAI3, temperature=1)
        show("Temp=1", response)

    # 3.3 max_output_tokens=16, chạy 1 lần. Để ý output_text và status.
    response = ask(PROMPT_LONG, max_output_tokens=16)
    show("MaxTokens=16", response)

    # 3.4 top_p=0.1 rồi top_p=1.0, mỗi mức 3 lần
    response = ask(PROMPT_BAI3, top_p=0.1)
    show("TopP=0.1", response)

    response = ask(PROMPT_BAI3, top_p=1.0)
    show("TopP=1.0", response)

    # 3.5 (tùy chọn) truyền CẢ temperature và top_p, xem API có báo lỗi không.
    #     Bọc lời gọi trong try/except openai.BadRequestError as e, rồi in e.
    response = ask(PROMPT_BAI3, temperature=0.5, top_p=0.5)
    show("Temp=0.5, TopP=0.5", response)

    response = ask(PROMPT_BAI3, temperature=1, top_p=1)
    show("Temp=1, TopP=1", response)


# Trong main: comment lời gọi bài 1, bài 2, rồi gọi run_bai3().
# Nếu 3.1 báo lỗi "unsupported parameter": ghi vào notes.md, đổi MODEL_BAI3, chạy lại.


# ============================================================================
# Bài 4 — Đếm token bằng tiktoken, tiếng Việt vs tiếng Anh
# ============================================================================
#
# Yêu cầu:
#   - count_tokens(text: str, encoding_name: str = "o200k_base") -> int
#     Dùng tiktoken.get_encoding(...).encode(...).
#   - Chọn 3 câu tiếng Việt và bản dịch tiếng Anh tương đương.
#     In số token mỗi câu và tỉ lệ Việt / Anh.
#   - Thử thêm: câu tiếng Việt viết không dấu. Số token thay đổi thế nào?
#   - Thử decode từng token của 1 câu tiếng Việt để xem nó bị cắt ở đâu:
#     encoding.decode([token_id]) cho từng token_id.
#   - Lưu ý: tiktoken là tokenizer của OpenAI. Model của hãng khác, như Claude,
#     dùng tokenizer khác nên số token sẽ không giống.
#   - Ghi vào notes.md: vì sao tiếng Việt tốn token hơn?


# TODO: viết code ở đây
def count_token(text: str, encoding_name: str = "o200k_base") -> int:

    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    return len(tokens)


# ============================================================================
# Bài 5 — Tự tính cost của 1 request
# ============================================================================
#
# Yêu cầu:
#   - Tra bảng giá chính thức của model bạn dùng. Giá thường tính theo
#     USD cho mỗi 1 triệu token (MTok), input và output giá khác nhau.
#     Khai báo thành hằng số ở đầu bài, kèm comment ghi ngày tra giá.
#   - cost_usd(input_tokens: int, output_tokens: int,
#              price_in_per_mtok: float, price_out_per_mtok: float) -> float
#   - Gọi 1 request thật, lấy số token từ response.usage.
#     Tự in usage ra xem có những field nào.
#   - In cost của request đó, rồi ước tính: 1000 user, mỗi người 20 tin/ngày,
#     1 tháng tốn bao nhiêu?
#   - Ghi vào notes.md: input hay output đắt hơn? Prompt tiếng Việt ảnh hưởng gì?


# TODO: viết code ở đây
# Giá gpt-4o-mini, USD / 1M token, tra ngày 29/09/2026 tại developers.openai.com/api/docs/pricing
PRICE_IN_PER_MTOK = 0.15
PRICE_OUT_PER_MTOK = 0.60


def cost_usd(
    input_tokens: int, output_tokens: int, price_in_per_mtok: float, price_out_per_mtok: float
) -> float:
    return (input_tokens / 1_000_000) * price_in_per_mtok + (
        output_tokens / 1_000_000
    ) * price_out_per_mtok


if __name__ == "__main__":
    # test bài 1
    print(chat_openai("You are a helpful assistant.", "What is python?"))

    # test bài 2
    # print(chat_history("You're helpful asistant", [{"role": "user", "content": "What is my name"}]))
    # print(
    #     chat_history(
    #         "You're helpful asistant",
    #         [
    #             {"role": "user", "content": "My name is An."},
    #             {"role": "assistant", "content": "Hello An! How can I help you today?"},
    #             {"role": "user", "content": "What is my name?"},
    #         ],
    #     )
    # )

    # test bài 3
    # run_bai3()

    # test bài 4
    # pairs = [
    #     ("Xin chào, hôm nay trời đẹp quá.", "Hello, the weather is so nice today."),
    #     (
    #         "Tôi muốn đặt một bàn cho bốn người vào tối thứ Bảy.",
    #         "I would like to book a table for four people on Saturday evening.",
    #     ),
    #     (
    #         "Mô hình ngôn ngữ lớn dự đoán token tiếp theo dựa trên ngữ cảnh.",
    #         "Large language models predict the next token based on context.",
    #     ),
    # ]
    # for vi, en in pairs:
    #     print(f"VI {count_token(vi)} token | {vi}")
    #     print(f"EN {count_token(en)} token | {en}\n")

    # co_dau = "Tôi muốn đặt một bàn cho bốn người vào tối thứ Bảy."
    # khong_dau = "Toi muon dat mot ban cho bon nguoi vao toi thu Bay."
    # print(f"Có dấu:    {count_token(co_dau)} token")
    # print(f"Không dấu: {count_token(khong_dau)} token")

    # test bài 5
    # response = ask(PROMPT_BAI3)
    # usage = response.usage
    # if usage is not None:
    #     print(usage)
    #     cost = cost_usd(
    #         usage.input_tokens, usage.output_tokens, PRICE_IN_PER_MTOK, PRICE_OUT_PER_MTOK
    #     )
    #     print(f"Input: {usage.input_tokens} token | Output: {usage.output_tokens} token")
    #     print(f"Cost 1 request: ${cost:.6f}")
    #     monthly = cost * 1000 * 20 * 30
    #     print(f"Ước tính 1000 user × 20 tin/ngày × 30 ngày: ${monthly:.2f}/tháng")
