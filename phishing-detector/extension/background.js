// Watches tab navigation and queries the phishing-detection API.
// All heavy lifting happens server-side; this file only orchestrates calls.

// Point this at your deployed Flask API (see README.md / Section 9 of the guide).
const API_ENDPOINT = "https://your-api-domain.example/api/predict";

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Only act once the URL is settled and it's an http(s) page.
  if (changeInfo.status !== "complete" || !tab.url || !tab.url.startsWith("http")) {
    return;
  }

  try {
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: tab.url }),
    });

    if (!response.ok) {
      console.warn("Phishing check failed:", response.status);
      return;
    }

    const result = await response.json();

    // Cache the latest result per tab so the popup can read it instantly.
    await chrome.storage.session.set({ [`result_${tabId}`]: result });

    if (result.verdict === "phishing" || result.verdict === "suspicious") {
      chrome.tabs.sendMessage(tabId, { type: "SHOW_WARNING", result });
    }
  } catch (error) {
    console.error("Error contacting phishing-detection API:", error);
  }
});
