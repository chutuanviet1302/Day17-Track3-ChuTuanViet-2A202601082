# Lab 17 Golden Set Report

- Implementation: `student`
- Kind: `golden`
- Cases: **20**
- Passed: **20/20**
- Evidence hit rate: **100.0%**
- Average retrieval latency: **999.0 ms**
- Average token reduction vs full source context: **17.4%**
- Golden bonus: **10/10** (100% required)

| Case | Layer | Pass | Latency ms | Retrieved tokens | Token reduction | Missing / Error |
| --- | --- | --- | ---: | ---: | ---: | --- |
| G01 | short_term | PASS | 0.2 | 227 | 0.0% |  |
| G02 | short_term | PASS | 0.1 | 133 | 0.0% |  |
| G06 | long_term | PASS | 1303.2 | 656 | 0.0% |  |
| G09 | semantic | PASS | 230.6 | 148 | 67.8% |  |
| G10 | semantic | PASS | 226.5 | 95 | 79.3% |  |
| G14 | mixed | PASS | 1594.4 | 431 | 0.0% |  |
| G03 | long_term | PASS | 1220.0 | 1405 | 0.0% |  |
| G04 | long_term | PASS | 1365.0 | 1410 | 0.0% |  |
| G07 | episodic | PASS | 282.8 | 159 | 28.1% |  |
| G08 | episodic | PASS | 327.6 | 202 | 8.6% |  |
| G11 | mixed | PASS | 1524.6 | 440 | 22.1% |  |
| G13 | mixed | PASS | 466.9 | 359 | 36.5% |  |
| G15 | mixed | PASS | 1790.0 | 683 | 0.0% |  |
| G16 | mixed | PASS | 2006.4 | 485 | 14.2% |  |
| G17 | mixed | PASS | 1549.5 | 485 | 14.2% |  |
| G18 | mixed | PASS | 440.5 | 349 | 38.2% |  |
| G19 | mixed | PASS | 1519.6 | 538 | 4.8% |  |
| G05 | long_term | PASS | 1358.6 | 1388 | 0.0% |  |
| G12 | mixed | PASS | 1399.0 | 431 | 31.8% |  |
| G20 | mixed | PASS | 1374.8 | 610 | 3.5% |  |

## Evidence excerpts

### G01 - short_term

`<SESSION_SUMMARY> user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. | assistant: Noted standup constraint. | user: Constraint HOLD-BETA-STAGING: writes go to staging DB only. | assistant: Noted staging constraint. | user: Filler A about button padding. | assistant: Filler A. | user: Filler B about color tokens. | assistant: Filler B. | user: Filler C about copy tone. | assistant: Filler C. </SESSION_SUMMARY> <DURABLE_NOTES> - user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. - assistant: Noted standup constraint. - user: Constraint HOLD-BETA-STAGING: writes go to staging DB only. - assistant: Noted staging constraint. </DURA`

### G02 - short_term

`<RECENT_TURNS> user: Ten du an ca nhan cua toi la ORCHID-27. Toi thich Python va khong thich Java. Khi giai thich code, hay dung vi du ngan. assistant: Da hieu: demo ca nhan ORCHID-27, uu tien Python, tranh Java, vi du ngan. user: Toi dang hoc async/await va hay nham coroutine voi Task. Neu sau nay gap chu de nay, hay giai thich bang timeline. assistant: Toi se uu tien timeline khi giai thich coroutine va Task. user: TODO: hoan thanh benchmark report truoc thu Sau luc 16:00. Day la open loop LAB-REPORT-1600. </RECENT_TURNS>`

### G06 - long_term

`FACT: Lan Tran does not use Python in the LOTUS-88 backend example. [valid_at=2026-08-01T11:00:00Z, invalid_at=None] FACT: Lan Tran's project is LOTUS-88. [valid_at=2026-08-01T11:00:00Z, invalid_at=None] FACT: Lan Tran prefers Spring Boot for the LOTUS-88 project. [valid_at=2026-08-01T11:00:00Z, invalid_at=2026-08-01T11:00:20Z] FACT: Lan Tran prefers Java for the LOTUS-88 project. [valid_at=2026-08-01T11:00:00Z, invalid_at=2026-08-01T11:00:20Z]  <USER_SUMMARY> Lan's project is LOTUS-88. They prioritize Java and Spring Boot for backend development.  Lan prefers not to use Python in the backend. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection ord`

