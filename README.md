# NUST Admissions Assistant (offline)

Local-first FAQ assistant for the NUST Islamabad chatbot competition brief: **no internet**, **no remote APIs**, **CPU-only** (BM25 retrieval over a bundled FAQ snapshot).

## What it does

- Parses `faq.md` (official-style FAQ HTML) into `data/faq.json` via `scripts/extract_faq.py`.
- Answers questions with **BM25** (`rank-bm25`) over question+answer text—fast and explainable on modest hardware.
- When nothing in the query overlaps the corpus (score 0), it **refuses to invent** an answer and suggests keywords.
- When a match is weak, it **surfaces uncertainty** and reminds users to verify on the live admissions site.

## Run

```bash
pip install -r requirements.txt
python scripts/extract_faq.py   # regenerate JSON if faq.md changes
python app.py
```

Open `http://127.0.0.1:5000`.

## Tradeoffs (for judges)

| Choice | Why |
|--------|-----|
| BM25, not a local LLM | Sub‑millisecond typical latency, tiny RAM footprint, answers are verbatim from the FAQ (trustworthy). |
| No GPU / no transformers | Stays within 8GB RAM and i5-class CPU; predictable behaviour under load. |
| HTML answers preserved | Rich text from the source FAQ; retrieval stays grounded. |
| Confidence + “no match” path | Avoids confident wrong answers when the query shares no tokens with the corpus. |

Run `python scripts/benchmark.py` for a rough latency distribution on your machine.

## Limits

- Content is only as current as `faq.md`. Dates and policies must be confirmed on **official** NUST channels.
- Retrieval is lexical; rephrase if a synonym-heavy question misses.
