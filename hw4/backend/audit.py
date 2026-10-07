"""append-only audit trail of agent-loop activity.

records are written as JSON Lines (one JSON object per line) to
output/audit_trail.json in append mode, so the file is never wiped between runs.
"""
import datetime as dt
import json
from pathlib import Path

import config

AUDIT_PATH = Path(
    config.project_dir / "output" / "audit_trail.json"
)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _short(value: object, limit: int = 200) -> str:
    text = str(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def append_record(record: dict) -> None:
    """append one record (as a JSON line) to the audit trail; best-effort."""
    try:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {"time": _now(), **record}
        with AUDIT_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # auditing must never break a chat turn
        pass


def log_tool_call(tool: str, args: dict, result: object) -> None:
    append_record(
        {
            "type": "tool_call",
            "tool": tool,
            "args": _short(args),
            "result": _short(result),
        }
    )


def log_turn(message: str, tools_used: list[str], stop_reason: str, requests: int) -> None:
    append_record(
        {
            "type": "turn",
            "message": _short(message, 120),
            "tools_used": tools_used,
            "requests": requests,
            "stop_reason": stop_reason,
        }
    )
