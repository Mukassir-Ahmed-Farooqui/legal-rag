import re


INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+all\s+instructions",
    r"disregard\s+instructions",
    r"override\s+system\s+prompt",
    r"reveal\s+system\s+prompt",
    r"show\s+system\s+prompt",
    r"act\s+as",
    r"you\s+are\s+chatgpt",
    r"developer\s+message",
    r"system\s+message",
]


def contains_prompt_injection(text: str) -> bool:

    text = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True

    return False