const CONFIG = {
  POLL_MS: 1500,
};

const PROCESSED = new Set();

let logPanel = null;
let statusBadge = null;

// Modern CSS colors matching ChatGPT's design system
const colors = {
  primary: "#10a37f", // ChatGPT green
  primaryLight: "#4ade80",
  secondary: "#818cf8", // ChatGPT blue
  accent: "#fbbf24", // ChatGPT yellow
  destructive: "#f87171", // ChatGPT red
  background: "#171717", // ChatGPT dark background
  surface: "#1e1e1e", // ChatGPT surface color
  border: "#2a2a2a",
  text: "#e0e0e0", // ChatGPT off-white text
  textSecondary: "#a0a0a0",
  overlay: "rgba(0, 0, 0, 0.8)",
};

function time() {
  return new Date().toLocaleTimeString();
}

function formatTimestamp() {
  const date = new Date();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}

function getLogColor(type) {
  const map = { info: colors.textSecondary, success: colors.primaryLight, error: colors.destructive, xml: colors.accent, send: colors.secondary };
  return map[type] || colors.text;
}

function getLogIcon(type) {
  const map = { info: "ℹ", success: "✓", error: "✗", xml: "◈", send: "↑" };
  return map[type] || "•";
}

function log(message, type = "info") {
  if (!logPanel) logPanel = createModernPanel();

  const color = getLogColor(type);

  const entry = document.createElement("div");
  entry.className = "bridge-log-entry";
  Object.assign(entry.style, {
    padding: "8px 12px", borderBottom: `1px solid ${colors.border}`,
    display: "flex", alignItems: "flex-start", gap: "8px",
    fontSize: "12px", lineHeight: "1.4",
    backgroundColor: type === "error" ? "rgba(248, 113, 113, 0.05)" :
                    type === "success" ? "rgba(74, 222, 128, 0.05)" :
                    type === "xml" ? "rgba(251, 191, 36, 0.05)" :
                    "transparent",
    transition: "all 0.2s ease",
  });

  const timestamp = document.createElement("span");
  timestamp.className = "log-timestamp";
  timestamp.textContent = `[${formatTimestamp()}]`;
  Object.assign(timestamp.style, {
    color: colors.textSecondary,
    fontFamily: "monospace",
    fontSize: "10px",
    marginTop: "2px",
    flexShrink: 0,
  });

  const content = document.createElement("span");
  content.className = "log-content";
  content.textContent = message;
  Object.assign(content.style, {
    color: color,
    flex: 1,
  });

  const icon = document.createElement("span");
  icon.className = "log-icon";
  icon.innerHTML = getLogIcon(type);
  Object.assign(icon.style, {
    width: "16px",
    height: "16px",
    marginTop: "2px",
    flexShrink: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  });

  entry.appendChild(icon);
  entry.appendChild(timestamp);
  entry.appendChild(content);

  // Add hover effect
  entry.onmouseover = () => {
    entry.style.backgroundColor = type === "error" ? "rgba(248, 113, 113, 0.1)" :
                                  type === "success" ? "rgba(74, 222, 128, 0.1)" :
                                  type === "xml" ? "rgba(251, 191, 36, 0.1)" :
                                  "rgba(255, 255, 255, 0.05)";
  };

  entry.onmouseout = () => {
    entry.style.backgroundColor = type === "error" ? "rgba(248, 113, 113, 0.05)" :
                                  type === "success" ? "rgba(74, 222, 128, 0.05)" :
                                  type === "xml" ? "rgba(251, 191, 36, 0.05)" :
                                  "transparent";
  };

  const body = document.getElementById("bridge-log-body");
  if (body) {
    body.appendChild(entry);
    body.scrollTop = body.scrollHeight;
  }

  document.getElementById("bridge-log-panel").style.display = "block";
  console.log(`[Bridge] ${message}`);
}

