# Hướng dẫn chi tiết — Lab 17: Multi-Memory Agent với Zep

Tài liệu này giải thích **cách làm** bài lab, **từng bước test** và **vì sao phải làm đúng như vậy**, dựa trên chính code của starter kit (`src/`, `data/`, `tests/`, `reports/`).

---

## 1. Bản chất lab và cách chấm điểm

### 1.1. Lab này dạy gì

Một agent cần **nhiều hơn một chỗ lưu text**. Lab xây 4 lớp memory song song và chứng minh rằng mỗi lớp phục vụ một mục đích khác nhau:

| Layer | Giữ cái gì | Scope | Backend |
| --- | --- | --- | --- |
| **Short-term** | 4–6 turn gần nhất của thread hiện tại + durable notes | Thread | `ShortTermMemory` local (buffer/summary/sliding) |
| **Long-term** | Preference, fact, open loop, quyết định bền vững qua nhiều session | User | Zep Context Block + fact edges |
| **Episodic** | Trajectory, outcome, reflection của những lần trước | User | Zep episode search |
| **Semantic** | Tri thức domain dùng chung (payment rule, playbook) | Toàn công ty | Zep standalone graph |
| **Mixed (E07)** | Ghép nhiều layer theo budget | — | `ContextBudgetManager` |

### 1.2. Scorer chấm thế nào (đọc kỹ trước khi code)

- Nguồn thật của evaluator là **`data/sessions.json`** (2 user, 3 stage, 11 case). `data/ground_truth.json` chỉ là bản trích để đọc nhanh — **scorer không load file này**.
- Mỗi case có `must_contain_all` (bắt buộc có) và `must_not_contain` (cấm xuất hiện).
- Scorer **normalize** (hạ hoa thường, gộp khoảng trắng) rồi tìm chuỗi con trong **retrieved text**:
  - Mọi string trong `must_contain_all` phải xuất hiện → mới PASS.
  - Bất kỳ string nào trong `must_not_contain` xuất hiện → FAIL.
  - Exception hoặc retrieved rỗng → FAIL.
- **Không có LLM tham gia chấm.** Vì vậy không thể "đoán câu trả lời nghe hợp lý" để che lỗi retrieval — nếu retrieval không lấy đúng evidence, case chắc chắn fail.

> **Hệ quả quan trọng:** bạn phải tối ưu cho **marker literal** (chuỗi đúng như `PAYMENT-RULE-3`, `concurrency=20`, `16:00`) xuất hiện nguyên văn trong text bạn trả về. Một câu trả lời "đúng ý" nhưng không chứa marker vẫn bị tính FAIL.

### 1.3. Bảng điểm (tran 80 + cong)

| Khoi | Diem |
| --- | ---: |
| 11 case E01–E11 | 56 |
| Privacy drill | 6 |
| 4 cau phan tich + `comparison.md` | 6 |
| 3 cau thuc hanh trong README_submission | 6 |
| Artefact | 6 |
| **Tran nen** | **80** |
| Golden 20/20 | +10 hoặc 0 |
| UI demo / report dep | +10 tối đa |

**Điều kiện pass:** nền ≥ 56/80 **và** practice hit rate ≥ 80% (≥ 9/11 PASS) **và** nộp đủ artefact **và** không commit secret.

---

## 2. Kiến trúc và luồng dữ liệu

```text
data/sessions.json ──> ingest theo stage ──> Zep user graph (threads, facts, episodes)
                                                       │
data/knowledge.jsonl ──> seed ──> Zep standalone semantic graph
                                                       │
Query ──> evaluator dispatch theo expected_layer ──> retrieve (student code)
                                                       │
        short_term (local)   long_term (Context Block)   episodic (user search)   semantic (graph search)
                                                       │
                              ContextBudgetManager (10/4/3/3, priority)
                                                       │
                                              merged context ──> scorer (normalize + markers)
```

### Vai trò từng file bạn phải biết

