# Kịch bản bảo vệ 5 phút — Lab 17 Multi-Memory Agent

## ⏱ Phân bổ 5 phút

| Thời gian | Phần | Nội dung |
| --- | --- | --- |
| 0:00 – 0:30 | Giới thiệu | Tên + kết quả: practice 11/11, golden 20/20, UI demo hoạt động |
| 0:30 – 2:30 | Trình bày (2 phút) | Kiến trúc 4 layer + 1 câu chuyện: "một query cần nhiều nguồn nhớ" |
| 2:30 – 4:30 | Demo (2 phút) | Mở UI (case G20) hoặc report — chỉ 2–3 điểm số |
| 4:30 – 5:00 | Kết luận | 3 bài học + mời câu hỏi |

**Câu mở đầu gợi ý (30 giây):**
> "Em hoàn thiện Lab 17 với 4 lớp memory: short-term local, long-term và episodic trên user graph của Zep, semantic trên standalone graph dùng chung. Kết quả practice 11/11, golden 20/20, và UI demo chat được với OpenRouter. Em xin trình bày nhanh rồi trả lời câu hỏi."

---

## Câu hỏi dự kiến 1 — Vì sao phải chọn đúng scope (user_id / graph_id / thread)?

**Trả lời (30–45 giây):**
1. Ba "không gian" khác nhau: **short-term = thread**, **long-term + episodic = user**, **semantic = graph dùng chung**.
2. Scope sai = trộn dữ liệu: long-term mà search bằng `graph_id` sẽ kéo domain knowledge vào hồ sơ cá nhân; semantic mà search bằng `user_id` sẽ kéo preference cá nhân vào KB dùng chung.
3. Bằng chứng thật: **E09** có `must_not_contain: ORCHID-27` — Lan không được nhận memory của Minh. **G06/G14** cũng cấm trộn stack của người khác.
4. Code tương ứng: `retrieve_long_term`/`retrieve_episodic` dùng `user_id`; `retrieve_semantic` dùng `graph_id`; short-term đọc đúng `fixture_messages`/thread.

> Cụm khóa: **"Scope là tường lửa — đúng user, đúng graph, đúng thread."**

---

## Câu hỏi dự kiến 2 — Vì sao trim phải giữ cả 2 đầu (head + tail)?

**Trả lời (30–45 giây):**
1. Budget mỗi layer rất nhỏ (long-term 4% = 320 token) nhưng Zep trả về rất nhiều (Context Block ~1400 token) → **bắt buộc trim**.
2. Marker không chỉ nằm ở đầu: fact open-loop (`LAB-REPORT-1600`) nằm cuối danh sách edges; marker của KB (`BUDGET-10-4-3-3`) nằm cuối document.
3. Lần chạy đầu chỉ giữ đầu text → **G16, G18 fail (18/20)** — marker đuôi bị cắt mất.
4. Sửa: trim **giữ 70% đầu + 30% đuôi** → 20/20. Bằng chứng số: long-term `1403 → 325 token` mà vẫn giữ `NestJS`.

> Cụm khóa: **"Marker có thể nằm ở đuôi — cắt hết đuôi là tự bỏ evidence."**

---

## Câu hỏi dự kiến 3 — Vì sao episodic bị "nhiễu" và xử lý thế nào?

**Trả lời (30–45 giây):**
1. Khi đánh giá, `prime_eval_thread` thêm **query vào user graph dưới dạng episode** — `ignore_roles` chỉ chặn biến thành *fact*, không chặn lưu *episode*.
2. Query golden dài (180–300 ký tự) được index như episode, **xếp hạng cao hơn cả message thật**, đẩy episode evidence (`ClientSession`, `ASYNC-FIX-20`, `connection churn`) ra khỏi top-5 → **G07, G13, G18 fail (17/20)**.
3. Sửa trong `retrieve_episodic`: lọc episode dạng query (dài >190 ký tự **không có mã marker**, hoặc chứa `?`), ưu tiên episode **có mã marker**, rồi first-fit vào budget 3%.
4. Bằng chứng: cùng code — graph nhiễu trước fix 17/20, sau fix **20/20 cả trên graph nhiễu lẫn graph sạch**.

> Cụm khóa: **"Query của chính benchmark làm nhiễu graph — lọc episode dạng query, ưu tiên episode mang mã evidence."**

---

## Câu hỏi phụ (dự phòng)

| Câu hỏi | Trả lời ngắn |
| --- | --- |
| Vì sao golden 20/20 mà +10 all-or-nothing? | Giảng viên re-run bằng file gốc; chấm retrieval, không chấm may mắn. 19/20 = 0. |
| Vì sao no-memory reduction cao nhưng hit rate thấp? | No-memory reduction ~82% vì **trả về gần như rỗng**; cắt hết rẻ nhưng sai (2/11). Hit rate mới là thước đo. |
| Budget 10/4/3/3 nghĩa là gì? | 10%/4%/3%/3% của 8000 token = 800/320/240/240. Trim layer kém ưu tiên trước (STM → LT → EP → SEM). |
| Compaction giữ cái gì? | Durable notes: constraint/decision/TODO/mã viết hoa. E10: `REVIEW-DEADLINE-1600` sống sót sau 10 lần compact. |
| E08 recency là gì? | Constraint mới theo project (BLUEBIRD-42 → TypeScript/NestJS) thắng preference chung (Python) **đúng scope project đó**; Python vẫn đúng cho ORCHID-27. |
| Vì sao không dùng scope="auto" cho semantic? | "auto" trả fact đã trích xuất, **mất mã literal** (PAYMENT-RULE-3...). scope="episodes" giữ marker nguyên văn cho scorer. |

---

## Mẹo khi nói

1. Nói theo 3 cụm: **scope đúng → marker còn nguyên → PASS**.
2. Bị hỏi sâu → mở `reports/benchmark.json`/`golden_benchmark.json` chỉ số: `hit rate`, `budget_breakdown`, `latency_ms`.
3. Không nói dối: không nhớ thì nói "để em kiểm tra lại report" (report luôn có trong repo).
4. Khi demo UI: chọn **G20** (3 layer) → Run retrieval → chỉ 4 ô metric (169/325/0/97) → chat 1 câu bằng OpenRouter.
