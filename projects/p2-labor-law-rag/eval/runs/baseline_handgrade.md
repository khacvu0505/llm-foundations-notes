# Chấm tay 20 câu — Buổi 18 Bài 6

**Cách chấm** (tự đọc, **chưa** xem điểm giám khảo):

- **Bám nguồn?** `có` = **mọi ý** trong câu trả lời đều có trong các đoạn bot đã lấy (đọc đoạn `[n]` được trích, và cả 5 đoạn nếu cần). `không` = có ít nhất 1 ý **không** có trong đoạn nào (bịa, lấy từ trí nhớ, hoặc suy diễn sai). Câu **từ chối** ("Không tìm thấy…") không có ý nào → `có`.
- **Đúng câu hỏi?** (thêm, không bắt buộc) `có` / `không` / `thiếu` — so với đáp án chuẩn.
- Điền vào 2 dòng `→` ở cuối mỗi câu. Ghi chú ngắn nếu muốn.

_(⚠️ **Do Claude chấm theo yêu cầu của user** (2026-11-13) — là chấm của **một LLM khác**, có bằng chứng (đối chiếu từng con số với đoạn được trích + đọc nội dung), **không phải người chấm**; user nên tự xem lại ít nhất các câu lệch: q03, q07, q13.)_

_(File do Claude tạo từ `runs/baseline.jsonl` + `eval_set.jsonl`, 2026-11-13: 16 câu bot có trả lời + 4 câu từ chối nhầm q03, q05, q16, q25. Không có điểm DeepEval trong file này.)_

---

## q01 — Thử việc tối đa bao lâu?

**Đáp án chuẩn:** Tùy công việc: không quá 180 ngày với người quản lý doanh nghiệp; không quá 60 ngày với công việc cần trình độ từ cao đẳng trở lên; không quá 30 ngày với trình độ trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ; không quá 06 ngày làm việc với công việc khác. Chỉ được thử việc một lần cho một công việc.

**Bot trả lời:**

```
- Tối đa 180 ngày đối với công việc của người quản lý doanh nghiệp [2] (Điều 25).
- Tối đa 60 ngày đối với công việc cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên [2] (Điều 25).
- Tối đa 30 ngày đối với công việc cần trình độ trung cấp, công nhân kỹ thuật hoặc nhân viên nghiệp vụ [2] (Điều 25).
- Tối đa 06 ngày làm việc đối với công việc khác [2] (Điều 25).
```

**Đoạn được trích:**

<details><summary>[2] Điều 25. Thời gian thử việc — bllđ-18-vbhn-2026 #24</summary>

```
Thời gian thử việc
Thời gian thử việc do hai bên thỏa thuận căn cứ vào tính chất và mức độ phức tạp của công việc nhưng chỉ được thử việc một lần đối với một công việc và bảo đảm điều kiện sau đây:
1. Không quá 180 ngày đối với công việc của người quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp, Luật Quản lý, sử dụng vốn nhà nước đầu tư vào sản xuất, kinh doanh tại doanh nghiệp;
2. Không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên;
3. Không quá 30 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ;
4. Không quá 06 ngày làm việc đối với công việc khác.
Điều 26. Tiền lương thử việc
Tiền lương của người lao động trong thời gian thử việc do hai bên thỏa thuận nhưng ít nhất phải bằng 85% mức lương của công việc đó.
Điều 27. Kết thúc thời gian thử việc
1. Khi kết thúc thời gian thử việc, người sử dụng lao động phải thông báo kết quả thử việc cho người lao động.
Trường hợp
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: thiếu — không nêu "chỉ thử việc 1 lần"

---

## q02 — Lao động nữ được nghỉ thai sản bao lâu?

**Đáp án chuẩn:** Nghỉ trước và sau khi sinh con là 06 tháng; sinh con thứ hai là 07 tháng; thời gian nghỉ trước khi sinh không quá 02 tháng. Sinh đôi trở lên thì từ con thứ hai trở đi, mỗi con được nghỉ thêm 01 tháng.

**Bot trả lời:**

```
Lao động nữ được nghỉ thai sản 06 tháng; nếu sinh con thứ hai thì được nghỉ 07 tháng. Thời gian nghỉ trước khi sinh không quá 02 tháng; sinh đôi trở lên thì từ con thứ hai, mỗi con được nghỉ thêm 01 tháng [1] (Điều 139).
```

**Đoạn được trích:**

<details><summary>[1] Điều 139. Nghỉ thai sản — bllđ-18-vbhn-2026 #128</summary>

```
n thực hiện hợp đồng lao động.
Điều 139. Nghỉ thai sản
1.4 Lao động nữ được nghỉ thai sản trước và sau khi sinh con là 06 tháng; trường hợp sinh con thứ hai, lao động nữ được nghỉ thai sản trước và sau khi sinh con là 07 tháng; thời gian nghỉ trước khi sinh không quá 02 tháng.
Trường hợp lao động nữ sinh đôi trở lên thì tính từ con thứ hai trở đi, cứ mỗi con, người mẹ được nghỉ thêm 01 tháng.
2. Trong thời gian nghỉ thai sản, lao động nữ được hưởng chế độ thai sản theo quy định của pháp luật về bảo hiểm xã hội.
3. Hết thời gian nghỉ thai sản theo quy định tại khoản 1 Điều này, nếu có nhu cầu, lao động nữ có thể nghỉ thêm một thời gian không hưởng lương sau khi thỏa thuận với người sử dụng lao động.
4. Trước khi hết thời gian nghỉ thai sản theo quy định tại khoản 1 Điều này, lao động nữ có thể trở lại làm việc khi đã nghỉ ít nhất được 04 tháng nhưng người lao động phải báo trước, được người sử dụng lao động đồng ý và có xác nhận của cơ sở khám bệnh, chữa bệnh có thẩm quyền về việc đi làm sớm không có hại cho sức khỏe của người lao động. Trong trường hợ
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q04 — Lương thử việc ít nhất là bao nhiêu?

**Đáp án chuẩn:** Do hai bên thỏa thuận nhưng ít nhất phải bằng 85% mức lương của công việc đó.

**Bot trả lời:**

```
Tiền lương thử việc ít nhất bằng 85% mức lương của công việc đó [1] (Điều 26).
```

**Đoạn được trích:**

<details><summary>[1] Điều 25. Thời gian thử việc — bllđ-18-vbhn-2026 #24</summary>

```
Thời gian thử việc
Thời gian thử việc do hai bên thỏa thuận căn cứ vào tính chất và mức độ phức tạp của công việc nhưng chỉ được thử việc một lần đối với một công việc và bảo đảm điều kiện sau đây:
1. Không quá 180 ngày đối với công việc của người quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp, Luật Quản lý, sử dụng vốn nhà nước đầu tư vào sản xuất, kinh doanh tại doanh nghiệp;
2. Không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên;
3. Không quá 30 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ;
4. Không quá 06 ngày làm việc đối với công việc khác.
Điều 26. Tiền lương thử việc
Tiền lương của người lao động trong thời gian thử việc do hai bên thỏa thuận nhưng ít nhất phải bằng 85% mức lương của công việc đó.
Điều 27. Kết thúc thời gian thử việc
1. Khi kết thúc thời gian thử việc, người sử dụng lao động phải thông báo kết quả thử việc cho người lao động.
Trường hợp
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q06 — Người lao động hưởng lương theo tháng được trả lương mấy lần?

**Đáp án chuẩn:** Được trả một tháng một lần hoặc nửa tháng một lần. Thời điểm trả lương do hai bên thỏa thuận và phải được ấn định vào một thời điểm có tính chu kỳ.

**Bot trả lời:**

```
Người lao động hưởng lương theo tháng được trả một lần hoặc nửa tháng một lần [1] (Điều 97).
```

**Đoạn được trích:**

<details><summary>[1] Điều 96. Hình thức trả lương — bllđ-18-vbhn-2026 #92</summary>

```
c vào ban đêm, nội dung và số tiền bị khấu trừ (nếu có).
Điều 96. Hình thức trả lương
1. Người sử dụng lao động và người lao động thỏa thuận về hình thức trả lương theo thời gian, sản phẩm hoặc khoán.
2. Lương được trả bằng tiền mặt hoặc trả qua tài khoản cá nhân của người lao động được mở tại ngân hàng.
Trường hợp trả lương qua tài khoản cá nhân của người lao động được mở tại ngân hàng thì người sử dụng lao động phải trả các loại phí liên quan đến việc mở tài khoản và chuyển tiền lương.
3. Chính phủ quy định chi tiết Điều này.
Điều 97. Kỳ hạn trả lương
1. Người lao động hưởng lương theo giờ, ngày, tuần thì được trả lương sau giờ, ngày, tuần làm việc hoặc được trả gộp do hai bên thỏa thuận nhưng không quá 15 ngày phải được trả gộp một lần.
2. Người lao động hưởng lương theo tháng được trả một tháng một lần hoặc nửa tháng một lần. Thời điểm trả lương do hai bên thỏa thuận và phải được ấn định vào một thời điểm có tính chu kỳ.
3. Người lao động hưởng lương theo sản phẩm, theo khoán được trả lương theo thỏa thuận của hai bên; nếu công việc phải làm trong nhiều tháng thì hằ
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có (câu hơi lủng củng: "trả một lần hoặc nửa tháng một lần")