| File | Vai trò | Bạn có sửa không? |
| --- | --- | --- |
| `src/memory_student.py` | **4 hàm TODO của bạn** | ✅ ĐÚNG |
| `src/memory_reference.py` | Lời giải của giảng viên | ❌ KHÔNG (copy = -30) |
| `src/evaluate.py` | Evaluator: đọc dataset, gọi memory impl, chấm, ghi report | ❌ KHÔNG |
| `src/seed.py` | Reset user + ingest session + seed semantic graph | ❌ KHÔNG |
| `src/zep_common.py` | Helper Zep: `prime_eval_thread`, `render_graph_search`, polling | ❌ KHÔNG |
| `src/context_budget.py` | `ContextBudgetManager` 10/4/3/3 | ❌ KHÔNG |
| `src/short_term.py` | Short-term local (đã hoàn chỉnh) | ❌ KHÔNG |
| `src/utils.py` | `cap_query` (≤400 ký tự), `estimate_tokens`, `normalize` | ❌ KHÔNG |
| `src/demo_ui.py` | Bonus UI (+10) | ✅ Chỉ hàm `retrieve_for_case` |
| `tests/` | Unit test lock starter kit | ❌ KHÔNG |

> **Quy tắc vàng:** chỉ sửa `memory_student.py` (bắt buộc) và `demo_ui.py` (nếu làm bonus). Sửa test/scorer/ground-truth để điểm tăng sẽ bị phát hiện và trừ artefact.

---

## 3. Các bước làm + TẠI SAO phải làm vậy

### Bước 0 — Chuẩn bị môi trường

```bash
cp .env.example .env          # điền ZEP_API_KEY
docker compose build
docker compose up -d redis qdrant
```

**Tại sao:**
- Docker đóng gói **client code + Redis + Qdrant local baseline** — không phải Zep server. Zep là **Cloud V3** (SDK `zep-cloud`), bạn chỉ cần API key.
- Redis/Qdrant tồn tại để bạn **nhìn thấy sự khác biệt** giữa "tự build memory" và "managed memory" — không phải để thay thế Zep.

### Bước 1 — Smoke test

```bash
docker compose run --rm app python -m src.smoke
```

**Nó kiểm tra 4 thứ:** Redis ping được, Qdrant trả HTTP 200, `sessions.json` có ≥10 evaluation phủ 4 layer, `ZEP_API_KEY` có giá trị.

**Tại sao phải chạy trước:** đây là *tiền quyết* — nếu một trong 4 mục fail, mọi bước sau (seed, evaluate) sẽ fail hàng loạt và bạn không biết lỗi nằm ở đâu. Tách "môi trường" khỏi "code" trước khi bắt đầu debug.

### Bước 2 — Seed Zep một lần

```bash
docker compose run --rm app python -m src.seed
```

**Nó làm gì:** reset 2 synthetic user, ingest toàn bộ message theo stage (1→2→3), seed 4 document từ `knowledge.jsonl` vào standalone graph, rồi **poll** đến khi marker chính (`PAYMENT-RULE-3`, `CONN-POOL-FIRST`, `DELETE-VERIFY-ALL`, `BUDGET-10-4-3-3`) searchable được.

**Tại sao:**
- Zep index **bất đồng bộ**: vừa ingest xong chưa chắc search ra. `wait_for_search` poll tới `ZEP_POLL_TIMEOUT` (240s) để chắc chắn dữ liệu sẵn sàng — nếu không, benchmark fail vì "chưa kịp index" chứ không phải vì code bạn sai.
- Chỉ cần seed **một lần**. Các lệnh sau dùng `--reuse-seeded` để **không ingest lặp lại** (vừa nhanh vừa không làm lệch trạng thái dữ liệu).

### Bước 3 — Pha A: short-term + compaction (E01, E10 — 9 điểm, KHÔNG viết code)

```bash
docker compose run --rm app python -m src.demo_short_term
docker compose run --rm app pytest -q tests/test_short_term.py
```