function createModernPanel() {
  const container = document.createElement("div");
  container.id = "bridge-log-panel";
  Object.assign(container.style, {
    position: "fixed", 
    bottom: "20px", 
    right: "20px", 
    zIndex: 9999,
    width: "420px", 
    maxHeight: "400px", 
    overflowY: "auto",
    background: colors.background,
    border: `1px solid ${colors.border}`,
    borderRadius: "12px",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    fontSize: "13px",
    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)",
    backdropFilter: "blur(12px)",
    display: "none",
    flexDirection: "column",
  });

  // Modern header with gradient
  const header = document.createElement("div");
  header.id = "bridge-log-header";
  Object.assign(header.style, {
    padding: "12px 16px",
    background: `linear-gradient(135deg, ${colors.secondary} 0%, ${colors.primary} 100%)`,
    borderRadius: "12px 12px 0 0",
    display: "flex", 
    justifyContent: "space-between",
    alignItems: "center",
    cursor: "pointer",
    userSelect: "none",
  });

  const title = document.createElement("div");
  title.style.cssText = `
    color: white;
    fontSize: "14px";
    fontWeight: "600";
    display: "flex";
    alignItems: "center";
    gap: "8px";
  `;
  title.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
      <path d="M3 3h18v18H3V3zm2 2v14h14V5H5zm4 4h6v2H9V9zm0 4h4v2H9v-2z"/>
    </svg>
    Bridge Log
  `;

  const toggleBtn = document.createElement("button");
  toggleBtn.id = "bridge-toggle";
  Object.assign(toggleBtn.style, {
    width: "24px", height: "24px",
    border: "none", borderRadius: "4px",
    background: "rgba(255, 255, 255, 0.2)",
    color: "white",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "12px",
    fontWeight: "bold",
  });
  toggleBtn.textContent = "_";

  header.appendChild(title);
  header.appendChild(toggleBtn);

  toggleBtn.onclick = (e) => {
    e.stopPropagation();
    const show = body.style.display !== "none";
    body.style.display = show ? "none" : "block";
    toggleBtn.textContent = show ? "+" : "_";
  };

  const body = document.createElement("div");
  body.id = "bridge-log-body";
  Object.assign(body.style, {
    padding: "0",
    maxHeight: "360px",
    overflowY: "auto",
    display: "block",
  });

  // Custom scrollbar
  body.style.scrollbarWidth = "6px";
  body.style.scrollbarColor = `${colors.primary} ${colors.surface}`;

  container.appendChild(header);
  container.appendChild(body);
  document.body.appendChild(container);

  // Close panel button (top-right)
  const closeBtn = document.createElement("button");
  closeBtn.innerHTML = "×";
  Object.assign(closeBtn.style, {
    position: "absolute",
    top: "8px",
    right: "8px",
    width: "20px",
    height: "20px",
    border: "none",
    borderRadius: "4px",
    background: "rgba(255, 255, 255, 0.1)",
    color: "white",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "bold",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  });

  closeBtn.onclick = (e) => {
    e.stopPropagation();
    body.style.display = "none";
  };

  header.appendChild(closeBtn);

  header.onclick = () => {
    const show = body.style.display !== "none";
    body.style.display = show ? "none" : "block";
    toggleBtn.textContent = show ? "+" : "_";
  };

  return body;
}

function showBadge() {
  statusBadge = document.createElement("div");
  statusBadge.id = "bridge-badge";
  Object.assign(statusBadge.style, {
    position: "fixed", 
    bottom: "20px", 
    right: "20px", 
    zIndex: 9999,
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 16px",
    background: colors.background,
    border: `1px solid ${colors.border}`,
    borderRadius: "24px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
    cursor: "pointer",
    transition: "all 0.3s ease",
  });

  const dot = document.createElement("div");
  dot.id = "bridge-dot";
  Object.assign(dot.style, {
    width: "10px", 
    height: "10px", 
    borderRadius: "50%", 
    background: colors.primaryLight,
    boxShadow: "0 0 8px rgba(74, 222, 128, 0.6)",
    animation: "pulse 2s infinite",
  });

  const text = document.createElement("span");
  text.textContent = "Bridge: Active";
  Object.assign(text.style, {
    color: colors.text,
    fontSize: "13px",
    fontWeight: "500",
  });

  statusBadge.appendChild(dot);
  statusBadge.appendChild(text);

  statusBadge.onmouseover = () => {
    statusBadge.style.background = colors.surface;
    statusBadge.style.transform = "translateY(-2px)";
    statusBadge.style.boxShadow = "0 6px 20px rgba(0, 0, 0, 0.4)";
  };

  statusBadge.onmouseout = () => {
    statusBadge.style.background = colors.background;
    statusBadge.style.transform = "translateY(0)";
    statusBadge.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.3)";
  };

  statusBadge.onclick = () => {
    const panel = document.getElementById("bridge-log-panel");
    if (panel) {
      const show = panel.style.display === "block" || panel.style.display === "";
      panel.style.display = show ? "none" : "block";
    }
  };

  document.body.appendChild(statusBadge);

  // Add pulse animation
  const style = document.createElement("style");
  style.textContent = `
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
   `;
  document.head.appendChild(style);
}

function hash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) - h) + s.charCodeAt(i);
    h |= 0;
  }
  return h;
}

function hasXML(text) {
  return /<tool_call>|<\/tool_call>|<tool_batch>|```(?:xml)?\s*\n/.test(text);
}