---

## q07 — Làm thêm giờ được trả lương ít nhất bao nhiêu?

**Đáp án chuẩn:** Tính theo đơn giá tiền lương hoặc tiền lương thực trả của công việc đang làm: ngày thường ít nhất 150%; ngày nghỉ hằng tuần ít nhất 200%; ngày nghỉ lễ, tết, ngày nghỉ có hưởng lương ít nhất 300% (chưa kể tiền lương ngày lễ, tết, ngày nghỉ có hưởng lương với người hưởng lương ngày).

**Bot trả lời:**

```
- Ngày thường: ít nhất bằng 150% tiền lương.
- Ngày nghỉ hằng tuần: ít nhất bằng 200%.
- Ngày nghỉ lễ, tết hoặc ngày nghỉ có hưởng lương: ít nhất bằng 300%, chưa kể tiền lương của ngày nghỉ đó đối với người hưởng lương ngày. [1] (Điều 98)
```

**Đoạn được trích:**

<details><summary>[1] Điều 97. Kỳ hạn trả lương — bllđ-18-vbhn-2026 #93</summary>

```
ương theo sản phẩm, theo khoán được trả lương theo thỏa thuận của hai bên; nếu công việc phải làm trong nhiều tháng thì hằng tháng được tạm ứng tiền lương theo khối lượng công việc đã làm trong tháng.
4. Trường hợp vì lý do bất khả kháng mà người sử dụng lao động đã tìm mọi biện pháp khắc phục nhưng không thể trả lương đúng hạn thì không được chậm quá 30 ngày; nếu trả lương chậm từ 15 ngày trở lên thì người sử dụng lao động phải đền bù cho người lao động một khoản tiền ít nhất bằng số tiền lãi của số tiền trả chậm tính theo lãi suất huy động tiền gửi có kỳ hạn 01 tháng do ngân hàng nơi người sử dụng lao động mở tài khoản trả lương cho người lao động công bố tại thời điểm trả lương.
Điều 98. Tiền lương làm thêm giờ, làm việc vào ban đêm
1. Người lao động làm thêm giờ được trả lương tính theo đơn giá tiền lương hoặc tiền lương thực trả theo công việc đang làm như sau:
a) Vào ngày thường, ít nhất bằng 150%;
b) Vào ngày nghỉ hằng tuần, ít nhất bằng 200%;
c) Vào ngày nghỉ lễ, tết, ngày nghỉ có hưởng lương, ít nhất bằng 300% chưa kể tiền
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q08 — Thời giờ làm việc bình thường tối đa là bao nhiêu?

**Đáp án chuẩn:** Không quá 08 giờ trong 01 ngày và không quá 48 giờ trong 01 tuần. Nếu người sử dụng lao động quy định theo tuần thì không quá 10 giờ trong 01 ngày và không quá 48 giờ trong 01 tuần. Nhà nước khuyến khích tuần làm việc 40 giờ.

**Bot trả lời:**

```
Tối đa 08 giờ trong một ngày và 48 giờ trong một tuần; nếu áp dụng thời giờ làm việc theo tuần thì tối đa 10 giờ trong một ngày, nhưng không quá 48 giờ trong một tuần [1] (Điều 105).
```

**Đoạn được trích:**

<details><summary>[1] Điều 105. Thời giờ làm việc bình thường — bllđ-18-vbhn-2026 #99</summary>

```
. Thời giờ làm việc bình thường
1. Thời giờ làm việc bình thường không quá 08 giờ trong 01 ngày và không quá 48 giờ trong 01 tuần.
2. Người sử dụng lao động có quyền quy định thời giờ làm việc theo ngày hoặc tuần nhưng phải thông báo cho người lao động biết; trường hợp theo tuần thì thời giờ làm việc bình thường không quá 10 giờ trong 01 ngày và không quá 48 giờ trong 01 tuần.
Nhà nước khuyến khích người sử dụng lao động thực hiện tuần làm việc 40 giờ đối với người lao động.
3. Người sử dụng lao động có trách nhiệm bảo đảm giới hạn thời gian làm việc tiếp xúc với yếu tố nguy hiểm, yếu tố có hại đúng theo quy chuẩn kỹ thuật quốc gia và pháp luật có liên quan.
Điều 106. Giờ làm việc ban đêm
Giờ làm việc ban đêm được tính từ 22 giờ đến 06 giờ sáng ngày hôm sau.
Điều 107. Làm thêm giờ
1. Thời gian làm thêm giờ là khoảng thời gian làm việc ngoài thời giờ làm việc bình thường theo quy định của pháp luật, thỏa ước lao động tập thể hoặc nội quy lao động.
2. Người sử dụng lao động được sử dụng người lao động làm thêm
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q10 — Làm đủ 12 tháng thì được nghỉ hằng năm bao nhiêu ngày?

**Đáp án chuẩn:** Hưởng nguyên lương: 12 ngày làm việc với công việc trong điều kiện bình thường; 14 ngày làm việc với lao động chưa thành niên, người khuyết tật, người làm nghề, công việc nặng nhọc, độc hại, nguy hiểm; 16 ngày làm việc với nghề, công việc đặc biệt nặng nhọc, độc hại, nguy hiểm. Làm chưa đủ 12 tháng thì tính theo tỷ lệ số tháng làm việc.

**Bot trả lời:**

```
- 12 ngày làm việc trong điều kiện bình thường; 14 ngày đối với người lao động chưa thành niên, người khuyết tật hoặc làm công việc nặng nhọc, độc hại, nguy hiểm; 16 ngày đối với công việc đặc biệt nặng nhọc, độc hại, nguy hiểm. Được hưởng nguyên lương theo hợp đồng lao động [1] (Điều 113).
```

**Đoạn được trích:**

<details><summary>[1] Điều 113. Nghỉ hằng năm — bllđ-18-vbhn-2026 #105</summary>

```
đ khoản 1 Điều này.
Điều 113. Nghỉ hằng năm
1. Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:
a) 12 ngày làm việc đối với người làm công việc trong điều kiện bình thường;
b) 14 ngày làm việc đối với người lao động chưa thành niên, lao động là người khuyết tật, người làm nghề, công việc nặng nhọc, độc hại, nguy hiểm;
c) 16 ngày làm việc đối với người làm nghề, công việc đặc biệt nặng nhọc, độc hại, nguy hiểm.
2. Người lao động làm việc chưa đủ 12 tháng cho một người sử dụng lao động thì số ngày nghỉ hằng năm theo tỷ lệ tương ứng với số tháng làm việc.
3. Trường hợp do thôi việc, bị mất việc làm mà chưa nghỉ hằng năm hoặc chưa nghỉ hết số ngày nghỉ hằng năm thì được người sử dụng lao động thanh toán tiền lương cho những ngày chưa nghỉ.
4. Người sử dụng lao động có trách nhiệm quy định lịch nghỉ hằng năm sau khi tham khảo ý kiến của người lao động và phải thông báo trước cho người lao độ
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q11 — Có những hình thức xử lý kỷ luật lao động nào?

**Đáp án chuẩn:** Có 4 hình thức: khiển trách; kéo dài thời hạn nâng lương không quá 06 tháng; cách chức; sa thải.

**Bot trả lời:**

```
- Khiển trách [3] (Điều 124).
- Kéo dài thời hạn nâng lương không quá 06 tháng [3] (Điều 124).
- Cách chức [3] (Điều 124).
- Sa thải [3] (Điều 124).
```

**Đoạn được trích:**

<details><summary>[3] Điều 123. Thời hiệu xử lý kỷ luật lao động — bllđ-18-vbhn-2026 #115</summary>

```
123. Thời hiệu xử lý kỷ luật lao động
1. Thời hiệu xử lý kỷ luật lao động là 06 tháng kể từ ngày xảy ra hành vi vi phạm; trường hợp hành vi vi phạm liên quan trực tiếp đến tài chính, tài sản, tiết lộ bí mật công nghệ, bí mật kinh doanh của người sử dụng lao động thì thời hiệu xử lý kỷ luật lao động là 12 tháng.
2. Khi hết thời gian quy định tại khoản 4 Điều 122 của Bộ luật này, nếu hết thời hiệu hoặc còn thời hiệu nhưng không đủ 60 ngày thì được kéo dài thời hiệu để xử lý kỷ luật lao động nhưng không quá 60 ngày kể từ ngày hết thời gian nêu trên.
3. Người sử dụng lao động phải ban hành quyết định xử lý kỷ luật lao động trong thời hạn quy định tại khoản 1 và khoản 2 Điều này.
Điều 124. Hình thức xử lý kỷ luật lao động
1. Khiển trách.
2. Kéo dài thời hạn nâng lương không quá 06 tháng.
3. Cách chức.
4. Sa thải.
Điều 125. Áp dụng hình thức xử lý kỷ luật sa thải
Hình thức xử lý kỷ luật sa thải được người sử dụng lao động áp dụng trong trường hợp sau đây:
1. Người la
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q12 — Thời hiệu xử lý kỷ luật lao động là bao lâu?

