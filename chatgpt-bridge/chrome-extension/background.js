const SERVER = "http://127.0.0.1:9876";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "ping") {
    fetch(`${SERVER}/api/health`)
      .then((r) => r.json())
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true;
  }

  if (request.type === "execute") {
    fetch(`${SERVER}/api/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: request.text,
        source: request.source || "chatgpt",
      }),
    })
      .then((r) => r.json())
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true;
  }
});
