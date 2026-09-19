from tools.ast_utils import find_occurrences, classify_occurrence, split_by_domain


def execute(symbol: str) -> str:
    occurrences = find_occurrences(symbol)

    if not occurrences:
        return f"No references found for '{symbol}'"

    code, tests, other = split_by_domain(occurrences)

    lines = [
        f"Found {len(occurrences)} references "
        f"({len(code)} code, {len(tests)} test, {len(other)} log/other)",
        "",
    ]

    for filepath, lineno, text in occurrences:
        kind = classify_occurrence(symbol, filepath, lineno, text)
        lines.append(f"{filepath}:{lineno} {kind}")

    return "\n".join(lines)
