from dotenv import load_dotenv

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

# TODO: viết code ở đây


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
    pass
