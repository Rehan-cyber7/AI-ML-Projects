// Reads the cached prediction result for the active tab (written by
// background.js) and renders it in the popup.

const VERDICT_COLORS = {
  phishing: "#c0392b",
  suspicious: "#e67e22",
  legitimate: "#27ae60",
};

async function renderPopup() {
  const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!activeTab) {
    return;
  }

  const key = `result_${activeTab.id}`;
  const stored = await chrome.storage.session.get(key);
  const result = stored[key];

  const verdictEl = document.getElementById("verdict");
  const fillEl = document.getElementById("confidence-bar-fill");
  const detailsEl = document.getElementById("details");

  if (!result) {
    verdictEl.textContent = "No data yet for this page.";
    return;
  }

  verdictEl.textContent = `Verdict: ${result.verdict}`;
  verdictEl.style.color = VERDICT_COLORS[result.verdict] || "#333";

  const pct = Math.round(result.confidence * 100);
  fillEl.style.width = `${pct}%`;
  fillEl.style.background = VERDICT_COLORS[result.verdict] || "#999";

  const signals = result.signals || {};
  detailsEl.textContent =
    `Confidence: ${pct}%\n` +
    `ML score: ${signals.ml_probability ?? "n/a"}\n` +
    `Recently registered domain: ${signals.domain_recently_registered ?? "n/a"}\n` +
    `Threat-intel flagged: ${signals.threat_intel?.flagged ?? "n/a"}`;
}

document.addEventListener("DOMContentLoaded", renderPopup);
