from __future__ import annotations

import json
import re
from typing import Any

from .config import settings
from .context_budget import ContextBudgetManager
from .utils import cap_query, estimate_tokens, join_nonempty
from .zep_common import prime_eval_thread, render_graph_search


class StudentMemory:
    """Only this file needs to be edited by students."""

    def __init__(self, client: Any):
        self.client = client
        self.budget = ContextBudgetManager(settings.context_tokens)

    # NOTE: Zep rejects graph.search queries longer than 400 characters. Some
    # eval queries are longer than that, so wrap every query with
    # `cap_query(query)` (see src/utils.py) before passing it to graph.search.

    def retrieve_long_term(self, user_id: str, thread_id: str, query: str) -> str:
        # LAB TODO 1/4
        # 1) prime_eval_thread(...) has already been provided as scaffolding.
        # 2) call thread.get_user_context(thread_id=...)
        # 3) return the .context string.
        # Bonus: append graph.search(scope="edges", limit>=20) facts with
        #        validity ranges (a low limit can miss deadline/open-loop facts).
        prime_eval_thread(self.client, user_id, thread_id, query)

        # Context Block: Zep assembles the user's relevant long-term context
        # (preferences, facts, open loops) from the user graph, scoped to the
        # user of this thread. This is the primary long-term evidence source.
        user_context = self.client.thread.get_user_context(thread_id=thread_id)
        context_block = getattr(user_context, "context", "") or ""

        # Bonus: also search the user's fact edges (scope="edges"). Facts carry
        # valid_at/invalid_at so deadline and open-loop entries are not lost
        # when the Context Block is terse. Search stays user-scoped, so it can
        # never leak another user's memory (E09 isolation).
        try:
            facts = self.client.graph.search(
                user_id=user_id,
                query=cap_query(query),
                scope="edges",
                limit=20,
            )
            fact_text = render_graph_search(facts)
        except Exception:
            fact_text = ""

        # Facts first: edge facts are compact and ranked for the query, so
        # marker-bearing facts (open loops like LAB-REPORT-1600, preferences,
        # validity ranges) survive inside the 4% long-term budget. The Context
        # Block still follows as the primary long-term source.
        return join_nonempty([fact_text, context_block], sep="\n\n")

    @staticmethod
    def _render_episodic_evidence(results: Any) -> str:
        """Render user episodes, keeping marker-bearing evidence inside budget.

        Zep indexes every ingested message, and priming the evaluation thread
        can leave the query text itself in the user graph as an episode. Those
        fragments are long question texts (or contain "?") with no uppercase
        code, and they crowd out the short marker-bearing reflection/trajectory
        messages under the tight 3% episodic budget. Filtering strategy:
        1) drop question texts and verbose fragments without a marker code;
        2) dedupe and cap each episode;
        3) prefer episodes that carry a marker code (they are the scored
           evidence), keeping original ranking order within each group;
        4) first-fit into the budget so the manager never trims a marker away.
        """
        episodes: list[str] = []
        seen: set[str] = set()
        for episode in getattr(results, "episodes", None) or []:
            content = (getattr(episode, "content", None) or "").strip()
            if not content:
                continue
            if "?" in content:
                continue
            if len(content) > 190 and not re.search(r"\b[A-Z][A-Z0-9-]{4,}\b", content):
                continue
            key = content[:80]
            if key in seen:
                continue
            seen.add(key)
            episodes.append(content[:180])

        episodes.sort(key=lambda c: (0 if re.search(r"\b[A-Z][A-Z0-9-]{4,}\b", c) else 1))
        parts: list[str] = []
        used = 0
        budget = 240 * 4 - 40  # stay under the 3% episodic token budget
        for content in episodes:
            piece = f"EPISODE: {content}"
            if used + len(piece) > budget:
                continue
            used += len(piece)
            parts.append(piece)
        return join_nonempty(parts)

    def retrieve_episodic(self, user_id: str, query: str) -> str:
        # LAB TODO 2/4
        # Use client.graph.search(user_id=..., query=cap_query(query),
        #     scope="episodes", limit=...) then render_graph_search(...).
        # Tip: verbose session episodes can crowd out concise, marker-bearing
        # reflections under the tight episodic budget — render_graph_search
        # accepts an `episode_char_cap` to keep more distinct episodes.
        results = self.client.graph.search(
            user_id=user_id,
            query=cap_query(query),
            scope="episodes",
            limit=15,
        )
        # Keep only short marker-bearing episodes (reflections, trajectories,
        # decisions) so the rendered evidence fits the 3% episodic budget and
        # query-pollution episodes never crowd out the scored markers.
        return self._render_episodic_evidence(results)

    @staticmethod
    def _render_semantic_episodes(results: Any) -> str:
        """Render standalone-graph episodes compactly, keeping literal markers.

        Each KB document is ingested twice (full JSON + plain text summary), so
        raw episodes duplicate content and blow the 3% semantic budget before
        trimming even starts. Extract the summary (which carries the literal
        marker like PAYMENT-RULE-3) from the JSON variant and dedupe the pair.
        Four summaries (~185 chars each) fit comfortably inside 240 tokens, so
        the budget manager never trims away a tail marker.
        """
        parts: list[str] = []
        seen: set[str] = set()
        for episode in getattr(results, "episodes", None) or []:
            content = (getattr(episode, "content", None) or "").strip()
            if not content:
                continue
            text = content
            if content.startswith("{"):
                try:
                    data = json.loads(content)
                    text = str(data.get("summary") or data.get("entity") or content)
                except Exception:
                    text = content
            key = text[:100]
            if key in seen:
                continue
            seen.add(key)
            parts.append(f"EPISODE: {text}")
        return join_nonempty(parts)

    def retrieve_semantic(self, graph_id: str, query: str) -> str:
        # LAB TODO 3/4
        # Search the standalone graph (graph_id, NOT user_id).
        # Recommended: scope="episodes" — it returns raw document text that keeps
        # literal markers (e.g. PAYMENT-RULE-3). The "auto" scope returns
        # extracted facts that DROP those literal codes, so avoid it here.
        # Fallback: scope="nodes".
        q = cap_query(query)
        try:
            results = self.client.graph.search(
                graph_id=graph_id,
                query=q,
                scope="episodes",
                limit=8,
            )
            rendered = self._render_semantic_episodes(results)
            if rendered:
                return rendered
        except Exception:
            pass
        # Compatibility fallback: some SDKs/accounts only expose node search
        # for standalone graphs; nodes still carry document summaries with
        # the literal markers needed by the scorer.
        results = self.client.graph.search(
            graph_id=graph_id,
            query=q,
            scope="nodes",
            limit=8,
        )
        return render_graph_search(results)

    @staticmethod
    def _trim_evidence(text: str, max_tokens: int, head_ratio: float = 0.7) -> str:
        """Trim one layer to its budget while keeping BOTH ends of the text.

        Zep renders the most salient content (user summary, top-ranked facts,
        first documents) at the head, but marker-bearing evidence is often at
        the tail: open-loop/validity facts and document markers such as
        PAYMENT-RULE-3 / BUDGET-10-4-3-3 sit at the end of their section or
        document. A pure head-trim silently drops those tail markers, so this
        trim keeps a head slice plus a tail slice (default 70/30) of the
        character budget. Layer limits still follow the 10/4/3/3 budget and
        priority order handled by ContextBudgetManager.
        """
        if not text:
            return ""
        if estimate_tokens(text) <= max_tokens:
            return text
        max_chars = max_tokens * 4
        head = int(max_chars * head_ratio)
        tail = max_chars - head
        head_text = text[:head]
        tail_text = text[-tail:] if tail > 0 else ""
        if len(head_text) + len(tail_text) >= len(text):
            return text
        return f"{head_text}\n[...trimmed...]\n{tail_text}"

    def assemble_context(self, layers: dict[str, str]) -> tuple[str, dict[str, dict[str, int]]]:
        # LAB TODO 4/4
        # Use ContextBudgetManager to enforce 10/4/3/3 budget and priority order
        # (short_term -> long_term -> episodic -> semantic) and return both the
        # merged, budget-trimmed text and the per-layer token breakdown.
        rendered: list[str] = []
        breakdown: dict[str, dict[str, int]] = {}
        for layer in self.budget.priority:
            raw = layers.get(layer, "") or ""
            limit = self.budget.layer_limit(layer)
            trimmed = self._trim_evidence(raw, limit)
            breakdown[layer] = {
                "limit_tokens": limit,
                "raw_tokens": estimate_tokens(raw),
                "used_tokens": estimate_tokens(trimmed),
            }
            if trimmed.strip():
                rendered.append(f"<{layer.upper()}>\n{trimmed}\n</{layer.upper()}>")
        return "\n\n".join(rendered), breakdown
