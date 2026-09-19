from tools.schemas import DEFAULT_TOOL_SCHEMAS


def validate_against_schema(tool_name: str, args: dict):
    schema = DEFAULT_TOOL_SCHEMAS.get(tool_name)

    if schema is None:
        raise ValueError(f"No schema defined for tool: {tool_name}")

    if not isinstance(args, dict):
        raise ValueError("Tool args must be a dict")

    required = schema.get("required", [])
    optional = schema.get("optional", [])

    missing = [key for key in required if key not in args]

    if missing:
        raise ValueError(
            f"Missing required args for {tool_name}: {missing}"
        )

    allowed = set(required + optional)
    unknown = [k for k in args if k not in allowed]

    if unknown:
        raise ValueError(
            f"Unknown args for {tool_name}: {unknown}. Allowed: {sorted(allowed)}"
        )

    for k, v in args.items():
        if v is None:
            raise ValueError(f"Arg '{k}' cannot be None")

        if not isinstance(k, str):
            raise ValueError("Arg keys must be strings")

    return args
