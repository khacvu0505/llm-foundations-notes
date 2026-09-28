# Buổi 2 — Lý thuyết trực giác #1: Transformer

Luật chơi: xem video xong mới viết, viết bằng lời của mình, không copy câu chữ từ video.

## 1. Xem (~2h)

3Blue1Brown, series "Neural networks", các chương về GPT/Transformer:

- [ ] Chương 5 — But what is a GPT? Visual intro to transformers — https://www.3blue1brown.com/lessons/gpt
- [ ] Chương 6 — Attention in transformers, visually explained — https://www.3blue1brown.com/lessons/attention
- [ ] Chương 7 — How might LLMs store facts — https://www.3blue1brown.com/lessons/mlp

### Hướng dẫn xem

Không cần nhớ hết video. Chỉ giữ lại những ý giúp trả lời 4 câu hỏi ở mục 2.
Chỉ xem video là đủ. Phần chữ bên dưới mỗi trang là bản viết của chính video, chỉ dùng để tra lại đoạn bị quên.

**Câu hỏi dẫn đường cho từng video** (để trong đầu trước khi bấm play):

- **Chương 5 — GPT:** Model nhận vào cái gì, trả ra cái gì ở bước cuối? Output có phải một chữ cố định không? Làm sao viết được cả đoạn dài khi mỗi lần chỉ ra một bước?
- **Chương 6 — Attention:** Một từ đổi nghĩa theo các từ xung quanh thế nào? Một token "nhìn" sang những token nào? Chi phí tăng thế nào khi câu dài ra?
- **Chương 7 — Lưu kiến thức:** Kiến thức nằm ở đâu trong model? Nó có được lưu như một bảng tra cứu chính xác không?

**Bỏ qua được:** các con số cụ thể (số chiều vector, số tham số GPT-3), kích thước ma trận, công thức toán.

**Cách nhớ tốt hơn:**

- Cứ khoảng 10 phút, dừng video và tự tóm tắt 1 câu. Không tóm tắt được thì tua lại đúng đoạn đó.
- Xem xong mỗi video, ghi từ khóa ngay, viết từ trí nhớ, không mở lại video.
- Nhớ nhiều nhất là lúc cố viết câu trả lời, không phải lúc xem.

**Thuật ngữ chương 5 — GPT:**

| Thuật ngữ | Nghĩa ngắn gọn |
|---|---|
| Token | Một mảnh văn bản nhỏ: có thể là một từ, một phần của từ, hoặc dấu câu. |
| Vector | Một danh sách rất nhiều con số. Có thể hình dung là một điểm trong không gian nhiều chiều. |
| Embedding | Bước đổi mỗi token thành một vector. Các token có nghĩa gần nhau sẽ có vector nằm gần nhau. |
| Trọng số (weights, parameters) | Các con số model học được trong lúc training. Đây là toàn bộ "kiến thức" của model. |
| Softmax | Phép biến một danh sách số bất kỳ thành các xác suất, tổng bằng 1. |
| Temperature | Tham số chỉnh độ "liều" khi chọn token tiếp theo. Sẽ nghịch thử ở Buổi 3. |

**Thuật ngữ chương 6 — Attention:**

| Thuật ngữ | Nghĩa ngắn gọn |
|---|---|
| Query | Vector mỗi token tạo ra để "hỏi": mình đang tìm thông tin kiểu gì từ các token khác? |
| Key | Vector mỗi token tạo ra để "trả lời": mình chứa thông tin kiểu gì? Query khớp với key nào thì token đó được chú ý nhiều. |
| Value | Thông tin thật sự được chuyển sang token đang hỏi, nếu query và key khớp nhau. |
| Attention pattern | Bảng điểm cho biết mỗi token chú ý tới từng token khác bao nhiêu. Để ý kích thước bảng này khi câu dài ra. |
| Masking | Quy tắc chặn token đứng sau ảnh hưởng tới token đứng trước, để model không "nhìn trộm" đáp án khi training. |
| Multi-head attention | Nhiều bộ attention chạy song song. Mỗi bộ, gọi là một head, học một kiểu quan hệ khác nhau giữa các từ. |
| Context size | Số token tối đa model xử lý được trong một lần. |

**Thuật ngữ chương 7 — Lưu kiến thức:**

| Thuật ngữ | Nghĩa ngắn gọn |
|---|---|
| MLP (multilayer perceptron) | Khối xử lý nằm sau attention. Nó xử lý từng vector riêng lẻ, không nhìn sang token khác. |
| Neuron | Một con số bên trong MLP. Có thể hình dung là nó "bật" lên khi vector đầu vào mang một đặc điểm nào đó. |
| ReLU | Hàm đổi mọi số âm thành 0 và giữ nguyên số dương. Đây là thứ tạo ra kiểu "bật hoặc tắt" của neuron. |
| Superposition | Hiện tượng một vector chứa được nhiều đặc điểm hơn số chiều của nó, nhờ dùng các hướng gần vuông góc với nhau. |

Ghi chú nhanh trong lúc xem (từ khóa, hình ảnh nhớ được):

-

## 2. Viết lại bằng lời của mình (5–10 dòng tổng cộng)

> Bản tham khảo do Claude viết. Đọc xong, thử viết lại bằng lời của mình ở dòng "Bản của mình" bên dưới mỗi câu.

### Vì sao LLM đoán next token?

LLM được train trên lượng văn bản khổng lồ với đúng một nhiệm vụ: nhìn đoạn phía trước, đoán token tiếp theo. Mỗi bước, model trả ra xác suất cho mọi token có thể có. Hệ thống chọn một token, nối vào cuối, rồi lặp lại, nên viết được cả đoạn dài. Nhiệm vụ nghe đơn giản, nhưng muốn đoán tốt thì model buộc phải học cả ngữ pháp, kiến thức và cách lập luận.

Bản của mình:

### Attention làm gì?

Attention cho mỗi token nhìn sang các token đứng trước nó, lấy thông tin liên quan để cập nhật nghĩa của chính mình. Ví dụ chữ "bàn" trong "bàn gỗ" và "bàn kế hoạch" mang nghĩa khác nhau, và attention giúp model phân biệt nhờ các từ xung quanh. Query là câu hỏi, key là câu trả lời, value là thông tin được chuyển sang.

Bản của mình:

### Vì sao có context window?

Attention so từng cặp token với nhau, nên bảng điểm lớn theo bình phương độ dài: gấp đôi số token thì tốn gấp bốn lần tính toán và bộ nhớ. Model cũng được train với một độ dài tối đa cố định. Phần văn bản nằm ngoài giới hạn đó thì model không nhìn thấy, nên hội thoại dài sẽ bị "quên" phần đầu.

Bản của mình:

### Vì sao LLM hallucinate?

Model không tra cứu một cơ sở dữ liệu. Kiến thức nằm rải rác trong trọng số dưới dạng gần đúng. Mục tiêu của nó là sinh ra token nghe hợp lý nhất, không phải token đúng sự thật, và nó không có cơ chế tự biết mình không biết. Khi thiếu kiến thức, nó vẫn viết ra câu trôi chảy nhưng sai.

Bản của mình:

## 3. Test

- [ ] Giải thích cho một người không biết kỹ thuật trong 3 phút (có thể tự ghi âm rồi nghe lại).
- Chỗ nào bị vấp khi giải thích:

-
