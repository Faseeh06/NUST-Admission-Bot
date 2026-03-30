const chat = document.getElementById("chat");
const form = document.getElementById("form");
const msg = document.getElementById("msg");
const send = document.getElementById("send");
const chips = document.getElementById("chips");
const faqCount = document.getElementById("faq-count");
const clearHistoryBtn = document.getElementById("clear-history");

const INTRO_HTML = `<div class="body"><p>Ask in plain English. Search is local (BM25), no network.</p></div>`;

const SUGGESTIONS = [
  "Quota or reserved seats?",
  "NET registration and fee",
  "Hostel facility",
  "ICS for engineering?",
  "Refund of security deposit",
];

function addBubble(role, html) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = html;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function addIntroBubble() {
  addBubble("bot", INTRO_HTML);
}

function clearHistory() {
  chat.replaceChildren();
  addIntroBubble();
}

function escapeHtml(s) {
  const p = document.createElement("p");
  p.textContent = s;
  return p.innerHTML;
}

async function sendMessage(text) {
  const t = text.trim();
  if (!t) return;
  addBubble("user", escapeHtml(t));
  send.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: t }),
    });
    const data = await res.json();

    let inner = "";
    if (data.matched_question) {
      inner += `<div class="meta">Match: ${escapeHtml(
        data.matched_question
      )} · ${(data.confidence * 100).toFixed(0)}%</div>`;
    }
    if (data.reply_html) {
      inner += `<div class="body">${data.reply_html}</div>`;
    } else if (data.notice) {
      inner += `<div class="body"><p>${escapeHtml(data.notice)}</p></div>`;
    }
    if (data.notice && data.reply_html) {
      inner += `<div class="notice">${escapeHtml(data.notice)}</div>`;
    }
    if (data.sources && data.sources.length) {
      const items = data.sources
        .map(
          (s) =>
            `<li>${escapeHtml(s.question)} (${s.score})</li>`
        )
        .join("");
      inner += `<details class="sources"><summary>Other close matches</summary><ul>${items}</ul></details>`;
    }
    addBubble("bot", inner || `<div class="body"><p>No response.</p></div>`);
  } catch (e) {
    addBubble(
      "bot",
      `<div class="body"><p>Could not reach the server. Run python app.py and try again.</p></div>`
    );
  } finally {
    send.disabled = false;
    msg.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(msg.value);
  msg.value = "";
});

clearHistoryBtn.addEventListener("click", () => {
  clearHistory();
  msg.focus();
});

SUGGESTIONS.forEach((s) => {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "chip";
  b.textContent = s;
  b.addEventListener("click", () => {
    msg.value = s;
    sendMessage(s);
    msg.value = "";
  });
  chips.appendChild(b);
});

fetch("/api/health")
  .then((r) => r.json())
  .then((d) => {
    if (d.faq_count != null) faqCount.textContent = `${d.faq_count} entries`;
  })
  .catch(() => {
    faqCount.textContent = "local FAQ";
  });

addIntroBubble();
