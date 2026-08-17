# Case Study — G20: Mixed Memory (Short-term + Long-term + Semantic)

Tài liệu này mổ xẻ **case G20** trong golden set (20 case ẩn, all-or-nothing +10): luồng xử lý từng bước,
evidence thật của từng layer, ý nghĩa của **từng con số** trong report, và cách demo lại.

---

## 1. Case G20 là gì

```json
{
  "id": "G20",
  "expected_layer": "mixed",
  "retrieve_layers": ["short_term", "long_term", "semantic"],
  "user_id": "minh-lab17",
  "thread_id": "eval-g20-v3",
  "after_stage": 3,
  "query": "Trong thread nay minh vua nhac constraint gio standup. Lat nua minh se them retry
           payment vao dung backend du an cong ty. Ghep ba manh: constraint standup con hieu luc
           trong thread, stack bat buoc cua backend cong ty, va cach danh dau request payment
           de khong trung don.",
  "must_contain_all": ["HOLD-ALPHA-0900", "NestJS", "Idempotency-Key"],
  "must_not_contain": ["LOTUS-88"]
}
```

**G20 là case duy nhất trong G13–G20 yêu cầu 3 layer cùng lúc** — mỗi marker đến từ **một layer khác nhau**:

| Marker | Layer cung cấp | Nguồn gốc |
| --- | --- | --- |
| `HOLD-ALPHA-0900` | **short_term** | Constraint trong `fixture_messages` của chính thread đánh giá |
| `NestJS` | **long_term** | Fact/Context Block của BLUEBIRD-42 (stage 3) |
| `Idempotency-Key` | **semantic** | Document `kb-payment-retry` (PAYMENT-RULE-3) |

`must_not_contain: ["LOTUS-88"]` kiểm tra **user isolation**: chỉ lấy memory của Minh, không được lẫn
project của Lan.

Ngoài ra G20 còn có `fixture_messages` — **14 message mô phỏng thread dài** (1 constraint + 1 lời xác nhận
+ 12 filler), thiết kế để ép **compaction** phải giữ constraint khi 12 filler bị evict.

---

## 2. Luồng xử lý (từng bước trong code)

### Bước 0 — Evaluator đọc case
`src/evaluate.py` → `run_case(case, dataset, memory_impl)`. Vì `expected_layer == "mixed"` nên nó không
chạy một hàm duy nhất mà dựng **dict 4 layer** theo `retrieve_layers`:

```python
wanted = case.get("retrieve_layers") or ["long_term", "semantic"]   # G20: 3 layer
layers = {"short_term": "", "long_term": "", "episodic": "", "semantic": ""}
if "short_term" in wanted:  layers["short_term"], _ = short_term_text(case, dataset)
if "long_term"  in wanted:  layers["long_term"]  = memory_impl.retrieve_long_term(...)
if "episodic"   in wanted:  layers["episodic"]   = memory_impl.retrieve_episodic(...)
if "semantic"   in wanted:  layers["semantic"]   = memory_impl.retrieve_semantic(settings.semantic_graph_id, ...)
retrieved, budget_breakdown = memory_impl.assemble_context(layers)
```

### Bước 1 — Layer short_term (local, không gọi Zep)
`short_term_text` dựng `ShortTermMemory(strategy="sliding", max_recent_messages=6, pressure_tokens=450)`
và `add` từng message trong `fixture_messages`.

- `detect_pressure`: số message > 6 → compact ngay.
- 14 message → **8 lần compact** (message thứ 7→14, mỗi lần giữ lại 6 turn gần nhất).
- `extract_durable_notes` quét từng message cũ, chỉ "thăng cấp" message chứa từ khoá
  (`todo`, `deadline`, `constraint`, `decision`, `must`...) **hoặc** mã viết hoa (`HOLD-ALPHA-0900`).
  → cả 2 message về constraint (`HOLD-ALPHA-0900...` và `Noted standup constraint.`) thành durable notes.
- Render = `SESSION_SUMMARY + DURABLE_NOTES + RECENT_TURNS` → **marker `HOLD-ALPHA-0900` nằm trong durable notes**, không phụ thuộc 6 turn gần nhất.

### Bước 2 — Layer long_term (Zep)
`retrieve_long_term(user_id="minh-lab17", thread_id="eval-g20-v3", query)`:

1. `prime_eval_thread`: xoá thread cũ `eval-g20-v3`, tạo mới, thêm query với `ignore_roles=["user"]`
   (query **không** thành memory).
2. `thread.get_user_context(thread_id=...)` → **Context Block** (user summary + episodes + facts).
3. Bonus: `graph.search(user_id=..., scope="edges", limit=20)` → các **fact edge** kèm
   `valid_at`/`invalid_at` (recency/provenance).
4. Trả về **facts trước, Context Block sau** — vì fact nhỏ gọn và được rank theo query, marker nằm
   trong cửa sổ 4% budget. `NestJS` xuất hiện ở cả 2 nguồn (redundant evidence).

### Bước 3 — Layer semantic (Zep standalone graph)
`retrieve_semantic(graph_id="vinuni-lab17-domain-kb", query)`:

1. `graph.search(graph_id=..., scope="episodes", limit=8)` — raw document content.
2. `_render_semantic_episodes`: mỗi doc được ingest **2 lần** (JSON + text summary) → trích trường
   `summary` từ JSON và **dedupe** cặp trùng → 4 doc ≈ 97 token, khớp budget 240 không cần trim.
3. `Idempotency-Key` nằm trong summary của `kb-payment-retry` (kèm marker `PAYMENT-RULE-3`).

### Bước 4 — assemble_context (budget 10/4/3/3)
`ContextBudgetManager` với `LAB_CONTEXT_TOKENS=8000`:

| Layer | Tỷ lệ | Limit (token) | = ký tự |
| --- | --- | ---: | ---: |
| short_term | 10% | 800 | 3200 |
| long_term | 4% | 320 | 1280 |
| episodic | 3% | 240 | 960 |
| semantic | 3% | 240 | 960 |

Thứ tự priority: **short_term → long_term → episodic → semantic**. Layer vượt budget bị trim theo
chiến lược **giữ đầu + giữ đuôi** (70/30) — vì marker có thể nằm ở đuôi (fact cuối, marker cuối doc).
Kết quả: merged text có dạng:

```text
<SHORT_TERM> ... </SHORT_TERM>

<LONG_TERM> ... </LONG_TERM>

<SEMANTIC> ... </SEMANTIC>
```

### Bước 5 — score_case
`normalize` (hạ hoa thường + gộp khoảng trắng) rồi kiểm tra:
- `HOLD-ALPHA-0900` ∈ merged ✓ (short_term durable notes)
- `NestJS` ∈ merged ✓ (long_term facts + Context Block)
- `Idempotency-Key` ∈ merged ✓ (semantic)
- `LOTUS-88` ∉ merged ✓ (chỉ search user-scoped + graph_id dùng chung không chứa project cá nhân)
→ **PASS**.

---

## 3. Evidence thật của từng layer (trích từ chạy live)

**Short-term (169 token — không cần trim):**
```text
<SESSION_SUMMARY>
user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. | assistant: Noted standup constraint. | ... filler ...
</SESSION_SUMMARY>
<DURABLE_NOTES>
- user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten.
- assistant: Noted standup constraint.
</DURABLE_NOTES>
<RECENT_TURNS> ... 6 filler cuối ... </RECENT_TURNS>
```

**Long-term (1403 token raw → trim còn 325):**
```text
FACT: Minh Nguyen requires NestJS for the BLUEBIRD-42 project backend.
      [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z]
FACT: Minh Nguyen requires TypeScript for the BLUEBIRD-42 project backend. [...]
FACT: Minh Nguyen is forbidden from using Python for the backend of the BLUEBIRD-42 project. [...]
... + Context Block (USER_SUMMARY: "backend must use TypeScript with NestJS" ...)
```

**Semantic (97 token — không cần trim):**
```text
EPISODE: For POST /payments, every retryable request MUST send the same Idempotency-Key.
Retry only HTTP 429 or transient 5xx errors, use exponential-backoff, and stop after
max-3-retries. Marker: PAYMENT-RULE-3.
EPISODE: Do not persist personal data without explicit opt-in. ... Marker: DELETE-VERIFY-ALL.
```