**Đáp án chuẩn:** 06 tháng kể từ ngày xảy ra hành vi vi phạm; nếu hành vi liên quan trực tiếp đến tài chính, tài sản, tiết lộ bí mật công nghệ, bí mật kinh doanh của người sử dụng lao động thì là 12 tháng.

**Bot trả lời:**

```
06 tháng kể từ ngày xảy ra hành vi vi phạm; nếu vi phạm liên quan trực tiếp đến tài chính, tài sản, bí mật công nghệ hoặc bí mật kinh doanh của người sử dụng lao động thì là 12 tháng [4] (Điều 123).
```

**Đoạn được trích:**

<details><summary>[4] Điều 123. Thời hiệu xử lý kỷ luật lao động — bllđ-18-vbhn-2026 #115</summary>

```
123. Thời hiệu xử lý kỷ luật lao động
1. Thời hiệu xử lý kỷ luật lao động là 06 tháng kể từ ngày xảy ra hành vi vi phạm; trường hợp hành vi vi phạm liên quan trực tiếp đến tài chính, tài sản, tiết lộ bí mật công nghệ, bí mật kinh doanh của người sử dụng lao động thì thời hiệu xử lý kỷ luật lao động là 12 tháng.
2. Khi hết thời gian quy định tại khoản 4 Điều 122 của Bộ luật này, nếu hết thời hiệu hoặc còn thời hiệu nhưng không đủ 60 ngày thì được kéo dài thời hiệu để xử lý kỷ luật lao động nhưng không quá 60 ngày kể từ ngày hết thời gian nêu trên.
3. Người sử dụng lao động phải ban hành quyết định xử lý kỷ luật lao động trong thời hạn quy định tại khoản 1 và khoản 2 Điều này.
Điều 124. Hình thức xử lý kỷ luật lao động
1. Khiển trách.
2. Kéo dài thời hạn nâng lương không quá 06 tháng.
3. Cách chức.
4. Sa thải.
Điều 125. Áp dụng hình thức xử lý kỷ luật sa thải
Hình thức xử lý kỷ luật sa thải được người sử dụng lao động áp dụng trong trường hợp sau đây:
1. Người la
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q13 — Độ tuổi lao động tối thiểu là bao nhiêu?

**Đáp án chuẩn:** Đủ 15 tuổi, trừ trường hợp quy định tại Mục 1 Chương XI của Bộ luật (lao động chưa thành niên).

**Bot trả lời:**

```
Độ tuổi tối thiểu thông thường là đủ 13 tuổi; người chưa đủ 13 tuổi chỉ được làm công việc nghệ thuật, thể dục, thể thao khi đáp ứng điều kiện luật định [5] (Điều 145).
```

**Đoạn được trích:**

<details><summary>[5] Điều 145. Sử dụng người chưa đủ 15 tuổi làm việc — bllđ-18-vbhn-2026 #133</summary>

```
tuổi;
c) Phải có giấy khám sức khỏe của cơ sở khám bệnh, chữa bệnh có thẩm quyền xác nhận sức khỏe của người chưa đủ 15 tuổi phù hợp với công việc và tổ chức kiểm tra sức khỏe định kỳ ít nhất một lần trong 06 tháng;
d) Bảo đảm điều kiện làm việc, an toàn, vệ sinh lao động phù hợp với lứa tuổi.
2. Người sử dụng lao động chỉ được tuyển dụng và sử dụng người từ đủ 13 tuổi đến chưa đủ 15 tuổi vào làm các công việc nhẹ theo quy định tại khoản 3 Điều 143 của Bộ luật này.
3. Người sử dụng lao động không được tuyển dụng và sử dụng người chưa đủ 13 tuổi làm việc, trừ các công việc nghệ thuật, thể dục, thể thao nhưng không làm tổn hại đến sự phát triển thể lực, trí lực, nhân cách của người chưa đủ 13 tuổi và phải có sự đồng ý của cơ quan chuyên môn về lao động thuộc Ủy ban nhân dân cấp tỉnh.
4. Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định chi tiết Điều này.
Điều 146. Thời giờ làm việc của người chưa thành niên
1. Thời giờ làm việc của người chưa đủ 15 tuổi không được quá 04 giờ trong 01 ngày và 20 giờ trong
```

</details>

→ Bám nguồn: không — suy diễn sai: Điều 145 nói về dùng người chưa đủ 15 tuổi, không nói "độ tuổi tối thiểu thông thường là 13" (ca ranh giới)

→ Đúng câu hỏi: không — đúng là đủ 15 tuổi (Điều 3)

---

## q14 — Người chưa thành niên được làm việc tối đa bao nhiêu giờ?

**Đáp án chuẩn:** Người chưa đủ 15 tuổi: không quá 04 giờ/ngày và 20 giờ/tuần, không được làm thêm giờ, làm việc ban đêm. Người từ đủ 15 đến chưa đủ 18 tuổi: không quá 08 giờ/ngày và 40 giờ/tuần; có thể làm thêm giờ, làm ban đêm trong một số nghề, công việc theo danh mục do Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành.

**Bot trả lời:**

```
- Người chưa đủ 15 tuổi: tối đa 4 giờ/ngày và 20 giờ/tuần [1] (Điều 146).
- Người từ đủ 15 tuổi đến chưa đủ 18 tuổi: tối đa 8 giờ/ngày và 40 giờ/tuần [1] (Điều 146).
```

**Đoạn được trích:**

<details><summary>[1] Điều 146. Thời giờ làm việc của người chưa thành niên — bllđ-18-vbhn-2026 #134</summary>

```
ười chưa thành niên
1. Thời giờ làm việc của người chưa đủ 15 tuổi không được quá 04 giờ trong 01 ngày và 20 giờ trong 01 tuần; không được làm thêm giờ, làm việc vào ban đêm.
2. Thời giờ làm việc của người từ đủ 15 tuổi đến chưa đủ 18 tuổi không được quá 08 giờ trong 01 ngày và 40 giờ trong 01 tuần. Người từ đủ 15 tuổi đến chưa đủ 18 tuổi có thể được làm thêm giờ, làm việc vào ban đêm trong một số nghề, công việc theo danh mục do Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành.
Điều 147. Công việc và nơi làm việc cấm sử dụng người lao động từ đủ 15 tuổi đến chưa đủ 18 tuổi
1. Cấm sử dụng người lao động từ đủ 15 tuổi đến chưa đủ 18 tuổi làm các công việc sau đây:
a) Mang, vác, nâng các vật nặng vượt quá thể trạng của người chưa thành niên;
b) Sản xuất, kinh doanh cồn, rượu, bia, thuốc lá, chất tác động đến tinh thần hoặc chất gây nghiện khác;
c) Sản xuất, sử dụng hoặc vận chuyển hóa chất, khí gas, chất nổ;
d) Bảo trì, bảo dưỡng thiết bị, máy móc;
đ) Phá dỡ các công trình xây dựng;
e) Nấu, thổi, đúc, cán, dập, h
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q15 — Tuổi nghỉ hưu của người lao động là bao nhiêu?

**Đáp án chuẩn:** Trong điều kiện lao động bình thường, tuổi nghỉ hưu tăng theo lộ trình đến đủ 62 tuổi với nam vào năm 2028 và đủ 60 tuổi với nữ vào năm 2035. Từ năm 2021 là đủ 60 tuổi 03 tháng (nam) và 55 tuổi 04 tháng (nữ), sau đó mỗi năm tăng thêm 03 tháng với nam và 04 tháng với nữ.

**Bot trả lời:**

```
Trong điều kiện lao động bình thường, tuổi nghỉ hưu tăng theo lộ trình: từ năm 2021 là 60 tuổi 03 tháng đối với nam và 55 tuổi 04 tháng đối với nữ; mỗi năm tăng thêm lần lượt 03 tháng và 04 tháng, đến đủ 62 tuổi đối với nam vào năm 2028 và 60 tuổi đối với nữ vào năm 2035 [1] (Điều 169).
```

**Đoạn được trích:**

<details><summary>[1] Điều 168. Tham gia bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp — bllđ-18-vbhn-2026 #151</summary>