### G09 - semantic

`EPISODE: Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL. EPISODE: For POST /payments, every retryable request MUST send the same Idempotency-Key. Retry only HTTP 429 or transient 5xx errors, use exponential-backoff, and stop after max-3-retries. Marker: PAYMENT-RULE-3. EPISODE: Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, episodic 3 percent, semantic 3 percent; trim lower-priority memory first. Marker: BUDGET-10-4-3-3.`

### G10 - semantic

`EPISODE: Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL. EPISODE: Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, episodic 3 percent, semantic 3 percent; trim lower-priority memory first. Marker: BUDGET-10-4-3-3.`

### G14 - mixed

`<LONG_TERM> FACT: Lan Tran does not use Python in the LOTUS-88 backend example. [valid_at=2026-08-01T11:00:00Z, invalid_at=None] FACT: Lan Tran's project is LOTUS-88. [valid_at=2026-08-01T11:00:00Z, invalid_at=None] FACT: Lan Tran prefers Spring Boot for the LOTUS-88 project. [valid_at=2026-08-01T11:00:00Z, invalid_at=2026-08-01T11:00:20Z] FACT: Lan Tran prefers Java for the LOTUS-88 project. [valid_at=2026-08-01T11:00:00Z, invalid_at=2026-08-01T11:00:20Z]  <USER_SUMMARY> Lan's project is LOTUS-88. They prioritize Java and Spring Boot for backend development.  Lan prefers not to use Python in the backend. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in s`

### G03 - long_term

`FACT: Minh Nguyen still prefers Python for personal demos like ORCHID-27. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: demo ca nhan ORCHID-27 prioritizes Python. [valid_at=2026-08-01T09:00:20Z, invalid_at=2026-08-05T08:00:20Z] FACT: Minh Nguyen likes Python. [valid_at=2026-08-01T09:00:00Z, invalid_at=2026-08-01T09:00:20Z] FACT: Minh Nguyen does not like Java. [valid_at=2026-08-01T09:00:00Z, invalid_at=2026-08-01T09:00:20Z] FACT: demo ca nhan ORCHID-27 avoids Java. [valid_at=2026-08-01T09:00:20Z, invalid_at=None] FACT: Minh Nguyen is learning async/await. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen suggests setting concurrency to 20. [valid_at=`

### G04 - long_term

`FACT: Minh Nguyen needs to complete the benchmark report before Friday at 16:00. This is an open loop, LAB-REPORT-1600. [valid_at=2026-08-01T09:04:00Z, invalid_at=None] FACT: Minh Nguyen often confuses coroutine with Task. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen is learning async/await. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen often confuses coroutine with Task. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen suggests setting concurrency to 20. [valid_at=2026-08-03T10:03:00Z, invalid_at=2026-08-03T10:03:20Z] FACT: If Minh Nguyen encounters the topic of async/await later, they request an explanation via a timeline. [valid`

### G07 - episodic

`EPISODE: Voi demo ca nhan cua Minh, ngon ngu uu tien la gi? EPISODE: Hom nay toi debug async HTTP. Toi da thu tang timeout len 60s nhung van fail. EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh la connection churn, khong phai timeout threshold. Ma su co ASYNC-FIX-20. EPISODE: Da ghi nhan trajectory: increase timeout khong hieu qua; ClientSession + concurrency=20 giai quyet connection churn. EPISODE: Sep hoi chuan hoa backend du an cong ty, minh hay lan voi stack project rieng. Rieng du an cong ty cua Minh: bat buoc ngon ngu va framework nao? Python ca nhan co duoc dung backend`

### G08 - episodic

