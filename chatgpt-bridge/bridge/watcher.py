#!/usr/bin/env python3
import os
import sys
import time
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bridge.clipboard import read as read_clipboard
from runtime import execute

POLL_INTERVAL = 2.0


def _hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    last_hash = ""
    print(f"Watching clipboard every {POLL_INTERVAL}s... (Ctrl+C to stop)")

    try:
        while True:
            try:
                content = read_clipboard()
            except Exception as e:
                print(f"\n--- Clipboard error: {e} ---")
                time.sleep(POLL_INTERVAL)
                continue
            current_hash = _hash(content)
            if current_hash != last_hash and content.strip():
                result = execute(content, source="clipboard")
                if result["success"]:
                    tools = ", ".join(r["tool"] for r in result.get("results", []))
                    print(f"\n--- Executed: {tools} ---")
                elif result.get("error"):
                    print(f"\n--- {result['error']} ---")
                last_hash = current_hash
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == "__main__":
    main()