```
ng theo quy định của pháp luật về bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp.
Điều 169. Tuổi nghỉ hưu
1. Người lao động bảo đảm điều kiện về thời gian đóng bảo hiểm xã hội theo quy định của pháp luật về bảo hiểm xã hội được hưởng lương hưu khi đủ tuổi nghỉ hưu.
2. Tuổi nghỉ hưu của người lao động trong điều kiện lao động bình thường được điều chỉnh theo lộ trình cho đến khi đủ 62 tuổi đối với lao động nam vào năm 2028 và đủ 60 tuổi đối với lao động nữ vào năm 2035.
Kể từ năm 2021, tuổi nghỉ hưu của người lao động trong điều kiện lao động bình thường là đủ 60 tuổi 03 tháng đối với lao động nam và đủ 55 tuổi 04 tháng đối với lao động nữ; sau đó, cứ mỗi năm tăng thêm 03 tháng đối với lao động nam và 04 tháng đối với lao động nữ.
3. Người lao động bị suy giảm khả năng lao động; làm nghề, công việc đặc biệt nặng nhọc, độc hại, nguy hiểm; làm nghề, công việc nặng nhọc, độc hại, nguy hiểm; làm việc ở vùng có điều kiện kinh tế - xã hội đặc biệt khó kh
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q18 — Mức lương tối thiểu là gì và do ai quyết định?

**Đáp án chuẩn:** Là mức lương thấp nhất trả cho người lao động làm công việc giản đơn nhất trong điều kiện lao động bình thường, bảo đảm mức sống tối thiểu của người lao động và gia đình. Được xác lập theo vùng, ấn định theo tháng, giờ. Chính phủ quyết định và công bố trên cơ sở khuyến nghị của Hội đồng tiền lương quốc gia.

**Bot trả lời:**

```
Mức lương tối thiểu là mức lương thấp nhất trả cho người lao động làm công việc giản đơn nhất trong điều kiện lao động bình thường, nhằm bảo đảm mức sống tối thiểu của người lao động và gia đình họ [1] (Điều 91). Chính phủ quyết định và công bố mức lương tối thiểu trên cơ sở khuyến nghị của Hội đồng tiền lương quốc gia [3] (Điều 91).
```

**Đoạn được trích:**

<details><summary>[1] Điều 90. Tiền lương — bllđ-18-vbhn-2026 #88</summary>

```
tập thể do phía người sử dụng lao động chi trả.
Chương VI
TIỀN LƯƠNG
Điều 90. Tiền lương
1. Tiền lương là số tiền mà người sử dụng lao động trả cho người lao động theo thỏa thuận để thực hiện công việc, bao gồm mức lương theo công việc hoặc chức danh, phụ cấp lương và các khoản bổ sung khác.
2. Mức lương theo công việc hoặc chức danh không được thấp hơn mức lương tối thiểu.
3. Người sử dụng lao động phải bảo đảm trả lương bình đẳng, không phân biệt giới tính đối với người lao động làm công việc có giá trị như nhau.
Điều 91. Mức lương tối thiểu
1. Mức lương tối thiểu là mức lương thấp nhất được trả cho người lao động làm công việc giản đơn nhất trong điều kiện lao động bình thường nhằm bảo đảm mức sống tối thiểu của người lao động và gia đình họ, phù hợp với điều kiện phát triển kinh tế - xã hội.
2. Mức lương tối thiểu được xác lập theo vùng, ấn định theo tháng, giờ.
3. Mức lương tối thiểu được điều chỉnh dựa trên mức sống tối thiểu của người lao động và gia đình họ; tương quan giữa mức lương tối thiểu và mức lương trên thị trường; chỉ số giá tiêu d
```

</details>

<details><summary>[3] Điều 91. Mức lương tối thiểu — bllđ-18-vbhn-2026 #89</summary>

```
người lao động và gia đình họ; tương quan giữa mức lương tối thiểu và mức lương trên thị trường; chỉ số giá tiêu dùng, tốc độ tăng trưởng kinh tế; quan hệ cung, cầu lao động; việc làm và thất nghiệp; năng suất lao động; khả năng chi trả của doanh nghiệp.
4. Chính phủ quy định chi tiết Điều này; quyết định và công bố mức lương tối thiểu trên cơ sở khuyến nghị của Hội đồng tiền lương quốc gia.
Điều 92. Hội đồng tiền lương quốc gia
1. Hội đồng tiền lương quốc gia là cơ quan tư vấn cho Chính phủ về mức lương tối thiểu và chính sách tiền lương đối với người lao động.
2. Thủ tướng Chính phủ thành lập Hội đồng tiền lương quốc gia bao gồm các thành viên là đại diện của Bộ Lao động - Thương binh và Xã hội, Tổng Liên đoàn Lao động Việt Nam, một số tổ chức đại diện người sử dụng lao động ở trung ương và chuyên gia độc lập.
3. Chính phủ quy định chức năng, nhiệm vụ, cơ cấu tổ chức và hoạt động của Hội đồng tiền lương quốc gia.
Điều 93. Xây dựng thang lương, bảng lương và định mức lao động
1. Người sử dụng lao động
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: thiếu — không nêu "theo vùng, theo tháng, giờ"

---

## q19 — Tôi làm kế toán, công việc yêu cầu trình độ cao đẳng. Công ty được cho tôi thử việc tối đa bao lâu?

**Đáp án chuẩn:** Không quá 60 ngày (công việc cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên), và chỉ được thử việc một lần đối với một công việc.

**Bot trả lời:**

```
Tối đa 60 ngày [1] (Điều 25).
```

**Đoạn được trích:**

<details><summary>[1] Điều 25. Thời gian thử việc — bllđ-18-vbhn-2026 #24</summary>

```
Thời gian thử việc
Thời gian thử việc do hai bên thỏa thuận căn cứ vào tính chất và mức độ phức tạp của công việc nhưng chỉ được thử việc một lần đối với một công việc và bảo đảm điều kiện sau đây:
1. Không quá 180 ngày đối với công việc của người quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp, Luật Quản lý, sử dụng vốn nhà nước đầu tư vào sản xuất, kinh doanh tại doanh nghiệp;
2. Không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên;
3. Không quá 30 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ;
4. Không quá 06 ngày làm việc đối với công việc khác.
Điều 26. Tiền lương thử việc
Tiền lương của người lao động trong thời gian thử việc do hai bên thỏa thuận nhưng ít nhất phải bằng 85% mức lương của công việc đó.
Điều 27. Kết thúc thời gian thử việc
1. Khi kết thúc thời gian thử việc, người sử dụng lao động phải thông báo kết quả thử việc cho người lao động.
Trường hợp
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có

---

## q21 — Thử việc tối đa bao lâu và lương thử việc ít nhất là bao nhiêu?

**Đáp án chuẩn:** Thời gian thử việc không quá 180 ngày (quản lý doanh nghiệp), 60 ngày (trình độ từ cao đẳng), 30 ngày (trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ), 06 ngày làm việc (công việc khác); chỉ thử việc một lần. Lương thử việc do hai bên thỏa thuận nhưng ít nhất bằng 85% mức lương của công việc đó.

**Bot trả lời:**

```
- Thời gian thử việc tối đa: 180 ngày với công việc của người quản lý doanh nghiệp; 60 ngày với công việc cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên; 30 ngày với công việc cần trình độ trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ; 06 ngày làm việc với công việc khác [1] (Điều 25).
- Lương thử việc ít nhất bằng 85% mức lương của công việc đó [1] (Điều 26).
```

**Đoạn được trích:**

<details><summary>[1] Điều 25. Thời gian thử việc — bllđ-18-vbhn-2026 #24</summary>

```
Thời gian thử việc
Thời gian thử việc do hai bên thỏa thuận căn cứ vào tính chất và mức độ phức tạp của công việc nhưng chỉ được thử việc một lần đối với một công việc và bảo đảm điều kiện sau đây:
1. Không quá 180 ngày đối với công việc của người quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp, Luật Quản lý, sử dụng vốn nhà nước đầu tư vào sản xuất, kinh doanh tại doanh nghiệp;
2. Không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên;
3. Không quá 30 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ;
4. Không quá 06 ngày làm việc đối với công việc khác.
Điều 26. Tiền lương thử việc
Tiền lương của người lao động trong thời gian thử việc do hai bên thỏa thuận nhưng ít nhất phải bằng 85% mức lương của công việc đó.
Điều 27. Kết thúc thời gian thử việc
1. Khi kết thúc thời gian thử việc, người sử dụng lao động phải thông báo kết quả thử việc cho người lao động.
Trường hợp
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: có (thiếu nhỏ "chỉ thử việc 1 lần")

---

## q24 — Lao động nữ mang thai tháng thứ 7 có phải làm ban đêm, làm thêm giờ không, và được nghỉ thai sản bao lâu?

**Đáp án chuẩn:** Không: người sử dụng lao động không được cho làm việc ban đêm, làm thêm giờ, đi công tác xa khi mang thai từ tháng thứ 07 (hoặc từ tháng thứ 06 nếu làm ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo). Nghỉ thai sản trước và sau sinh 06 tháng (sinh con thứ hai 07 tháng), nghỉ trước sinh không quá 02 tháng.

