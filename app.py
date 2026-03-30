"""Local Flask app: offline NUST admissions FAQ assistant."""
from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from nust_chatbot.retrieve import FaqRetriever

app = Flask(__name__)
_retriever: FaqRetriever | None = None


def get_retriever() -> FaqRetriever:
    global _retriever
    if _retriever is None:
        _retriever = FaqRetriever(Path(__file__).parent / "data" / "faq.json")
    return _retriever


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    r = get_retriever()
    return jsonify(
        {
            "status": "ok",
            "offline": True,
            "faq_count": len(r._items),
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    out = get_retriever().query(message)
    return jsonify(out)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
