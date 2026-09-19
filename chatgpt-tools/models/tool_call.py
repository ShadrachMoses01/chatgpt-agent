from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ToolCall:
    tool: str
    args: Dict[str, Any]
    id: str = ""
