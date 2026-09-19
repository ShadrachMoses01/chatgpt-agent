#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bridge.clipboard import read as read_clipboard
from runtime import execute


def main():
    try:
        chat_response = read_clipboard()
    except Exception as e:
        print(f"Clipboard error: {e}")
        sys.exit(1)
    if not chat_response.strip():
        print("Clipboard is empty")
        sys.exit(1)

    result = execute(chat_response, source="clipboard")

    if result["success"]:
        tools = ", ".join(r["tool"] for r in result.get("results", []))
        print(f"OK  {tools}")
    elif result.get("error"):
        print(f"SKIP  {result['error']}")
    else:
        print("No action taken")


if __name__ == "__main__":
    main()