> Chú ý quirk của Zep: fact `NestJS` có `invalid_at=08:00:20Z` (20 giây sau) — vì message xác nhận của
> assistant ("Da tach scope...") khiến Zep đánh dấu fact cũ hết hiệu lực. **Marker vẫn được chấm** vì
> (1) fact edge vẫn trả về text chứa "NestJS", và (2) Context Block USER_SUMMARY cũng lặp lại
> "must use TypeScript with NestJS" — **redundancy giữa edges và Context Block là cần thiết**.

---

## 4. Giải thích các con số (từ `reports/golden_benchmark.json`)

### 4.1. Budget breakdown

```json
"budget_breakdown": {
  "short_term": { "limit_tokens": 800, "raw_tokens": 169, "used_tokens": 169 },
  "long_term":   { "limit_tokens": 320, "raw_tokens": 1403, "used_tokens": 325 },
  "episodic":    { "limit_tokens": 240, "raw_tokens": 0,    "used_tokens": 0 },
  "semantic":    { "limit_tokens": 240, "raw_tokens": 97,   "used_tokens": 97 }
}
```

- **short_term 169/800**: fixture nhỏ, không vượt budget → không trim. Số 169 = 1 summary + 2 durable
  notes + 6 recent turns (ước lượng 4 ký tự/token).
- **long_term 1403 → 325**: Context Block của Zep rất dài (~735 token) + 20 fact edges (~590 token).
  Vượt 320 → trim giữ đầu 70% (896 ký tự) + đuôi 30% (384 ký tự) + nhãn `[...trimmed...]` (~5 token)
  → `used_tokens = 325` (lớn hơn limit 320 một chút vì overhead nhãn trim).
- **semantic 97/240**: sau khi dedupe JSON/text chỉ còn 4 summary → khớp budget, không trim.
- **episodic 0/240**: `retrieve_layers` của G20 **không yêu cầu** episodic → layer bỏ trống.
  (So sánh: G19 cần episodic nên raw_tokens ≠ 0.)

### 4.2. Latency: 1641.3 ms

| Call | Ước lượng | Ghi chú |
| --- | ---: | --- |
| `prime_eval_thread` (delete + create + add_messages) | ~200–400 ms | Thao tác thread |
| `get_user_context` | ~600–900 ms | Call đắt nhất — Zep tổng hợp graph |
| `graph.search(edges, limit=20)` | ~200–400 ms | Fact edges |
| `graph.search(graph_id, episodes)` | ~200–300 ms | Semantic |
| `ShortTermMemory.add × 14` (local) | ~0.1–0.4 ms | Không gọi mạng |

Tổng ~1.6s — **dominated bởi long-term** (2–3 call Zep). So với case long_term thuần (G03–G06:
~1.2–1.4s) thì G20 thêm semantic search nên cao hơn chút.

### 4.3. Token: 610 retrieved / 632 full source / reduction 3.5%

- `full_source_tokens = 632`: toàn bộ message của Minh tới stage 3 **+ toàn bộ `knowledge.jsonl`**
  (4 document) — tức là "nếu không có memory, agent phải nhét hết mọi thứ vào context".
- `retrieved_tokens = 610`: merged context thực tế (169 + 325 + 97 + tag `<LAYER>` + separator).
- `token_reduction = 3.5%` — **rất thấp**, vì:
  1. G20 phải phủ **3 layer** nên context phải chứa nhiều thứ (không thể cắt mạnh).
  2. Layer long_term chiếm phần lớn budget (325/610 ≈ 53%) nhưng raw tới 1403 — trim chỉ giảm được
     ~77% của nó.
- **Bài học:** token reduction thấp KHÔNG phải là lỗi. Quan trọng là **hit rate**: cả 3 marker đều
  phải có mặt. (Ngược lại, no-memory có reduction ~82% nhưng chỉ pass 2/11 — cắt hết thì rẻ nhưng sai.)

### 4.4. short_term_stats: `{messages_kept: 6, durable_notes: 2, compactions: 8}`

- 14 message đầu vào, `max_recent_messages=6` → 8 lần compact (message thứ 7→14).
- Mỗi lần compact giữ **6 turn gần nhất**, các turn cũ bị nén vào summary/durable notes.
- `durable_notes: 2` = `HOLD-ALPHA-0900...` (có mã viết hoa + từ "Constraint") và
  `Noted standup constraint.` (từ "constraint"). Dù 12 filler bị evict, constraint vẫn còn → marker PASS.

---

## 5. Cách demo lại case G20

