import subprocess


def execute(query: str) -> str:
    try:
        result = subprocess.run(
            ["rg", "-n", query, "."],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "Error: 'rg' (ripgrep) is not installed or not on PATH."

    return result.stdout
