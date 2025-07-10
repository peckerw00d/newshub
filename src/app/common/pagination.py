from datetime import datetime

SEPARATOR = "__"


def encode_cursor(dt: datetime, hash_str: str) -> str:
    return f"{dt.isoformat()}{SEPARATOR}{hash_str}"


def decode_cursor(cursor: str) -> tuple[datetime, str]:
    dt_str, hash_str = cursor.split(SEPARATOR, 1)
    return datetime.fromisoformat(dt_str), hash_str