`EPISODE: Ten du an ca nhan cua toi la ORCHID-27. Toi thich Python va khong thich Java. Khi giai thich code, hay dung vi du ngan. EPISODE: Toi dang hoc async/await va hay nham coroutine voi Task. Neu sau nay gap chu de nay, hay giai thich bang timeline. EPISODE: Cuoi tuan minh ngoi mot minh lam demo rieng, khong hop team. Truoc khi chon template, nhac lai: khi lam viec ca nhan minh uu tien ngon ngu nao, va ma du an demo ca nhan la gi? Chi  EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh la connection churn, khong phai timeout threshold. Ma su co ASYNC-FIX-20. EPISODE: Sep hoi chuan hoa backend du an cong ty, minh hay lan voi stack project rie`

### G11 - mixed

`<LONG_TERM> FACT: Minh Nguyen increased the timeout to 60s. [valid_at=2026-08-03T10:00:00Z, invalid_at=2026-08-03T10:03:00Z] FACT: Minh Nguyen failed to debug async HTTP even after increasing the timeout to 60s. [valid_at=2026-08-03T10:00:00Z, invalid_at=2026-08-03T10:03:00Z] FACT: Minh Nguyen is learning async/await. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen is debugging async HTTP. [valid_at=2026-08-03T10:00:00Z, invalid_at=None] FACT: Minh Nguyen likes Python. [valid_at=2026-08-01T09:00:00Z, invalid_at=2026-08-01T09:00:20Z] FACT: demo ca nhan ORCHID-27 prioritizes Python. [valid_at=2026-08-01T09:00:20Z, invalid_at=2026-08-05T08:00:20Z] FACT: demo ca nhan ORCHID-27`

### G13 - mixed

`<EPISODIC> EPISODE: Cuoi tuan minh ngoi mot minh lam demo rieng, khong hop team. Truoc khi chon template, nhac lai: khi lam viec ca nhan minh uu tien ngon ngu nao, va ma du an demo ca nhan la gi? Chi  EPISODE: Mai hop mentor, toi nay minh muon don open-loop. Liet ke viec chua dong, deadline, va ma dinh danh task. Can du ba manh de ghi vao note hop. EPISODE: Hom nay toi debug async HTTP. Toi da thu tang timeout len 60s nhung van fail. EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh la connection churn, khong phai timeout threshold. Ma su co ASYNC-FIX-20. EPISODE: Sep hoi chuan hoa backend du an cong ty, minh hay lan voi stack project rieng. R`

### G15 - mixed

`<LONG_TERM> FACT: Minh Nguyen is debugging async HTTP. [valid_at=2026-08-03T10:00:00Z, invalid_at=None] FACT: Minh Nguyen failed to debug async HTTP even after increasing the timeout to 60s. [valid_at=2026-08-03T10:00:00Z, invalid_at=2026-08-03T10:03:00Z] FACT: demo ca nhan ORCHID-27 prioritizes Python. [valid_at=2026-08-01T09:00:20Z, invalid_at=2026-08-05T08:00:20Z] FACT: If Minh Nguyen encounters the topic of async/await later, they request an explanation via a timeline. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen is learning async/await. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen increased the timeout to 60s. [valid_at=2026-08-03T10:00:00Z, i`

### G16 - mixed

`<LONG_TERM> FACT: Minh Nguyen needs to complete the benchmark report before Friday at 16:00. This is an open loop, LAB-REPORT-1600. [valid_at=2026-08-01T09:04:00Z, invalid_at=None] FACT: Lab Assistant checks concurrency. [valid_at=2026-08-03T10:01:00Z, invalid_at=None] FACT: The benchmark report is an open loop LAB-REPORT-1600. [valid_at=2026-08-01T09:04:00Z, invalid_at=None] FACT: Minh Nguyen is learning async/await. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Lab Assistant prioritizes the timeline when explaining coroutine. [valid_at=2026-08-01T09:02:20Z, invalid_at=None] FACT: Minh Nguyen is debugging async HTTP. [valid_at=2026-08-03T10:00:00Z, invalid_at=None] FACT: Lab Assist`

### G17 - mixed

