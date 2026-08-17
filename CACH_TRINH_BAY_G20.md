# Cách trình bày G20 — kịch bản nói 2 phút

> Nguyên tắc: **đừng trình bày code, hãy kể câu chuyện.** Người nghe hiểu được ví dụ
> đời thường nhanh hơn nhiều so với tên hàm. Nói chậm, mỗi màn chỉ 1 ý.

---

## MỞ ĐẦU — Ví dụ đời thường (30 giây)

> "G20 là một câu hỏi cần **3 loại trí nhớ cùng lúc**. Giống như khi em gặp lại một người bạn:
>
> - Em nhớ **điều bạn vừa nói xong** — short-term, trong cuộc trò chuyện này.
> - Em nhớ **bạn thích gì, đang làm dự án gì** — long-term, đã biết từ trước.
> - Em nhớ **luật chung của công ty** — semantic, ai cũng biết.
>
> G20 hỏi đúng cả 3 thứ đó trong một câu."

👉 Lúc này mở UI (hoặc slide 2): chỉ vào query và 3 marker.

---

## THÂN BÀI — Chỉ vào UI, đọc 3 dòng (1 phút)

> "Trong UI em chọn case G20 và bấm Run retrieval. Kết quả hiện 3 badge:

| Badge | Marker trả về | Giải thích bằng 1 câu |
| --- | --- | --- |
| **short_term** (xanh) | `HOLD-ALPHA-0900` | Giờ standup — durable notes giữ constraint dù 12 tin filler bị nén |
| **long_term** (xanh lá) | `NestJS` | Stack BLUEBIRD-42 — Zep nhớ fact của Minh từ stage 3 |
| **semantic** (tím) | `Idempotency-Key` | Quy tắc payment — từ KB dùng chung |

> Ghép 3 mảnh vào merged context, chấm điểm: **đủ 3 marker, và không có LOTUS-88 → PASS**."

👉 Lời nói ngắn cho từng lớp (nếu bị hỏi sâu):
- **short_term:** "14 tin nhắn, chỉ giữ 6 tin gần nhất, 8 lần compaction — nhưng constraint có từ khoá
  durable nên được giữ lại ở DURABLE_NOTES."
- **long_term:** "Zep trả 1403 token, budget chỉ 320 → phải trim. Em giữ cả đầu lẫn đuôi nên fact
  NestJS (ở đầu) vẫn còn."
- **semantic:** "Mỗi tài liệu được seed 2 lần, em dedupe chỉ giữ summary → 97 token, khớp budget."

---

## KẾT BÀI — 2 con số + 1 câu chốt (30 giây)

> "Về con số: 4 ô token **169 / 325 / 0 / 97**.
> 169 và 97 khớp budget nên không cần cắt. 325 là long-term bị trim từ 1403 — nhưng vẫn giữ
> NestJS nhờ trim giữ cả 2 đầu. episodic = 0 vì câu hỏi không cần.
>
> **Tóm lại: đúng scope → đủ marker → PASS."**

---

## Nếu bị hỏi (3 câu dự phòng)

| Câu hỏi | Trả lời |
| --- | --- |
| Vì sao LOTUS-88 không xuất hiện? | "Mỗi lớp lấy đúng chỗ của nó: short-term đọc đúng thread, long-term chỉ lấy graph của Minh, semantic chỉ lấy KB dùng chung. Đúng scope thì tự cách ly." |
| Vì sao long-term phải trim? | "Zep trả về rất nhiều (1403 token) nhưng budget của long-term chỉ 4% = 320 token. Không trim thì vỡ context." |
| Vì sao trim giữ cả 2 đầu? | "Marker có thể nằm ở đuôi: fact open-loop, mã ở cuối tài liệu. Cắt hết đuôi là tự bỏ evidence — lần đầu em chỉ giữ đầu nên fail 2 case, sửa xong 20/20." |

---

## 5 lỗi thường gặp khi trình bày

1. ❌ Đọc code từng dòng → ✅ Kể chuyện bằng ví dụ người bạn.
2. ❌ Nói hết 20 case → ✅ Chỉ tập trung G20 (1 case = 1 câu chuyện đủ).
3. ❌ Dùng quá nhiều thuật ngữ → ✅ "đúng chỗ", "đủ marker", "khớp budget".
4. ❌ Nói nhanh → ✅ Mỗi màn 1 ý, dừng lại sau mỗi badge.
5. ❌ Không biết số liệu → ✅ Nhớ 4 con số: **169 / 325 / 0 / 97** và **1403 → 325**.

---

## Phiên bản siêu ngắn (nếu chỉ có 30 giây)

> "G20 cần 3 loại nhớ: thread (short-term → giờ standup), hồ sơ user (long-term → NestJS),
> KB chung (semantic → Idempotency-Key). Đúng scope từng lớp, gộp lại đủ 3 marker, không lẫn
> LOTUS-88 → PASS."