Quan sát 3 strategy trong `src/short_term.py`:
- **buffer:** giữ tất cả → token tăng tuyến tính, không bao giờ quên nhưng vỡ budget.
- **summary:** nén turn cũ thành summary, giữ 2 turn gần nhất.
- **sliding (default):** `SESSION_SUMMARY + DURABLE_NOTES + RECENT_TURNS(last K)`.

Cơ chế cốt lõi là `extract_durable_notes`: nó chỉ "giữ lại" message có dấu hiệu bền vững (chứa `todo`, `deadline`, `constraint`, `decision`, `must`, `open loop`, `preference`, `uu tien`, hoặc **marker viết hoa** như `REVIEW-DEADLINE-1600`).

**Tại sao E10 pass được:** fixture gồm 14 turn nhưng chỉ 2 turn chứa constraint. Sliding evict 10 turn filler nhưng durable note vẫn giữ `REVIEW-DEADLINE-1600 - Friday 16:00`. Buffer thì giữ hết nhưng đó là "thắng về recall, thua về budget" — lab dạy rằng **compaction không phải tóm tắt văn hoa**, mà phải ưu tiên **state, decision, TODO, constraint**.

**Tại sao không cần sửa `evaluate.py`:** E01/E10 được `src.evaluate` chạy **trực tiếp** qua `ShortTermMemory` local với `fixture_messages`, không đi qua 4 hàm student. Test `tests/test_short_term.py` đã khóa hành vi này.

### Bước 4 — Pha B: long-term bằng Context Block (TODO 1/4 — E02, E03, E08, E09 = 20 điểm)

```python
def retrieve_long_term(self, user_id, thread_id, query):
    prime_eval_thread(self.client, user_id, thread_id, query)          # 1) đã có sẵn
    user_context = self.client.thread.get_user_context(thread_id=thread_id)  # 2)
    context_block = getattr(user_context, "context", "") or ""         # 3) trả .context
    # bonus: graph.search(user_id=..., scope="edges", limit=20) + render
    return join_nonempty([context_block, fact_text], sep="\n\n")
```

**Tại sao từng dòng:**
1. `prime_eval_thread` tạo **thread đánh giá mới** (xóa thread cũ cùng id) và thêm query hiện tại với `ignore_roles=["user"]` — nghĩa là **query không bị tính thành memory bền**. Nếu bỏ qua, Zep có thể học nhầm câu hỏi thành fact.
2. `get_user_context` trả về **Context Block** — Zep tự tổng hợp user summary + facts + episodes liên quan từ **toàn bộ thread của user đó**. Đây chính là long-term memory: preference từ `minh-s1` vẫn trả về khi query ở thread mới `eval-e02` (E02 pass nhờ vậy).
3. Phải trả về **`.context` (string)**, không trả object SDK — scorer cần text.

**Bonus edges (scope="edges")**: fact có `valid_at/invalid_at` — hữu ích để thấy recency (E08: TypeScript thay Python cho BLUEBIRD-42) và tránh mất open loop. **Tại sao an toàn:** search theo `user_id` nên không bao giờ leak sang user khác (E09 yêu cầu Lan không thấy `ORCHID-27`).

**Tại sao 4 case này là long-term:**
- E02: preference từ thread cũ (`minh-s1`) hỏi ở thread mới → cần cross-session, short-term không có.
- E03: open loop "benchmark report 16:00" là durable task → phải nằm trong user graph.
- E08: **recency/conflict** — constraint mới (TypeScript/NestJS cho BLUEBIRD-42) thắng preference chung (Python) **đúng scope project đó**, nhưng Python vẫn đúng cho ORCHID-27.
- E09: **user isolation** — `lan-lab17` chỉ được thấy memory của Lan.

### Bước 5 — Pha C: episodic (TODO 2/4 — E04, E05 = 10 điểm)

```python
def retrieve_episodic(self, user_id, query):
    results = self.client.graph.search(
        user_id=user_id,                 # scope theo USER, không phải graph_id
        query=cap_query(query),          # luôn cap ≤ 400 ký tự
        scope="episodes", limit=15,
    )
    return render_graph_search(results, episode_char_cap=180)
```