async function sendToServer(text) {
  log("Sending to server...", "send");
  setDot("yellow");
  try {
    const res = await chrome.runtime.sendMessage({
      type: "execute",
      text,
      source: "chatgpt",
    });
    if (res.ok) {
      const data = res.data;
      if (data.error && !data.success) {
        log(`No action: ${data.error}`, "info");
        setDot("green");
        return;
      }
      for (const r of data.results || []) {
        log(`Tool: ${r.tool} - ${r.success ? "SUCCESS" : "FAILED"}`, r.success ? "success" : "error");
      }
      setDot("green");
    } else {
      log(`Failed: ${res.error}`, "error");
      setDot("red");
    }
  } catch (err) {
    log(`Bridge error: ${err.message}`, "error");
    setDot("red");
  }
}

function setDot(color) {
  const dot = document.getElementById("bridge-dot");
  if (dot) dot.style.background = color;
}

function isComplete(el) {
  const html = el.innerHTML;
  return /copy|edit|regenerate|continue/i.test(html) && html.includes("<button");
}

function findAssistantMessages() {
  const selectors = [
    '[data-message-author-role="assistant"]',
    '[data-message-role="assistant"]',
  ];
  for (const sel of selectors) {
    const els = document.querySelectorAll(sel);
    if (els.length > 0) return Array.from(els);
  }
  return [];
}

function getText(el) {
  // innerText preserves block-element boundaries with \n and works correctly
  // inside <pre><code> (code fences). textContent concatenates everything without
  // separators, which destroys newlines when React renders XML across <p> tags.
  return el.innerText || el.textContent || "";
}

function processMessage(el) {
  const text = getText(el);
  if (!text.trim()) return;
  const h = hash(text);
  if (PROCESSED.has(h)) return;
  PROCESSED.add(h);

  if (hasXML(text)) {
    log("XML detected (completed)", "xml");
    sendToServer(text);
  }
}

const lastSeen = new WeakMap();

function scan() {
  const messages = findAssistantMessages();
  for (const el of messages) {
    const text = getText(el);
    if (!text.trim()) continue;
    if (PROCESSED.has(hash(text))) continue;

    const prev = lastSeen.get(el);
    const stable = !!prev && prev.text === text;

    if (stable && isComplete(el)) {
      lastSeen.delete(el);
      setTimeout(() => processMessage(el), 100);
    } else {
      lastSeen.set(el, { text });
    }
  }
}

function start() {
  showBadge();

  // Reuse the status dot created by showBadge() (id "bridge-dot") instead
  // of creating a second element with the same id, which made
  // getElementById("bridge-dot") resolve nondeterministically.
  const badge = document.getElementById("bridge-badge");
  const dot = document.getElementById("bridge-dot");
  if (badge && dot && dot.parentElement !== badge) {
    badge.prepend(dot);
  }

  log("Bridge active", "info");

  setInterval(scan, CONFIG.POLL_MS);
  scan();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start);
} else {
  start();
}
