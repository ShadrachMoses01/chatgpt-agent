import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import server


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: chatgpt-agent <command>")
        print("")
        print("Commands:")
        print("  start    Launch the bridge HTTP server")
        return

    command = sys.argv[1]

    if command == "start":
        server.main()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
