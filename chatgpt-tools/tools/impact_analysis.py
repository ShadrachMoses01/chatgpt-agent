import ast
from pathlib import Path

from tools.ast_utils import (
    find_occurrences, classify_occurrence, classify_symbol,
    get_function_body, extract_calls, split_by_domain,
)


def _find_callers(symbol: str, root="."):
    callers = []
    for filepath, lineno, text in find_occurrences(symbol, root):
        if f"{symbol}(" in text or f".{symbol}(" in text:
            callers.append((filepath, lineno, text.strip()))
    return callers


def _find_callees(symbol: str, root="."):
    callees = []
    for filepath, lineno, text in find_occurrences(symbol, root):
        kind = classify_occurrence(symbol, filepath, lineno, text)
        if kind == "definition":
            body = get_function_body(filepath, symbol)
            if body:
                calls = extract_calls(body)
                callees.extend(calls)
    return callees


def _find_tests_for_symbol(symbol: str, root="tests"):
    tests = []
    for filepath, lineno, text in find_occurrences(symbol, root):
        tests.append(f"{filepath}:{lineno}")
    return tests


def execute(symbol: str) -> str:
    all_occurrences = find_occurrences(symbol)
    code, tests_occ, other = split_by_domain(all_occurrences)
    total = len(all_occurrences)

    definitions = sum(
        1 for _, _, t in all_occurrences
        if classify_occurrence(symbol, "", 0, t) == "definition"
    )
    usages = sum(
        1 for _, _, t in all_occurrences
        if classify_occurrence(symbol, "", 0, t) == "usage"
    )
    imports = sum(
        1 for _, _, t in all_occurrences
        if classify_occurrence(symbol, "", 0, t) == "import"
    )

    symbol_kind = classify_symbol(symbol)

    callers = _find_callers(symbol)
    callees = _find_callees(symbol)
    tests = _find_tests_for_symbol(symbol)

    unique_callees = list(set(callees))

    parts = [
        f"Symbol: {symbol}",
        f"Kind: {symbol_kind}",
        f"Total references: {total}",
        f"  Code: {len(code)}",
        f"  Tests: {len(tests_occ)}",
        f"  Logs/other: {len(other)}",
        f"  Definitions: {definitions}",
        f"  Usages: {usages}",
        f"  Imports: {imports}",
        f"Direct callers: {len(callers)}",
        f"Direct callees: {len(unique_callees)}",
        f"Tests referencing: {len(tests)}",
        "",
    ]

    if callers:
        parts.append("Callers:")
        for f, l, t in callers[:10]:
            parts.append(f"  {f}:{l}  {t[:60]}")
        if len(callers) > 10:
            parts.append(f"  ... and {len(callers) - 10} more")
        parts.append("")

    if unique_callees:
        parts.append("Callees:")
        for c in sorted(unique_callees):
            kind = classify_symbol(c)
            parts.append(f"  {c} ({kind})")
        parts.append("")

    if tests:
        parts.append("Tests:")
        for t in tests[:10]:
            parts.append(f"  {t}")
        if len(tests) > 10:
            parts.append(f"  ... and {len(tests) - 10} more")
        parts.append("")

    parts.append("Reference files:")
    seen_files = set()
    for f, l, t in all_occurrences:
        if f not in seen_files:
            seen_files.add(f)
            parts.append(f"  {f}")

    return "\n".join(parts)