**Bot trả lời:**

```
- Từ tháng thứ 7 của thai kỳ, người sử dụng lao động không được bố trí lao động nữ làm việc ban đêm hoặc làm thêm giờ [1] (Điều 137).
- Lao động nữ được nghỉ thai sản 6 tháng, thời gian nghỉ trước khi sinh không quá 2 tháng; theo tài liệu, nếu sinh con thứ hai thì được nghỉ 7 tháng [2] (Điều 139).
```

**Đoạn được trích:**

<details><summary>[1] Điều 137. Bảo vệ thai sản — bllđ-18-vbhn-2026 #125</summary>

```
ụng người lao động làm việc ban đêm, làm thêm giờ và đi công tác xa trong trường hợp sau đây:
a) Mang thai từ tháng thứ 07 hoặc từ tháng thứ 06 nếu làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo;
b) Đang nuôi con dưới 12 tháng tuổi, trừ trường hợp được người lao động đồng ý.
2. Lao động nữ làm nghề, công việc nặng nhọc, độc hại, nguy hiểm hoặc đặc biệt nặng nhọc, độc hại, nguy hiểm hoặc làm nghề, công việc có ảnh hưởng xấu tới chức năng sinh sản và nuôi con khi mang thai và có thông báo cho người sử dụng lao động biết thì được người sử dụng lao động chuyển sang làm công việc nhẹ hơn, an toàn hơn hoặc giảm bớt 01 giờ làm việc hằng ngày mà không bị cắt giảm tiền lương và quyền, lợi ích cho đến hết thời gian nuôi con dưới 12 tháng tuổi.
3. Người sử dụng lao động không được sa thải hoặc đơn phương chấm dứt hợp đồng lao động đối với người lao động vì lý do kết hôn, mang thai, nghỉ thai sản, nuôi con dưới 12 tháng tuổi, trừ trường hợp người sử dụng lao động là cá nhân chết, bị Tòa án tuyên bố mất n
```

</details>

<details><summary>[2] Điều 139. Nghỉ thai sản — bllđ-18-vbhn-2026 #128</summary>

```
n thực hiện hợp đồng lao động.
Điều 139. Nghỉ thai sản
1.4 Lao động nữ được nghỉ thai sản trước và sau khi sinh con là 06 tháng; trường hợp sinh con thứ hai, lao động nữ được nghỉ thai sản trước và sau khi sinh con là 07 tháng; thời gian nghỉ trước khi sinh không quá 02 tháng.
Trường hợp lao động nữ sinh đôi trở lên thì tính từ con thứ hai trở đi, cứ mỗi con, người mẹ được nghỉ thêm 01 tháng.
2. Trong thời gian nghỉ thai sản, lao động nữ được hưởng chế độ thai sản theo quy định của pháp luật về bảo hiểm xã hội.
3. Hết thời gian nghỉ thai sản theo quy định tại khoản 1 Điều này, nếu có nhu cầu, lao động nữ có thể nghỉ thêm một thời gian không hưởng lương sau khi thỏa thuận với người sử dụng lao động.
4. Trước khi hết thời gian nghỉ thai sản theo quy định tại khoản 1 Điều này, lao động nữ có thể trở lại làm việc khi đã nghỉ ít nhất được 04 tháng nhưng người lao động phải báo trước, được người sử dụng lao động đồng ý và có xác nhận của cơ sở khám bệnh, chữa bệnh có thẩm quyền về việc đi làm sớm không có hại cho sức khỏe của người lao động. Trong trường hợ
```

</details>

→ Bám nguồn: có

→ Đúng câu hỏi: thiếu — không nêu "đi công tác xa" và mốc tháng thứ 06 ở vùng cao…

---

## q03 — Có mấy loại hợp đồng lao động?

**Đáp án chuẩn:** Có 2 loại: hợp đồng lao động không xác định thời hạn (hai bên không xác định thời hạn, thời điểm chấm dứt hợp đồng) và hợp đồng lao động xác định thời hạn (thời hạn không quá 36 tháng kể từ khi hợp đồng có hiệu lực).

**Bot trả lời:**

```
Không tìm thấy thông tin này trong tài liệu.
```

**Đoạn đã lấy (bot không trích):**

<details><summary>[1] Điều 18. Thẩm quyền giao kết hợp đồng lao động — bllđ-18-vbhn-2026 #18</summary>

```
o động được những người lao động trong nhóm ủy quyền hợp pháp giao kết hợp đồng lao động.
5. Người được ủy quyền giao kết hợp đồng lao động không được ủy quyền lại cho người khác giao kết hợp đồng lao động.
Điều 19. Giao kết nhiều hợp đồng lao động
1. Người lao động có thể giao kết nhiều hợp đồng lao động với nhiều người sử dụng lao động nhưng phải bảo đảm thực hiện đầy đủ các nội dung đã giao kết.
2. Người lao động đồng thời giao kết nhiều hợp đồng lao động với nhiều người sử dụng lao động thì việc tham gia bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp được thực hiện theo quy định của pháp luật về bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp và an toàn, vệ sinh lao động.
Điều 20. Loại hợp đồng lao động
1. Hợp đồng lao động phải được giao kết theo một trong các loại sau đây:
a) Hợp đồng lao động không xác định thời hạn là hợp đồng mà trong đó hai bên không xác định thời hạn, thời điểm chấm dứt hiệu lực của hợp đồng;
b) Hợp đồ
```

</details>

<details><summary>[2] Điều 30. Tạm hoãn thực hiện hợp đồng lao động — bllđ-18-vbhn-2026 #28</summary>

```
m hoãn thực hiện hợp đồng lao động
1. Các trường hợp tạm hoãn thực hiện hợp đồng lao động bao gồm:
a) Người lao động thực hiện nghĩa vụ quân sự, nghĩa vụ tham gia Dân quân tự vệ;
b) Người lao động bị tạm giữ, tạm giam theo quy định của pháp luật về tố tụng hình sự;
c) Người lao động phải chấp hành quyết định áp dụng biện pháp đưa vào trường giáo dưỡng, cơ sở cai nghiện bắt buộc hoặc cơ sở giáo dục bắt buộc;
d) Lao động nữ mang thai theo quy định tại Điều 138 của Bộ luật này;
đ) Người lao động được bổ nhiệm làm người quản lý doanh nghiệp của công ty trách nhiệm hữu hạn một thành viên do Nhà nước nắm giữ 100% vốn điều lệ;
e) Người lao động được ủy quyền để thực hiện quyền, trách nhiệm của đại diện chủ sở hữu nhà nước đối với phần vốn nhà nước tại doanh nghiệp;
g) Người lao động được ủy quyền để thực hiện quyền, trách nhiệm của doanh nghiệp đối với phần vốn của doanh nghiệp đầu tư tại doanh nghiệp khác;
h) Trường hợp khác do hai bên thỏa thuận.
2. Trong thời gian tạm ho
```

</details>

<details><summary>[3] Điều 32. Làm việc không trọn thời gian — bllđ-18-vbhn-2026 #30</summary>

```
ường theo ngày hoặc theo tuần hoặc theo tháng được quy định trong pháp luật về lao động, thỏa ước lao động tập thể hoặc nội quy lao động.
2. Người lao động thỏa thuận với người sử dụng lao động làm việc không trọn thời gian khi giao kết hợp đồng lao động.
3. Người lao động làm việc không trọn thời gian được hưởng lương; bình đẳng trong thực hiện quyền và nghĩa vụ với người lao động làm việc trọn thời gian; bình đẳng về cơ hội, không bị phân biệt đối xử, bảo đảm an toàn, vệ sinh lao động.
Điều 33. Sửa đổi, bổ sung hợp đồng lao động
1. Trong quá trình thực hiện hợp đồng lao động, nếu bên nào có yêu cầu sửa đổi, bổ sung nội dung hợp đồng lao động thì phải báo cho bên kia biết trước ít nhất 03 ngày làm việc về nội dung cần sửa đổi, bổ sung.
2. Trường hợp hai bên thỏa thuận được thì việc sửa đổi, bổ sung nội dung hợp đồng lao động được tiến hành bằng việc ký kết phụ lục hợp đồng lao động hoặc giao kết hợp đồng lao động mới.
3. Trường hợp hai bên không thỏa thuận được việc sửa đổi,
```

</details>

<details><summary>[4] Điều 219. Sửa đổi, bổ sung một số điều của các luật có liên quan đến lao động — bllđ-18-vbhn-2026 #207</summary>

