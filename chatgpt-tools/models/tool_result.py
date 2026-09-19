from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ToolResult:
    success: bool
    data: Dict[str, Any]
    id: str = ""
