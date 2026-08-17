# README_submission.md — Lab 17 Multi-Memory Agent (Zep)

**Result:** practice **11/11 PASS (100% hit rate)**; no-memory baseline **2/11 (18.2%)**.
Artifacts: `reports/benchmark.{md,json}`, `reports/benchmark_no_memory.md`, `reports/comparison.md`,
screenshots `submission/{long_term,episodic,semantic,privacy}.png`.

## 1. Most important layer in this test set — long-term
Long-term memory decides the most cases: E02, E03, E08, E09 (4/11, 20/56 points).
It is the only layer exercised across cross-session preference (E02), open-loop recall (E03),
recency (E08) and user isolation (E09) at once. Every other layer appears at most twice.

## 2. Zep Context Block vs Redis+Qdrant
Zep gives managed graph extraction, cross-thread Context Block, and scoped search
(`user_id` vs `graph_id`) with provenance, so four layers work without building an extractor.
Redis+Qdrant needs manual schema, TTL and a HashingVectorizer, plus my own compaction.
Self-hosted wins on control, no API dependency and auditability; Zep wins on convenience and
semantic quality, costing ~771 ms average retrieval latency.

## 3. Memory-poisoning guardrails
Scope is the main gate: long-term/episodic always pass `user_id`, semantic always passes
`graph_id`, so Lan never receives Minh's facts (E09 passes its `must_not_contain`).
Durable writes keep scope/source/timestamp/validity (MEMORY_SCHEMA.md); short-term compaction
promotes only messages with durable markers (TODO/deadline/constraint) or uppercase codes;
heartbeat can mark stale tasks but never grants new instructions/permissions.

## 4. Benchmark analysis
- **Weakest layer:** none failed (11/11). Long-term is most fragile: it retrieves the most
  tokens (E03 = 1417) and sits closest to its 4% budget, so a slightly longer Context Block
  would trim evidence first.
- **Most tokens:** E03 open-loop query (1417 tokens; the Context Block re-emits full user context).
- **E07 mixed:** long-term (Minh prefers Python) + semantic (payment retry with Idempotency-Key);
  both markers are mandatory evidence.
- **Token reduction:** memory 14.2% vs no-memory 81.8%. No-memory "reduces" by retrieving
  nothing — cheap but 2/11 PASS. Reduction is only meaningful together with hit rate.
- **E08 recency:** the BLUEBIRD-42 constraint (TypeScript/NestJS) overrides the generic Python
  preference for that project only; provenance keeps Python valid for ORCHID-27.
- **E10 compaction:** sliding window evicts 10 filler turns yet durable notes preserve
  REVIEW-DEADLINE-1600 (Friday 16:00); a plain buffer would grow unboundedly and exceed budget.

## 5. Privacy
`src.forget --user-id minh-lab17` deleted the Zep user and 3 Redis keys;
`--verify-only` confirms `Zep user absent: True` and `Redis user keys remaining: 0`.
The shared semantic KB is untouched (domain knowledge, not user PII).