```
ộng theo hình thức sa thải hoặc về trường hợp bị đơn phương chấm dứt hợp đồng lao động;
b) Về bồi thường thiệt hại, trợ cấp khi chấm dứt hợp đồng lao động;
c) Giữa người giúp việc gia đình với người sử dụng lao động;
d) Về bảo hiểm xã hội theo quy định của pháp luật về bảo hiểm xã hội, về bảo hiểm y tế theo quy định của pháp luật về bảo hiểm y tế, về bảo hiểm thất nghiệp theo quy định của pháp luật về việc làm, về bảo hiểm tai nạn lao động, bệnh nghề nghiệp theo quy định của pháp luật về an toàn, vệ sinh lao động;
đ) Về bồi thường thiệt hại giữa người lao động với doanh nghiệp, tổ chức đưa người lao động đi làm việc ở nước ngoài theo hợp đồng;
e) Giữa người lao động thuê lại với người sử dụng lao động thuê lại.
1a. Tranh chấp lao động cá nhân mà hai bên thỏa thuận lựa chọn Hội đồng trọng tài lao động giải quyết nhưng hết thời hạn theo quy định của pháp luật về lao động mà Ban trọng tài lao động không được thành lập, Ban trọng tài lao động không ra quyết định gi
```

</details>

<details><summary>[5] Điều 29. Chuyển người lao động làm công việc khác so với hợp đồng lao động — bllđ-18-vbhn-2026 #27</summary>

```
thời chuyển người lao động làm công việc khác so với hợp đồng lao động quy định tại khoản 1 Điều này, người sử dụng lao động phải báo cho người lao động biết trước ít nhất 03 ngày làm việc, thông báo rõ thời hạn làm tạm thời và bố trí công việc phù hợp với sức khỏe, giới tính của người lao động.
3. Người lao động chuyển sang làm công việc khác so với hợp đồng lao động được trả lương theo công việc mới. Nếu tiền lương của công việc mới thấp hơn tiền lương của công việc cũ thì được giữ nguyên tiền lương của công việc cũ trong thời hạn 30 ngày làm việc. Tiền lương theo công việc mới ít nhất phải bằng 85% tiền lương của công việc cũ nhưng không thấp hơn mức lương tối thiểu.
4. Người lao động không đồng ý tạm thời làm công việc khác so với hợp đồng lao động quá 60 ngày làm việc cộng dồn trong 01 năm mà phải ngừng việc thì người sử dụng lao động phải trả lương ngừng việc theo quy định tại Điều 99 của Bộ luật này.
Điều 30. Tạm hoãn thực hiện hợp đồng lao động
1. Các trường hợp tạm hoãn thực hiện hợp đồng lao động
```

</details>

→ Bám nguồn: có (từ chối, không có ý nào)

→ Đúng câu hỏi: không — từ chối nhầm

---

## q05 — Người lao động muốn nghỉ việc thì phải báo trước bao lâu?

**Đáp án chuẩn:** Phải báo trước cho người sử dụng lao động: ít nhất 45 ngày nếu hợp đồng không xác định thời hạn; ít nhất 30 ngày nếu hợp đồng xác định thời hạn từ 12 tháng đến 36 tháng; ít nhất 03 ngày làm việc nếu hợp đồng xác định thời hạn dưới 12 tháng; một số ngành, nghề, công việc đặc thù thì theo quy định của Chính phủ.

**Bot trả lời:**

```
Không tìm thấy thông tin này trong tài liệu.
```

**Đoạn đã lấy (bot không trích):**

<details><summary>[1] Điều 36. Quyền đơn phương chấm dứt hợp đồng lao động của người sử dụng lao động — bllđ-18-vbhn-2026 #37</summary>

```
) Người lao động tự ý bỏ việc mà không có lý do chính đáng từ 05 ngày làm việc liên tục trở lên;
g) Người lao động cung cấp không trung thực thông tin theo quy định tại khoản 2 Điều 16 của Bộ luật này khi giao kết hợp đồng lao động làm ảnh hưởng đến việc tuyển dụng người lao động.
2. Khi đơn phương chấm dứt hợp đồng lao động trong trường hợp quy định tại các điểm a, b, c, đ và g khoản 1 Điều này, người sử dụng lao động phải báo trước cho người lao động như sau:
a) Ít nhất 45 ngày đối với hợp đồng lao động không xác định thời hạn;
b) Ít nhất 30 ngày đối với hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;
c) Ít nhất 03 ngày làm việc đối với hợp đồng lao động xác định thời hạn có thời hạn dưới 12 tháng và đối với trường hợp quy định tại điểm b khoản 1 Điều này;
d) Đối với một số ngành, nghề, công việc đặc thù thì thời hạn báo trước được thực hiện theo quy định của Chính phủ.
3. Khi đơn phương chấm dứt hợp đồng lao động quy định tại điểm
```

</details>

<details><summary>[2] Điều 109. Nghỉ trong giờ làm việc — bllđ-18-vbhn-2026 #103</summary>

```
06 giờ trở lên thì thời gian nghỉ giữa giờ được tính vào giờ làm việc.
2. Ngoài thời gian nghỉ quy định tại khoản 1 Điều này, người sử dụng lao động bố trí cho người lao động các đợt nghỉ giải lao và ghi vào nội quy lao động.
Điều 110. Nghỉ chuyển ca
Người lao động làm việc theo ca được nghỉ ít nhất 12 giờ trước khi chuyển sang ca làm việc khác.
Điều 111. Nghỉ hằng tuần
1. Mỗi tuần, người lao động được nghỉ ít nhất 24 giờ liên tục. Trong trường hợp đặc biệt do chu kỳ lao động không thể nghỉ hằng tuần thì người sử dụng lao động có trách nhiệm bảo đảm cho người lao động được nghỉ tính bình quân 01 tháng ít nhất 04 ngày.
2. Người sử dụng lao động có quyền quyết định sắp xếp ngày nghỉ hằng tuần vào ngày Chủ nhật hoặc ngày xác định khác trong tuần nhưng phải ghi vào nội quy lao động.
3. Nếu ngày nghỉ hằng tuần trùng với ngày nghỉ lễ, tết quy định tại khoản 1 Điều 112 của Bộ luật này thì người lao động được nghỉ bù ngày nghỉ hằng tuần vào ngày làm việc kế tiếp.
Điều 112. Ngh
```

</details>

<details><summary>[3] Điều 35. Quyền đơn phương chấm dứt hợp đồng lao động của người lao động — bllđ-18-vbhn-2026 #34</summary>

```
ghề, công việc đặc thù thì thời hạn báo trước được thực hiện theo quy định của Chính phủ.
2. Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:
a) Không được bố trí theo đúng công việc, địa điểm làm việc hoặc không được bảo đảm điều kiện làm việc theo thỏa thuận, trừ trường hợp quy định tại Điều 29 của Bộ luật này;
b) Không được trả đủ lương hoặc trả lương không đúng thời hạn, trừ trường hợp quy định tại khoản 4 Điều 97 của Bộ luật này;
c) Bị người sử dụng lao động ngược đãi, đánh đập hoặc có lời nói, hành vi nhục mạ, hành vi làm ảnh hưởng đến sức khỏe, nhân phẩm, danh dự; bị cưỡng bức lao động;
d) Bị quấy rối tình dục tại nơi làm việc;
đ) Lao động nữ mang thai phải nghỉ việc theo quy định tại khoản 1 Điều 138 của Bộ luật này;
e) Đủ tuổi nghỉ hưu theo quy định tại Điều 169 của Bộ luật này, trừ trường hợp các bên có thỏa thuận khác;
g) Người sử dụng lao động cung cấp thông tin không trung thực theo quy định tại khoản 1 Điều 16 của Bộ lu
```

</details>

<details><summary>[4] Điều 113. Nghỉ hằng năm — bllđ-18-vbhn-2026 #106</summary>

```
định lịch nghỉ hằng năm sau khi tham khảo ý kiến của người lao động và phải thông báo trước cho người lao động biết. Người lao động có thể thỏa thuận với người sử dụng lao động để nghỉ hằng năm thành nhiều lần hoặc nghỉ gộp tối đa 03 năm một lần.
5. Khi nghỉ hằng năm mà chưa đến kỳ trả lương, người lao động được tạm ứng tiền lương theo quy định tại khoản 3 Điều 101 của Bộ luật này.
6. Khi nghỉ hằng năm, nếu người lao động đi bằng các phương tiện đường bộ, đường sắt, đường thủy mà số ngày đi đường cả đi và về trên 02 ngày thì từ ngày thứ 03 trở đi được tính thêm thời gian đi đường ngoài ngày nghỉ hằng năm và chỉ được tính cho 01 lần nghỉ trong năm.
7. Chính phủ quy định chi tiết điều này.
Điều 114. Ngày nghỉ hằng năm tăng thêm theo thâm niên làm việc
Cứ đủ 05 năm làm việc cho một người sử dụng lao động thì số ngày nghỉ hằng năm của người lao động theo quy định tại khoản 1 Điều 113 của Bộ luật này được tăng thêm tương ứng 01 ngày.
Điều 115. Nghỉ việc riêng, nghỉ không hưởng lương
1. Người lao động được
```

