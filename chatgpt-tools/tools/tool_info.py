from tools.schemas import DEFAULT_TOOL_SCHEMAS


def _flatten_schema(name, schema):
    """Flatten a tool schema into a readable top-level response."""
    curated = schema.get("curated", False)
    result = {
        "tool": name,
        "description": schema.get("description", ""),
        "category": schema.get("category", ""),
        "complexity": schema.get("complexity", ""),
        "safety_level": schema.get("safety_level", ""),
        "curated": str(curated).lower(),
        "required": ", ".join(schema.get("required", [])),
        "optional": ", ".join(schema.get("optional", [])),
    }

    args = schema.get("arguments", {})
    if args:
        lines = []
        for arg_name, arg_info in args.items():
            req = "required" if arg_info.get("required") else "optional"
            desc = arg_info.get("description", "")
            lines.append(f"  {arg_name} ({req}): {desc}")
        result["arguments"] = "\n" + "\n".join(lines)

    returns = schema.get("returns", {})
    if returns:
        lines = []
        for ret_name, ret_info in returns.items():
            rtype = ret_info.get("type", "")
            desc = ret_info.get("description", "")
            lines.append(f"  {ret_name} ({rtype}): {desc}")
        result["returns"] = "\n" + "\n".join(lines)

    examples = schema.get("examples", [])
    if examples:
        result["examples"] = "\n" + "\n".join(f"  {e}" for e in examples)

    failure_modes = schema.get("failure_modes", [])
    if failure_modes:
        lines = []
        for fm in failure_modes:
            lines.append(f"  {fm.get('condition', '')}: {fm.get('message', '')}")
        result["failure_modes"] = "\n" + "\n".join(lines)

    result["supports_sha"] = str(schema.get("supports_sha", False)).lower()
    result["supports_rollback"] = str(schema.get("supports_rollback", False)).lower()
    result["supports_preview"] = str(schema.get("supports_preview", False)).lower()

    for field in ["supported_symbol_types", "unsupported_symbol_types", "accepted_formats", "unsupported_formats"]:
        val = schema.get(field)
        if val:
            result[field] = ", ".join(val)

    limitations = schema.get("limitations")
    if limitations:
        result["limitations"] = "\n" + "\n".join(f"  {l}" for l in limitations)

    if not curated:
        result["curated_metadata"] = (
            "Best_for: not yet curated\n"
            "Avoid_when: not yet curated\n"
            "Related_tools: not yet curated\n"
            "Limitations: not yet curated"
        )

    return result


def execute(tool: str = "") -> dict:
    if tool:
        schema = DEFAULT_TOOL_SCHEMAS.get(tool)
        if not schema:
            return {"error": f"Unknown tool: {tool}"}
        return _flatten_schema(tool, schema)

    tools = sorted(DEFAULT_TOOL_SCHEMAS.keys())
    lines = ["Available tools:\n"]
    for t in tools:
        s = DEFAULT_TOOL_SCHEMAS[t]
        desc = s.get("description", "")
        cat = s.get("category", "")
        lines.append(f"  {t:<20} {cat:<12} {desc}")
    return {
        "tools": "\n" + "\n".join(lines),
        "count": len(tools),
        "tool_list": ", ".join(tools),
    }
