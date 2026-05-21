"""Helpers for parsing CSV query parameters."""
from typing import Optional

from fastapi import HTTPException


def parse_int_csv(value: Optional[str]) -> list[int]:
    """Parse a comma-separated string of ints. Empty/None → []."""
    if not value:
        return []
    try:
        return [int(x) for x in value.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(400, f"Invalid int CSV value: {value!r}")