</details>

<details><summary>[5] Điều 36. Quyền đơn phương chấm dứt hợp đồng lao động của người sử dụng lao động — bllđ-18-vbhn-2026 #36</summary>

```
c đối với người làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng hoặc quá nửa thời hạn hợp đồng lao động đối với người làm việc theo hợp đồng lao động xác định thời hạn có thời hạn dưới 12 tháng mà khả năng lao động chưa hồi phục.
Khi sức khỏe của người lao động bình phục thì người sử dụng lao động xem xét để tiếp tục giao kết hợp đồng lao động với người lao động;
c) Do thiên tai, hỏa hoạn, dịch bệnh nguy hiểm, địch họa hoặc di dời, thu hẹp sản xuất, kinh doanh theo yêu cầu của cơ quan nhà nước có thẩm quyền mà người sử dụng lao động đã tìm mọi biện pháp khắc phục nhưng vẫn buộc phải giảm chỗ làm việc;
d) Người lao động không có mặt tại nơi làm việc sau thời hạn quy định tại Điều 31 của Bộ luật này;
đ) Người lao động đủ tuổi nghỉ hưu theo quy định tại Điều 169 của Bộ luật này, trừ trường hợp có thỏa thuận khác;
e) Người lao động tự ý bỏ việc mà không có lý do chính đáng từ 05 ngày làm việc liên tục trở lên;
```

</details>

→ Bám nguồn: có (từ chối)

→ Đúng câu hỏi: không — từ chối nhầm

---

## q16 — Thời hiệu yêu cầu giải quyết tranh chấp lao động cá nhân là bao lâu?

**Đáp án chuẩn:** Tính từ ngày phát hiện hành vi vi phạm quyền, lợi ích hợp pháp: yêu cầu hòa giải viên lao động 06 tháng; yêu cầu Hội đồng trọng tài lao động 09 tháng; yêu cầu Tòa án 01 năm.

**Bot trả lời:**

```
Không tìm thấy thông tin này trong tài liệu.
```

**Đoạn đã lấy (bot không trích):**

<details><summary>[1] Điều 189. Giải quyết tranh chấp lao động cá nhân của Hội đồng trọng tài lao động — bllđ-18-vbhn-2026 #177</summary>

```
giải quyết tranh chấp.
3. Trong thời hạn 30 ngày kể từ ngày Ban trọng tài lao động được thành lập, Ban trọng tài lao động phải ra quyết định về việc giải quyết tranh chấp và gửi cho các bên tranh chấp.
4. Trường hợp hết thời hạn quy định tại khoản 2 Điều này mà Ban trọng tài lao động không được thành lập hoặc hết thời hạn quy định tại khoản 3 Điều này mà Ban trọng tài lao động không ra quyết định giải quyết tranh chấp thì các bên có quyền yêu cầu Tòa án giải quyết.
5. Trường hợp một trong các bên không thi hành quyết định giải quyết tranh chấp của Ban trọng tài lao động thì các bên có quyền yêu cầu Tòa án giải quyết.
Điều 190. Thời hiệu yêu cầu giải quyết tranh chấp lao động cá nhân
1. Thời hiệu yêu cầu hòa giải viên lao động thực hiện hòa giải tranh chấp lao động cá nhân là 06 tháng kể từ ngày phát hiện ra hành vi mà bên tranh chấp cho rằng quyền và lợi ích hợp pháp của mình bị vi phạm.
2. Thời hiệu yêu cầu Hội đồng trọng tài lao động giải quyết tranh chấp lao động cá nhân là 09 tháng kể từ ngày phát hiện ra hành vi mà
```

</details>

<details><summary>[2] Điều 36. Quyền đơn phương chấm dứt hợp đồng lao động của người sử dụng lao động — bllđ-18-vbhn-2026 #37</summary>

```
) Người lao động tự ý bỏ việc mà không có lý do chính đáng từ 05 ngày làm việc liên tục trở lên;
g) Người lao động cung cấp không trung thực thông tin theo quy định tại khoản 2 Điều 16 của Bộ luật này khi giao kết hợp đồng lao động làm ảnh hưởng đến việc tuyển dụng người lao động.
2. Khi đơn phương chấm dứt hợp đồng lao động trong trường hợp quy định tại các điểm a, b, c, đ và g khoản 1 Điều này, người sử dụng lao động phải báo trước cho người lao động như sau:
a) Ít nhất 45 ngày đối với hợp đồng lao động không xác định thời hạn;
b) Ít nhất 30 ngày đối với hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;
c) Ít nhất 03 ngày làm việc đối với hợp đồng lao động xác định thời hạn có thời hạn dưới 12 tháng và đối với trường hợp quy định tại điểm b khoản 1 Điều này;
d) Đối với một số ngành, nghề, công việc đặc thù thì thời hạn báo trước được thực hiện theo quy định của Chính phủ.
3. Khi đơn phương chấm dứt hợp đồng lao động quy định tại điểm
```

</details>

<details><summary>[3] Điều 34. Các trường hợp chấm dứt hợp đồng lao động — bllđ-18-vbhn-2026 #33</summary>

```
y định tại Điều 42 và Điều 43 của Bộ luật này.
12. Giấy phép lao động hết hiệu lực đối với người lao động là người nước ngoài làm việc tại Việt Nam theo quy định tại Điều 156 của Bộ luật này.
13. Trường hợp thỏa thuận nội dung thử việc ghi trong hợp đồng lao động mà thử việc không đạt yêu cầu hoặc một bên hủy bỏ thỏa thuận thử việc.
Điều 35. Quyền đơn phương chấm dứt hợp đồng lao động của người lao động
1. Người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước cho người sử dụng lao động như sau:
a) Ít nhất 45 ngày nếu làm việc theo hợp đồng lao động không xác định thời hạn;
b) Ít nhất 30 ngày nếu làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;
c) Ít nhất 03 ngày làm việc nếu làm việc theo hợp đồng lao động xác định thời hạn có thời hạn dưới 12 tháng;
d) Đối với một số ngành, nghề, công việc đặc thù thì thời hạn báo trước được thực hiện theo quy định của Chính phủ.
2. Người lao đ
```

</details>

<details><summary>[4] Điều 197. Giải quyết tranh chấp lao động tập thể về lợi ích của Hội đồng trọng tài lao động — bllđ-18-vbhn-2026 #185</summary>

```
ơ sở đồng thuận, các bên tranh chấp có quyền yêu cầu Hội đồng trọng tài lao động giải quyết tranh chấp trong trường hợp hòa giải không thành hoặc hết thời hạn hòa giải quy định tại khoản 2 Điều 188 của Bộ luật này mà hòa giải viên lao động không tiến hành hòa giải hoặc một trong các bên không thực hiện thỏa thuận trong biên bản hòa giải thành.
2. Trong thời hạn 07 ngày làm việc kể từ ngày nhận được yêu cầu giải quyết tranh chấp theo quy định tại khoản 1 Điều này, Ban trọng tài lao động phải được thành lập để giải quyết tranh chấp.
3. Trong thời hạn 30 ngày kể từ ngày được thành lập, căn cứ vào quy định của pháp luật về lao động, thỏa ước lao động tập thể, nội quy lao động đã được đăng ký và các quy chế, thỏa thuận hợp pháp khác, Ban trọng tài lao động phải ra quyết định về việc giải quyết tranh chấp và gửi cho các bên tranh chấp.
4. Khi các bên lựa chọn giải quyết tranh chấp thông qua Hội đồng trọng tài lao động theo quy định tại Điều này thì tổ chức đại diện người lao động không được tiến hành đình công trong thời gian Hội đồng trọng tài lao động đang ti
```

</details>

<details><summary>[5] Điều 125. Áp dụng hình thức xử lý kỷ luật sa thải — bllđ-18-vbhn-2026 #117</summary>

```
n trong thời hạn 30 ngày hoặc 20 ngày cộng dồn trong thời hạn 365 ngày tính từ ngày đầu tiên tự ý bỏ việc mà không có lý do chính đáng.
Trường hợp được coi là có lý do chính đáng bao gồm thiên tai, hỏa hoạn, bản thân, thân nhân bị ốm có xác nhận của cơ sở khám bệnh, chữa bệnh có thẩm quyền và trường hợp khác được quy định trong nội quy lao động.
Điều 126. Xóa kỷ luật, giảm thời hạn chấp hành kỷ luật lao động
1. Người lao động bị khiển trách sau 03 tháng hoặc bị xử lý kỷ luật kéo dài thời hạn nâng lương sau 06 tháng hoặc bị xử lý kỷ luật cách chức sau 03 năm kể từ ngày bị xử lý, nếu không tiếp tục vi phạm kỷ luật lao động thì đương nhiên được xóa kỷ luật.
2. Người lao động bị xử lý kỷ luật kéo dài thời hạn nâng lương sau khi chấp hành được một nửa thời hạn nếu sửa chữa tiến bộ thì có thể được người sử dụng lao động xét giảm thời hạn.
Điều 127. Các hành vi bị nghiêm cấm khi xử lý kỷ luật lao động
1. Xâm phạm sức khỏe, danh dự, tính mạng, uy tín, nhân phẩm của người lao độ
```