`<LONG_TERM> FACT: Minh Nguyen often confuses coroutine with Task. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen often confuses coroutine with Task. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: If Minh Nguyen encounters the topic of async/await later, they request an explanation via a timeline. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Minh Nguyen is debugging async HTTP. [valid_at=2026-08-03T10:00:00Z, invalid_at=None] FACT: Minh Nguyen is learning async/await. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: Lab Assistant prioritizes the timeline when explaining coroutine. [valid_at=2026-08-01T09:02:20Z, invalid_at=None] FACT: Minh Nguyen su`

### G18 - mixed

`<EPISODIC> EPISODE: Cuoi tuan minh ngoi mot minh lam demo rieng, khong hop team. Truoc khi chon template, nhac lai: khi lam viec ca nhan minh uu tien ngon ngu nao, va ma du an demo ca nhan la gi? Chi  EPISODE: Voi demo ca nhan cua Minh, ngon ngu uu tien la gi? EPISODE: Mai hop mentor, toi nay minh muon don open-loop. Liet ke viec chua dong, deadline, va ma dinh danh task. Can du ba manh de ghi vao note hop. EPISODE: Toi nay minh viet tool ca nhan de tai hien su co HTTP roi sua dung playbook. Can ba manh: ngon ngu minh thich khi lam mot minh, ma su co async lan truoc, va buoc playbook truoc khi EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh `

### G19 - mixed

`<LONG_TERM> FACT: Minh Nguyen is debugging async HTTP. [valid_at=2026-08-03T10:00:00Z, invalid_at=None] FACT: Minh Nguyen suggests that reusing aiohttp ClientSession is an effective approach. [valid_at=2026-08-03T10:03:00Z, invalid_at=None] FACT: Minh Nguyen failed to debug async HTTP even after increasing the timeout to 60s. [valid_at=2026-08-03T10:00:00Z, invalid_at=2026-08-03T10:03:00Z] FACT: Minh Nguyen is learning async/await. [valid_at=2026-08-01T09:02:00Z, invalid_at=None] FACT: demo ca nhan ORCHID-27 prioritizes Python. [valid_at=2026-08-01T09:00:20Z, invalid_at=2026-08-05T08:00:20Z] FACT: demo ca nhan ORCHID-27 avoids Java. [valid_at=2026-08-01T09:00:20Z, invalid_at=None] FACT: If M`

### G05 - long_term

`FACT: Minh Nguyen is forbidden from using Python for the backend of the BLUEBIRD-42 project. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: Minh Nguyen requires TypeScript for the BLUEBIRD-42 project backend. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: Minh Nguyen requires NestJS for the BLUEBIRD-42 project backend. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: Minh Nguyen still prefers Python for personal demos like ORCHID-27. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: Minh Nguyen likes Python. [valid_at=2026-08-01T09:00:00Z, invalid_at=2026-08-01T09:00:20Z] FACT: demo ca nhan ORCHID-27 p`

### G12 - mixed

`<LONG_TERM> FACT: Minh Nguyen requires NestJS for the BLUEBIRD-42 project backend. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: Minh Nguyen requires TypeScript for the BLUEBIRD-42 project backend. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: Minh Nguyen is forbidden from using Python for the backend of the BLUEBIRD-42 project. [valid_at=2026-08-05T08:00:00Z, invalid_at=2026-08-05T08:00:20Z] FACT: BLUEBIRD-42 uses TypeScript/NestJS. [valid_at=2026-08-05T08:00:20Z, invalid_at=None] FACT: Minh Nguyen needs to complete the benchmark report before Friday at 16:00. This is an open loop, LAB-REPORT-1600. [valid_at=2026-08-01T09:04:00Z, invalid_at=`

### G20 - mixed

`<SHORT_TERM> <SESSION_SUMMARY> user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. | assistant: Noted standup constraint. | user: Filler about dashboard widgets. | assistant: Filler. | user: Filler about CSS variables. | assistant: Filler. | user: Filler about copy review. | assistant: Filler. </SESSION_SUMMARY> <DURABLE_NOTES> - user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. - assistant: Noted standup constraint. </DURABLE_NOTES> <RECENT_TURNS> user: Filler about empty charts. assistant: Filler. user: Filler about telemetry. assistant: Filler. user: Filler about a11y labels. assistant: Filler. </RECENT_TURNS> </SHORT_TERM>`
