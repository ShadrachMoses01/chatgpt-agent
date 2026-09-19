import re
import xml.etree.ElementTree as ET
from typing import Optional


def extract_xml(text: str) -> Optional[str]:
    candidates = _find_candidates(text)
    seen = set()
    for raw in candidates:
        normalized = _normalize(raw)
        if normalized and normalized not in seen:
            seen.add(normalized)
            root = _parse_and_check(normalized)
            if root is not None:
                return normalized
    return None


def _parse_and_check(xml_str: str):
    try:
        root = ET.fromstring(xml_str)
        if root.tag in ("tool_call", "tool_batch"):
            return root
        return None
    except ET.ParseError:
        return None


def extract_all_xml(text: str) -> list[str]:
    candidates = _find_candidates(text)
    seen = set()
    valid = []
    for raw in candidates:
        normalized = _normalize(raw)
        if normalized and normalized not in seen:
            seen.add(normalized)
            if _parse_and_check(normalized) is not None:
                valid.append(normalized)
    return valid


def _find_candidates(text: str) -> list[str]:
    candidates = []

    code_block_pattern = r"```(?:xml)?\s*\n(.*?)```"
    matches = re.findall(code_block_pattern, text, re.DOTALL)
    candidates.extend(matches)

    tool_batch_pattern = r"(<tool_batch[^>]*>.*?</tool_batch>)"
    matches = re.findall(tool_batch_pattern, text, re.DOTALL)
    candidates.extend(matches)

    tool_call_pattern = r"(<tool_call[^>]*>.*?</tool_call>)"
    matches = re.findall(tool_call_pattern, text, re.DOTALL)
    candidates.extend(matches)

    return candidates


def _normalize(raw: str) -> str:
    return raw.strip()