</details>

→ Bám nguồn: có (từ chối)

→ Đúng câu hỏi: không — từ chối nhầm

---

## q25 — Người lao động tự ý bỏ việc 5 ngày trong một tháng có thể bị sa thải không? Nếu bị sa thải thì có được trợ cấp thôi việc không?

**Đáp án chuẩn:** Có thể bị sa thải nếu tự ý bỏ việc 05 ngày cộng dồn trong 30 ngày (hoặc 20 ngày cộng dồn trong 365 ngày) mà không có lý do chính đáng. Bị sa thải là trường hợp chấm dứt hợp đồng tại khoản 8 Điều 34, không thuộc các trường hợp được trả trợ cấp thôi việc (Điều 46 chỉ áp dụng các khoản 1, 2, 3, 4, 6, 7, 9, 10 Điều 34) → không được trợ cấp thôi việc.

**Bot trả lời:**

```
Không tìm thấy thông tin này trong tài liệu.
```

**Đoạn đã lấy (bot không trích):**

<details><summary>[1] Điều 125. Áp dụng hình thức xử lý kỷ luật sa thải — bllđ-18-vbhn-2026 #116</summary>

```
Hình thức xử lý kỷ luật sa thải được người sử dụng lao động áp dụng trong trường hợp sau đây:
1. Người lao động có hành vi trộm cắp, tham ô, đánh bạc, cố ý gây thương tích, sử dụng ma tuý tại nơi làm việc;
2. Người lao động có hành vi tiết lộ bí mật kinh doanh, bí mật công nghệ, xâm phạm quyền sở hữu trí tuệ của người sử dụng lao động, có hành vi gây thiệt hại nghiêm trọng hoặc đe dọa gây thiệt hại đặc biệt nghiêm trọng về tài sản, lợi ích của người sử dụng lao động hoặc quấy rối tình dục tại nơi làm việc được quy định trong nội quy lao động;
3. Người lao động bị xử lý kỷ luật kéo dài thời hạn nâng lương hoặc cách chức mà tái phạm trong thời gian chưa xóa kỷ luật. Tái phạm là trường hợp người lao động lặp lại hành vi vi phạm đã bị xử lý kỷ luật mà chưa được xóa kỷ luật theo quy định tại Điều 126 của Bộ luật này;
4. Người lao động tự ý bỏ việc 05 ngày cộng dồn trong thời hạn 30 ngày hoặc 20 ngày cộng dồn trong thời hạn 365 ngày tính từ ngày đầu tiên tự ý bỏ vi
```

</details>

<details><summary>[2] Điều 125. Áp dụng hình thức xử lý kỷ luật sa thải — bllđ-18-vbhn-2026 #117</summary>

```
n trong thời hạn 30 ngày hoặc 20 ngày cộng dồn trong thời hạn 365 ngày tính từ ngày đầu tiên tự ý bỏ việc mà không có lý do chính đáng.
Trường hợp được coi là có lý do chính đáng bao gồm thiên tai, hỏa hoạn, bản thân, thân nhân bị ốm có xác nhận của cơ sở khám bệnh, chữa bệnh có thẩm quyền và trường hợp khác được quy định trong nội quy lao động.
Điều 126. Xóa kỷ luật, giảm thời hạn chấp hành kỷ luật lao động
1. Người lao động bị khiển trách sau 03 tháng hoặc bị xử lý kỷ luật kéo dài thời hạn nâng lương sau 06 tháng hoặc bị xử lý kỷ luật cách chức sau 03 năm kể từ ngày bị xử lý, nếu không tiếp tục vi phạm kỷ luật lao động thì đương nhiên được xóa kỷ luật.
2. Người lao động bị xử lý kỷ luật kéo dài thời hạn nâng lương sau khi chấp hành được một nửa thời hạn nếu sửa chữa tiến bộ thì có thể được người sử dụng lao động xét giảm thời hạn.
Điều 127. Các hành vi bị nghiêm cấm khi xử lý kỷ luật lao động
1. Xâm phạm sức khỏe, danh dự, tính mạng, uy tín, nhân phẩm của người lao độ
```

</details>

<details><summary>[3] Điều 36. Quyền đơn phương chấm dứt hợp đồng lao động của người sử dụng lao động — bllđ-18-vbhn-2026 #36</summary>

```
c đối với người làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng hoặc quá nửa thời hạn hợp đồng lao động đối với người làm việc theo hợp đồng lao động xác định thời hạn có thời hạn dưới 12 tháng mà khả năng lao động chưa hồi phục.
Khi sức khỏe của người lao động bình phục thì người sử dụng lao động xem xét để tiếp tục giao kết hợp đồng lao động với người lao động;
c) Do thiên tai, hỏa hoạn, dịch bệnh nguy hiểm, địch họa hoặc di dời, thu hẹp sản xuất, kinh doanh theo yêu cầu của cơ quan nhà nước có thẩm quyền mà người sử dụng lao động đã tìm mọi biện pháp khắc phục nhưng vẫn buộc phải giảm chỗ làm việc;
d) Người lao động không có mặt tại nơi làm việc sau thời hạn quy định tại Điều 31 của Bộ luật này;
đ) Người lao động đủ tuổi nghỉ hưu theo quy định tại Điều 169 của Bộ luật này, trừ trường hợp có thỏa thuận khác;
e) Người lao động tự ý bỏ việc mà không có lý do chính đáng từ 05 ngày làm việc liên tục trở lên;
```

</details>

<details><summary>[4] Điều 36. Quyền đơn phương chấm dứt hợp đồng lao động của người sử dụng lao động — bllđ-18-vbhn-2026 #37</summary>

```
) Người lao động tự ý bỏ việc mà không có lý do chính đáng từ 05 ngày làm việc liên tục trở lên;
g) Người lao động cung cấp không trung thực thông tin theo quy định tại khoản 2 Điều 16 của Bộ luật này khi giao kết hợp đồng lao động làm ảnh hưởng đến việc tuyển dụng người lao động.
2. Khi đơn phương chấm dứt hợp đồng lao động trong trường hợp quy định tại các điểm a, b, c, đ và g khoản 1 Điều này, người sử dụng lao động phải báo trước cho người lao động như sau:
a) Ít nhất 45 ngày đối với hợp đồng lao động không xác định thời hạn;
b) Ít nhất 30 ngày đối với hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;
c) Ít nhất 03 ngày làm việc đối với hợp đồng lao động xác định thời hạn có thời hạn dưới 12 tháng và đối với trường hợp quy định tại điểm b khoản 1 Điều này;
d) Đối với một số ngành, nghề, công việc đặc thù thì thời hạn báo trước được thực hiện theo quy định của Chính phủ.
3. Khi đơn phương chấm dứt hợp đồng lao động quy định tại điểm
```

</details>

<details><summary>[5] Điều 219. Sửa đổi, bổ sung một số điều của các luật có liên quan đến lao động — bllđ-18-vbhn-2026 #202</summary>

```
c biệt khó khăn bao gồm cả thời gian làm việc ở nơi có phụ cấp khu vực hệ số 0,7 trở lên trước ngày 01 tháng 01 năm 2021;
c) Người lao động có tuổi thấp hơn tối đa 10 tuổi so với tuổi nghỉ hưu của người lao động quy định tại khoản 2 Điều 169 của Bộ luật Lao động và có đủ 15 năm làm công việc khai thác than trong hầm lò;
d) Người bị nhiễm HIV do tai nạn rủi ro nghề nghiệp trong khi thực hiện nhiệm vụ được giao.
2. Người lao động quy định tại điểm đ và điểm e khoản 1 Điều 2 của Luật này nghỉ việc có đủ 20 năm đóng bảo hiểm xã hội trở lên được hưởng lương hưu khi thuộc một trong các trường hợp sau đây:
a) Có tuổi thấp hơn tối đa 05 tuổi so với tuổi nghỉ hưu quy định tại khoản 2 Điều 169 của Bộ luật Lao động, trừ trường hợp Luật Sĩ quan Quân đội nhân dân Việt Nam, Luật Công an nhân dân, Luật Cơ yếu, Luật Quân nhân chuyên nghiệp, công nhân và viên chức quốc phòng có quy định khác;
b) Có tuổi thấp hơn tối đa 05 tuổi so với tuổi nghỉ hưu quy định tại khoản 3 Điều 169 của Bộ luật Lao độ
```

</details>

→ Bám nguồn: có (từ chối)

→ Đúng câu hỏi: không — từ chối nhầm