### 5.1. Demo terminal (chạy đúng benchmark)

```bash
# (bắt buộc nếu graph chưa seed hoặc muốn sạch)
docker compose run --rm app python -m src.seed

# Chạy full golden — quan sát dòng G20
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden
# => G20 mixed: ... PASS  ~1.6s

# Hoặc chỉ chạy nhóm mixed (E07 + G11-G20) để thấy G20 cạnh các case mixed khác
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --only-layer mixed
```

**Xem chi tiết số liệu:**
```bash
# mở reports/golden_benchmark.json → tìm "G20" → đọc budget_breakdown, latency_ms, retrieved
```

### 5.2. Demo từng layer (script chạy live)

```bash
docker compose run --rm app python - <<'EOF'
import json
from src.memory_student import StudentMemory
from src.short_term import ShortTermMemory
from src.zep_common import get_zep_client
from src.config import settings

case = next(e for e in json.load(open('data/golden_eval.json', encoding='utf-8'))['evaluations']
            if e['id'] == 'G20')
mem = StudentMemory(get_zep_client())

stm = ShortTermMemory(strategy='sliding', max_recent_messages=6, pressure_tokens=450)
for m in case['fixture_messages']:
    stm.add(m['role'], m['content'])
print('SHORT_TERM:\n', stm.render())
print('\nLONG_TERM:\n', mem.retrieve_long_term(case['user_id'], case['thread_id'], case['query'])[:800])
print('\nSEMANTIC:\n', mem.retrieve_semantic(settings.semantic_graph_id, case['query']))
EOF
```

### 5.3. Demo UI (bonus +10)

```bash
make ui   # mở http://localhost:8501
```

1. Sidebar chọn **`G20 · mixed · minh-lab17`** → card hiện query, layer, user, thread.
2. Bấm **▶️ Run retrieval** → quan sát:
   - 3 badge layer: `short_term`, `long_term`, `semantic` (episodic không sáng — đúng vì không được yêu cầu).
   - 4 ô metric token: short_term ~169, long_term ~325, semantic ~97, episodic 0.
   - Merged context: `<SHORT_TERM>` → `<LONG_TERM>` → `<SEMANTIC>` theo đúng priority.
3. Chat tiếp ví dụ: *"Giờ standup mấy giờ?"* → assistant trả lời grounded bằng OpenRouter/Gemini,
   dựa trên retrieved context (history giữ trong session state).

### 5.4. Checklist quan sát khi demo

- [ ] 3 marker `HOLD-ALPHA-0900`, `NestJS`, `Idempotency-Key` đều có trong merged context.
- [ ] `LOTUS-88` **không** xuất hiện (isolation).
- [ ] Durable notes giữ constraint sau 8 lần compaction.
- [ ] long_term bị trim (1403 → 325) nhưng `NestJS` vẫn còn (facts đầu + Context Block).
- [ ] episodic = 0 token vì G20 không yêu cầu.

---

## 6. Điểm học được từ G20

1. **Một query có thể cần nhiều layer** — G20 tách rõ 3 mảnh: thread (short-term), user (long-term),
   domain (semantic). Router/dataset quyết định layer nào được gọi.
2. **Scope là tường lửa**: short-term đọc fixture của đúng thread, long-term chỉ user `minh-lab17`,
   semantic chỉ `graph_id` dùng chung → `LOTUS-88` (của Lan) không bao giờ lọt vào.
3. **Compaction ≠ mất thông tin**: 12 filler bị evict nhưng constraint (có dấu hiệu durable) được
   thăng cấp lên durable notes.
4. **Trim phải giữ cả 2 đầu**: marker có thể nằm ở đuôi (fact cuối, cuối doc) — head-trim thuần sẽ
   làm mất `NestJS`/`Idempotency-Key` trong các trường hợp tương tự.
5. **Redundancy là bạn của retrieval**: `NestJS` xuất hiện ở cả fact edges lẫn USER_SUMMARY của
   Context Block — kể cả khi Zep đánh dấu fact `invalid_at`, marker vẫn còn.
6. **Token reduction thấp không đáng lo**: G20 cần 3 layer nên context phải đủ rộng (3.5% reduction);
   chỉ số quyết định là **hit rate** (3/3 marker) — không phải càng cắt nhiều càng tốt.