**Tại sao:**
- Episodic = "lần trước đã làm gì" → thuộc **user graph** (dùng `user_id`), không phải standalone graph. Dùng `graph_id` sẽ search sang domain knowledge (sai scope, fail 0 điểm).
- `scope="episodes"` trả về **nguyên văn message/episode** — chứa marker `ClientSession`, `concurrency=20`, `ASYNC-FIX-20`.
- **`episode_char_cap=180`:** episode session rất dài (cả đoạn hội thoại debug). Nếu render nguyên, episode dài sẽ đẩy episode ngắn chứa reflection ra ngoài budget 3% → E05 fail. Cắt mỗi episode còn 180 ký tự giúp **giữ được nhiều episode khác nhau** trong budget.
- `cap_query`: Zep **từ chối query > 400 ký tự**. Query golden có thể dài 450–600 ký tự → luôn cap trước khi gọi.

### Bước 6 — Pha D: semantic (TODO 3/4 — E06, E11 = 11 điểm)

```python
def retrieve_semantic(self, graph_id, query):
    q = cap_query(query)
    try:
        results = self.client.graph.search(graph_id=graph_id, query=q, scope="episodes", limit=8)
    except Exception:
        results = self.client.graph.search(graph_id=graph_id, query=q, scope="nodes", limit=8)
    return render_graph_search(results)
```

**Tại sao `scope="episodes"` và KHÔNG `scope="auto"`:** document `knowledge.jsonl` chứa marker literal ở cuối (`Marker: PAYMENT-RULE-3`, `Marker: CONN-POOL-FIRST`). Scope `episodes` trả **raw document content** → marker nguyên văn. Scope `auto` trả fact đã trích xuất, **có thể bỏ mã literal** — câu trả lời nghe đúng nhưng scorer fail. Đây là điểm khác biệt giữa "search theo nghĩa" và "search theo contract chấm điểm của lab".

**Fallback `nodes`:** một số account/SDK không hỗ trợ episode scope cho standalone graph → bắt exception và thử nodes (node vẫn mang summary chứa marker).

### Bước 7 — Pha E: assemble budget (TODO 4/4 — E07 = 6 điểm)

```python
def assemble_context(self, layers):
    return self.budget.assemble(layers)   # 10/4/3/3 + priority STM→LT→EP→SEM
```

`ContextBudgetManager` với `LAB_CONTEXT_TOKENS=8000`:
- short_term 10% = 800, long_term 4% = 320, episodic 3% = 240, semantic 3% = 240.
- Trim theo **token estimator 4 ký tự/token**, giữ **đầu text** (vì retrieval xếp kết quả quan trọng nhất ở đầu).
- Priority: short_term → long_term → episodic → semantic. Trả `(merged_text, breakdown)`.

**Tại sao E07 cần đúng budget:** E07 mixed cần **cả** `Python` (long-term) **và** `Idempotency-Key` (semantic) trong merged text. Nếu một layer bị trim hết hoặc nối không đúng thứ tự, marker mất → fail. `budget_breakdown` cho biết layer nào bị trim để tối ưu ở **nguồn retrieval**, không tăng budget tùy tiện (tăng budget = che lỗi, bị trừ).

### Bước 8 — Chạy benchmark đầy đủ + baseline + so sánh

```bash
docker compose run --rm app pytest -q
docker compose run --rm app python -m src.evaluate --impl no_memory
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded
docker compose run --rm app python -m src.compare_reports
```

**Tại sao cả 4 lệnh:**
- `pytest`: xác nhận starter kit còn nguyên vẹn (test khóa dataset/router/compaction/budget/privacy). **Xanh không nghĩa là student retrieval xong** — test không chấm 4 TODO.
- `--impl no_memory`: baseline chứng minh **memory có giá trị**. Nó chỉ pass E01/E10 (evidence còn trong thread hiện tại); 9 case cross-session fail → chứng minh thiếu durable memory là thiếu hit rate.
- `--impl student --reuse-seeded`: **bài làm của bạn**, ghi `reports/benchmark.json` + `.md`. Đây là report nộp bài.
- `compare_reports`: tạo `reports/comparison.md` — bắt buộc nộp (2 điểm phân tích).

