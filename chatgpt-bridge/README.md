# ChatGPT Agent Bridge

Local HTTP bridge between ChatGPT (via the Chrome extension or the
clipboard) and the `chatgpt-tools` runtime. Receives free-form chat text,
extracts `<tool_call>` / `<tool_batch>` XML, dispatches it, and returns the
result as JSON (HTTP) while also copying the `<tool_result>` XML to the
clipboard for pasting back into ChatGPT.

Standard library only — no third-party dependencies.

## Layout

```
chatgpt-bridge/
├── server.py              # HTTP server: POST /api/execute, GET /api/health
├── runtime.py             # Extract -> parse -> dispatch -> clipboard
├── cli.py                 # `chatgpt-agent start` entry point
├── bridge/
│   ├── xml_extractor.py   # Find first/all valid tool XML in chat text
│   ├── clipboard.py       # macOS pbpaste/pbcopy (fails loudly elsewhere)
│   ├── watcher.py         # Polling clipboard daemon
│   └── main.py            # One-shot clipboard executor
├── chrome-extension/
│   ├── manifest.json      # MV3, matches chat.openai.com + chatgpt.com
│   ├── content_script.js  # Scrapes assistant messages, detects XML, forwards
│   ├── background.js      # Service-worker fetch proxy (avoids page CORS)
│   └── README.md          # Extension install notes
├── protocol_test.md       # Multiline/markdown transport fixture
└── test.txt               # Tiny transport fixture ("Hello")
```

## Running

```bash
pip install -e .            # installs the `chatgpt-agent` script (stdlib only)
chatgpt-agent start         # serves http://127.0.0.1:9876
# or: python3 server.py / python3 cli.py start
python3 -m pytest bridge/ -q
```

The server expects a sibling checkout of `chatgpt-tools` next to this
directory (`../chatgpt-tools`); `runtime.py` adds it to `sys.path`.

## Request flow

```
ChatGPT assistant message (DOM)
  -> content_script.js: poll every 1.5s, wait until message text is stable
     and the reply looks finished, check for tool XML
  -> background.js: POST http://127.0.0.1:9876/api/execute {text, source}
  -> server.py: BridgeHandler validates JSON, 10 MB body cap
  -> runtime.py: extract_xml -> parse -> dispatcher.dispatch (chatgpt-tools)
  -> result JSON to the extension; <tool_result> XML to the clipboard
```

The clipboard path (`bridge/watcher.py`, `bridge/main.py`) skips the HTTP
server: it reads `pbpaste` output and calls the same `runtime.execute`.

## Security model (read this before running)

- Binds **`127.0.0.1:9876` only** — never `0.0.0.0`. Keep it that way.
- **No authentication.** Any local process — and any web page you visit
  while the server runs (CORS is `*`) — can POST tool calls that read,
  rewrite, and execute code as your user. This is a local development
  tool: do not expose the port, do not run it on shared machines, and stop
  it when you are done.
- The extension requests only `scripting` + host permissions for the two
  ChatGPT origins and `http://127.0.0.1:9876/*`.
- ChatGPT coupling: the content script scrapes
  `[data-message-author-role="assistant"]` / `[data-message-role]`
  elements and treats a message as finished when its text stabilizes and
  the HTML contains a button plus copy/edit/regenerate/continue text.
  Those selectors and heuristics will break if the ChatGPT web UI changes
  (see chrome-extension/README.md).
- `runtime.py` honors an `id` attribute on the tool XML as the request id
  for log correlation — i.e. the model can choose its own request ids.
