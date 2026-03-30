"""BM25 retrieval over extracted FAQ (CPU-only, no network)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class FaqRetriever:
    def __init__(self, faq_path: Path | str | None = None) -> None:
        root = Path(__file__).resolve().parents[1]
        path = Path(faq_path) if faq_path else root / "data" / "faq.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._items: list[dict[str, Any]] = raw
        corpus = [f"{x['question']} {x['answer']}" for x in self._items]
        self._tokenized = [_tokenize(t) for t in corpus]
        self._bm25 = BM25Okapi(self._tokenized)

    def query(self, message: str, top_k: int = 5) -> dict[str, Any]:
        q = (message or "").strip()
        if not q:
            return {
                "reply_html": "",
                "reply_text": "",
                "confidence": 0.0,
                "uncertain": True,
                "sources": [],
                "notice": "Ask a question about NUST admissions (fees, NET, programmes, eligibility, etc.).",
            }

        q_tokens = _tokenize(q)
        if not q_tokens:
            return {
                "reply_html": "",
                "reply_text": "",
                "confidence": 0.0,
                "uncertain": True,
                "sources": [],
                "notice": "Try adding words related to your question (e.g. NET, fee, hostel, engineering).",
            }

        scores = list(self._bm25.get_scores(q_tokens))
        ranked = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )
        top_idx = ranked[: max(3, top_k)]
        top_scores = [scores[i] for i in top_idx[:top_k]]

        best = top_idx[0]
        s0 = float(scores[best])
        s1 = float(scores[top_idx[1]]) if len(top_idx) > 1 else 0.0

        if s0 <= 0.0:
            return {
                "reply_html": "",
                "reply_text": "",
                "confidence": 0.0,
                "uncertain": True,
                "sources": [],
                "notice": (
                    "No FAQ entry matched those words. Try keywords such as NET, fee, merit, "
                    "hostel, engineering, MBBS, or eligibility."
                ),
                "matched_question": "",
            }

        # Separation between #1 and #2 (higher => clearer winner)
        sep = (s0 - s1) / (s0 + 1e-9) if s0 > 0 else 0.0
        # Absolute strength: normalize by corpus max score seen this query
        max_s = max(scores) if scores else 0.0
        strength = s0 / (max_s + 1e-9)

        uncertain = bool(
            s0 < 0.01 or (sep < 0.08 and s0 < 3.0) or strength < 0.95
        )

        item = self._items[best]
        answer_html = item.get("answer_html") or item["answer"]

        notice_parts: list[str] = []
        if uncertain:
            notice_parts.append(
                "This is the closest match in the local FAQ snapshot. "
                "Confirm deadlines and policy details on the official NUST admissions site."
            )

        sources = []
        for i in top_idx[:3]:
            it = self._items[i]
            sources.append(
                {
                    "id": it["id"],
                    "question": it["question"],
                    "score": round(float(scores[i]), 4),
                    "answer_preview": it["answer"][:220]
                    + ("…" if len(it["answer"]) > 220 else ""),
                }
            )

        confidence = min(1.0, max(0.0, 0.35 * strength + 0.45 * min(1.0, sep) + 0.2 * min(1.0, s0 / 10.0)))

        return {
            "reply_html": answer_html,
            "reply_text": item["answer"],
            "confidence": round(confidence, 3),
            "uncertain": uncertain,
            "sources": sources,
            "notice": " ".join(notice_parts) if notice_parts else "",
            "matched_question": item["question"],
        }