**Tại sao no-memory có token reduction cao (81.8%) nhưng hit rate thấp (18.2%):** nó "reduction" bằng cách **trả về gần như không có gì**. Giảm context rẻ và dễ, nhưng sai. Token reduction chỉ có ý nghĩa khi đọc **cùng với** evidence hit rate.

> ⚠️ **Bẫy quan trọng:** `--only-layer X` **ghi đè** `reports/benchmark.json` bằng tập con. Luôn chạy lại **full benchmark cuối cùng trước khi nộp** để report có đủ 11 case.

### Bước 9 — Privacy drill (6 điểm)

```bash
# SAU khi đã lưu benchmark đầy đủ
docker compose run --rm app python -m src.forget --user-id minh-lab17
docker compose run --rm app python -m src.forget --user-id minh-lab17 --verify-only
```

**Tại sao thứ tự là bắt buộc:**
1. Xóa user Zep + Redis keys của `minh-lab17`.
2. `--verify-only` in `Zep user absent: True` và `Redis user keys remaining: 0` → bằng chứng xóa sạch (4 điểm).
3. **Semantic graph KHÔNG bị xóa** — nó là domain knowledge dùng chung, không chứa PII user.

**Tại sao không được seed lại trước khi chụp verify:** user vừa xóa sẽ xuất hiện lại → bằng chứng privacy không còn hợp lệ. **Sau khi** chụp ảnh xong mới seed lại để chuẩn bị golden.

**Tại sao phải chạy TRƯỚC golden:** golden cần memory của Minh; nếu bạn forget rồi quên seed, golden fail hàng loạt (mất cả +10).

### Bước 10 — Golden (tùy chọn, +10 hoặc 0)

```bash
# Giảng viên phát data/golden_eval.json (gitignored) — 20 case G01–G20
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden
```

**Tại sao all-or-nothing:** 20/20 mới +10; 19/20 = 0. Giảng viên **re-run bằng file gốc** → không được sửa JSON, không hard-code marker/case ID. Code phải đủ tổng quát để pass 20 case chưa biết.

### Bước 11 — UI demo (tùy chọn, +10)

```bash
make ui   # http://localhost:8501
```

Hoàn thiện hàm duy nhất `retrieve_for_case` trong `src/demo_ui.py`:
1. Load case từ `data/sessions.json` (đã có sẵn).
2. Chọn case → hiện query/layer/user/thread (đã có).
3. Build short-term từ `fixture_messages` (hoặc message của thread đó) + chat history mới; gọi các hàm student theo `expected_layer` (mixed → long_term + semantic); gọi `assemble_context`.
4. Chat tiếp trên đúng `user_id`/`thread_id`, giữ history trong session state.

LLM chỉ dùng cho **câu trả lời chat** (Gemini hoặc OpenRouter), **không bao giờ dùng cho chấm điểm**.

---

## 4. Giải thích chi tiết các bước TEST

### 4.1. `pytest -q` — chạy cái gì, tại sao

| Test | Khóa hành vi gì |
| --- | --- |
| `test_short_term.py` | Sliding compaction phải giữ `REVIEW-DEADLINE-1600`/`Friday`/`16:00`; buffer không compact |
| `test_context_budget.py` | Tỷ lệ 10/4/3/3 đúng; priority STM→LT→EP→SEM đúng |
| `test_dataset.py` | Dataset có đủ 5 loại layer; E09 có `must_not_contain`; marker PAYMENT-RULE-3/CONN-POOL-FIRST tồn tại; golden (nếu có) đúng 20 case |
| `test_privacy.py` | User synthetic opt-in; PII bị redact; user lạ bị từ chối |

**Tại sao "pytest xanh không có nghĩa là xong":** các test này lock **starter kit**, không import 4 hàm student. Bạn có thể để nguyên `NotImplementedError` mà pytest vẫn xanh. Chạy pytest để đảm bảo bạn **không phá starter kit**, còn chất lượng retrieval phải xem `reports/benchmark.json`.

