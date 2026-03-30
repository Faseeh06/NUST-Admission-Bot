# NUST Admissions Assistant

A small Flask app that answers NUST admissions questions **without calling the internet**. Everything runs on your machine: the UI, the FAQ data, and a lightweight search layer (BM25) over the text you ship in the repo.

If you’re prepping for the local chatbot competition—or you just want a fast, boringly honest FAQ lookup—this is basically that.

## What you get

You type a question in plain English. The app finds the closest entries in a bundled FAQ (sourced from the official NUST FAQ snapshot in `faq.md`, extracted to `data/faq.json`). Answers come straight from that text, not from a model making things up.

A few behaviours that matter:

- **No match, no guess.** If your words don’t overlap the FAQ enough, you get a nudge to try different keywords instead of a random paragraph.
- **Weak match?** It’ll say so and still remind you to double-check on the live admissions site.
- **CPU-only, low drama.** No GPU, no giant transformer download—just retrieval that’s quick on a typical laptop.

## Quick start

```bash
pip install -r requirements.txt
python scripts/extract_faq.py   # rebuild data/faq.json if you change faq.md
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

First-time setup needs network for `pip`; after that, the app itself doesn’t need a connection to work.

## Repo layout (the useful bits)

| Path | Role |
|------|------|
| `app.py` | Flask server and `/api/chat` |
| `templates/`, `static/` | Chat UI |
| `nust_chatbot/retrieve.py` | BM25 over FAQ entries |
| `faq.md` | Raw FAQ HTML |
| `data/faq.json` | Parsed Q&A (generated—don’t hand-edit unless you know what you’re doing) |
| `scripts/extract_faq.py` | HTML → JSON |
| `scripts/benchmark.py` | Quick latency sanity check |

## Why BM25 and not a local LLM?

Tradeoffs are simple: BM25 is fast, tiny in memory, and the answers stay **verbatim** from your FAQ—which is easier to defend in a demo. A local LLM could paraphrase and drift; here, what you see is what’s in the file.

Run `python scripts/benchmark.py` if you want a rough latency read on your hardware.

## Caveats (read this once)

Policies and dates change. Treat this as a **mirror of whatever is in `faq.md`**, not a legal substitute for the official NUST admissions pages. If something sounds time-sensitive, verify it there.

Search is **lexical**—if you ask in a way that doesn’t share words with the FAQ, try rephrasing or using terms like NET, programme names, fees, etc.

## License / use

Built for a NUST competition-style submission; adapt the code and copy as you need for your own project.
