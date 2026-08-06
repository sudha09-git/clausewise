import re
from dataclasses import dataclass
CLAUSE_HEADER_PATTERNS = [
    re.compile(r"^\s*(\d+(?:\.\d+){0,3})[\.\)]?\s+([A-Z][A-Za-z ,&/\-]{2,80})\s*$"),
]

MAX_HEADER_LINE_LENGTH = 100


def _match_header(line: str):
    """Return (clause_number, title) if the line looks like a clause header, else None."""
    stripped = line.strip()
    if not stripped or len(stripped) > MAX_HEADER_LINE_LENGTH:
        return None

    for pattern in CLAUSE_HEADER_PATTERNS:
        match = pattern.match(stripped)
        if match:
            number = match.group(1).strip()
            title = match.group(2).strip()
            return number, title

    return None