### 4.2. Tại sao seed chỉ 1 lần + `--reuse-seeded`

- `seed` **reset** user (xóa + tạo lại) và **reset** semantic graph. Chạy nhiều lần = xóa dữ liệu đang tốt và mất thời gian chờ index.
- `--reuse-seeded` bỏ qua ingest → đúng trạng thái dữ liệu đã chuẩn bị, evaluate nhanh.
- Ngoại lệ: sau privacy drill, chạy lại seed **một lần** để phục hồi `minh-lab17` trước golden/UI.

### 4.3. Tại sao có 3 impl: `no_memory` / `reference` / `student`

- `reference` = lời giải chuẩn của giảng viên, dùng để **kiểm tra môi trường** (nếu reference fail → lỗi setup, không phải lỗi bạn).
- `student` = code của bạn, **là report nộp bài**.
- `no_memory` = baseline để chứng minh memory tạo ra giá trị (hit rate 18% → 100%).

> Không được nộp report `reference` đổi tên thành `student` (bị phát hiện, 0 điểm khoi đó).

### 4.4. Tại sao phải đọc `reports/benchmark.md` theo thứ tự

1. `passed`/`memory_hit_rate` → tổng quan.
2. `error`, `missing`, `forbidden_found` của từng case FAIL → lỗi nằm ở retrieval hay trimming.
3. `retrieved_tokens`/`token_reduction` → có đang lãng phí budget không.
4. `budget_breakdown` của E07 → layer nào bị trim.
5. Evidence excerpt → kiểm tra marker có nguyên văn không.

### 4.5. Tại sao `cap_query(400)`

Zep Cloud V3 từ chối `graph.search` với query dài hơn 400 ký tự (lỗi HTTP 4xx). Query golden được thiết kế dài hơn để **ép** bạn cap — quên cap = case fail vì exception, dù retrieval logic đúng. `cap_query` cắt ở word boundary gần nhất trong giới hạn.

---

## 5. Các "tại sao" cốt lõi nhất (nếu chỉ nhớ 5 điều)

1. **Scope quyết định mọi thứ:** long-term/episodic dùng `user_id`, semantic dùng `graph_id`, short-term dùng thread. Sai scope = fail cả cụm case (semantic mà search user_id sẽ kéo preference cá nhân vào, hoặc ngược lại).
2. **Marker literal là contract:** chọn scope/limit/render sao cho chuỗi `must_contain_all` xuất hiện **nguyên văn**. `scope="auto"` phá điều này.
3. **Zep bất đồng bộ:** luôn để seed/poll hoàn tất trước khi benchmark; đừng kết luận "code sai" khi dữ liệu chưa index.
4. **Budget 10/4/3/3 là bài học, không phải rào cản:** trim ở nguồn retrieval (cap, giới hạn episode, scope đúng) thay vì tăng `LAB_CONTEXT_TOKENS`.
5. **Recency + scope > preference chung (E08), compaction giữ durable constraint (E10):** đây là hai case "hiểu sâu" được chấm trong README_submission.

---

## 6. Checklist nộp bài

- [ ] `src/memory_student.py`: 4 hàm xong, không còn `NotImplementedError`.
- [ ] `reports/benchmark.json` + `.md`: impl `student`, đủ 11 case, pass ≥ 9.
- [ ] `reports/benchmark_no_memory.md` + `reports/comparison.md`.
- [ ] `README_submission.md` ≤ 400 từ, đủ 3 câu thực hành + 4 câu phân tích + E08/E10.
- [ ] 4 ảnh: `long_term.png`, `episodic.png`, `semantic.png`, `privacy.png`.
- [ ] Privacy: forget + verify-only đã chụp **trước khi** seed lại.
- [ ] KHÔNG commit `.env`, API key, `data/golden_eval.json`.
- [ ] KHÔNG sửa `tests/`, `evaluate.py`, `memory_reference.py`, ground truth.
- [ ] Lần chạy `--impl student` cuối cùng là **full 11 case** (không phải `--only-layer`).
