"""Parse faq.md (NUST admissions FAQ HTML) into structured JSON for offline retrieval."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


def _clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_faq(html_path: Path) -> list[dict]:
    raw = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    cards = soup.find_all("div", class_="card")
    out: list[dict] = []
    for i, card in enumerate(cards):
        btn = card.find("button")
        body = card.find("div", class_="card-body")
        if not btn or not body:
            continue
        spans = btn.find_all("span", recursive=False)
        if not spans:
            continue
        q = _clean_text(spans[0].get_text(" ", strip=True))
        a_html = body.decode_contents()
        a = _clean_text(body.get_text(" ", strip=True))
        if not q or not a:
            continue
        out.append(
            {
                "id": i,
                "question": q,
                "answer": a,
                "answer_html": a_html.strip(),
            }
        )
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    html_path = root / "faq.md"
    out_path = root / "data" / "faq.json"
    if not html_path.is_file():
        print(f"Missing {html_path}", file=sys.stderr)
        sys.exit(1)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    faq = extract_faq(html_path)
    out_path.write_text(json.dumps(faq, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(faq)} Q&A pairs to {out_path}")


if __name__ == "__main__":
    main()
