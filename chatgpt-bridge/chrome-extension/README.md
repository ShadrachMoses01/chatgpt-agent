# ChatGPT Tool Bridge — Chrome Extension

Forwards `<tool_call>` / `<tool_batch>` XML emitted by ChatGPT to the local
bridge server (`http://127.0.0.1:9876`, see `../README.md`) and shows results
in an on-page panel.

## Install

1. Start the bridge server first: `chatgpt-agent start`.
2. Open Chrome and go to `chrome://extensions`.
3. Enable "Developer mode" (top-right toggle).
4. Click "Load unpacked" and select this `chrome-extension` folder.
5. The extension is active on `chat.openai.com` and `chatgpt.com`.

## How it works

- `content_script.js` polls the page every 1.5 s for assistant messages,
  waits until a message's text stops changing (streaming finished) and the
  reply looks complete, then forwards messages containing tool XML via
  `chrome.runtime.sendMessage`.
- `background.js` (service-worker) performs the actual
  `POST /api/execute` fetch — content scripts cannot call the local server
  directly because of page CORS, so the service worker acts as a proxy.
- No build step, no npm dependencies; vanilla JS + Chrome MV3 APIs.

## Permissions

- `scripting` only. No `tabs`, `storage`, or broad host access.
- Runs solely on the two ChatGPT origins; talks to
  `http://127.0.0.1:9876/*` and nothing else.

## Known coupling to the ChatGPT web UI

This extension scrapes the live ChatGPT DOM, so it is inherently coupled
to it:

- Assistant messages are found via
  `[data-message-author-role="assistant"]` / `[data-message-role]`.
- A reply counts as finished when its text is stable across polls **and**
  its HTML contains a `<button>` plus copy/edit/regenerate/continue text
  (English UI). A redesign, i18n, or markup change can silently stop
  detection — the on-page panel will simply stay quiet.
- Polling (not `MutationObserver`); per-message dedup uses a 32-bit hash
  held in a `Set` that grows for the lifetime of the page.
- Message text is read via `innerText` so fenced code blocks keep their
  newlines; only static strings are ever written with `innerHTML`.
