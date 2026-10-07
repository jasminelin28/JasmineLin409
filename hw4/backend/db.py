"""thin sqlite helpers for the campus customs database."""
import json
import sqlite3
from typing import Any

import config


def get_connection() -> sqlite3.Connection:
    """open a connection with row access by column name."""
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def parse_json_list(value: str) -> list[str]:
    """catalogue stores colors/tags as json text; fall back to comma split."""
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (json.JSONDecodeError, TypeError):
        pass
    return [part.strip() for part in value.split(",") if part.strip()]
