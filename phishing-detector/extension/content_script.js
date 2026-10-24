// Renders an in-page warning banner when instructed by the background worker.

chrome.runtime.onMessage.addListener((message) => {
  if (message.type !== "SHOW_WARNING") {
    return;
  }

  const { verdict, confidence } = message.result;

  const banner = document.createElement("div");
  banner.textContent =
    verdict === "phishing"
      ? `Warning: this site is flagged as likely phishing (confidence: ${Math.round(confidence * 100)}%).`
      : "This site has some suspicious characteristics - proceed with caution.";

  Object.assign(banner.style, {
    position: "fixed",
    top: "0",
    left: "0",
    right: "0",
    zIndex: "2147483647",
    padding: "12px",
    textAlign: "center",
    fontFamily: "sans-serif",
    fontWeight: "bold",
    color: "#fff",
    backgroundColor: verdict === "phishing" ? "#c0392b" : "#e67e22",
  });

  document.documentElement.prepend(banner);
});
