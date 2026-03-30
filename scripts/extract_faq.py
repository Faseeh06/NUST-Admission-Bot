"""Parse faq.md (Markdown Q&A) into data/faq.json for offline retrieval."""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path


def _clean_text(s: str) -> str:
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _answer_to_html(answer: str) -> str:
    """Plain answer → simple <p> HTML for the UI."""
    paras = [p.strip() for p in answer.split("\n\n") if p.strip()]
    if not paras:
        return ""
    return "".join(f"<p>{html.escape(p)}</p>" for p in paras)


def extract_faq_markdown(text: str) -> list[dict]:
    text = text.lstrip("\ufeff").strip()
    if text.startswith("#"):
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl + 1 :].lstrip()
    blocks = re.split(r"(?m)^##\s+", text)
    blocks = [b.strip() for b in blocks if b.strip()]
    out: list[dict] = []
    for i, block in enumerate(blocks):
        nl = block.find("\n")
        if nl == -1:
            continue
        q = _clean_text(block[:nl])
        a = _clean_text(block[nl + 1 :])
        if not q or not a:
            continue
        out.append(
            {
                "id": len(out),
                "question": q,
                "answer": a,
                "answer_html": _answer_to_html(a),
            }
        )
    return out


def extract_faq(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    return extract_faq_markdown(raw)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    md_path = root / "faq.md"
    out_path = root / "data" / "faq.json"
    if not md_path.is_file():
        print(f"Missing {md_path}", file=sys.stderr)
        sys.exit(1)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    faq = extract_faq(md_path)
    out_path.write_text(json.dumps(faq, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(faq)} Q&A pairs to {out_path}")


if __name__ == "__main__":
    main()
