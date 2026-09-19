
import json


def validate_tool_input(args: dict):
    if not isinstance(args, dict):
        raise ValueError("Tool args must be a dict")

    for k in args.keys():
        if not isinstance(k, str):
            raise ValueError("Tool arg keys must be strings")

    return args


def normalize_output(data):
    return json.loads(json.dumps(data, default=str))


def strict_output_check(data):
    """
    Enforces runtime output safety boundary.
    """
    try:
        return json.loads(json.dumps(data, default=str))
    except Exception as e:
        raise ValueError(f"Output not serializable: {e}")
    