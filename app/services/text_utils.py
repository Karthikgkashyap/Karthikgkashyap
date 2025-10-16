from __future__ import annotations

import re
from typing import List

_word_re = re.compile(r"[A-Za-z][A-Za-z\-\+\#]*")


def normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def extract_words(text: str) -> List[str]:
    return [m.group(0).lower() for m in _word_re.finditer(text or "")]  # type: ignore


def split_skills(skills_text: str) -> List[str]:
    if not skills_text:
        return []
    # Split on commas or newlines or semicolons
    raw = re.split(r"[\n,;]", skills_text)
    return [normalize_skill(s) for s in raw if normalize_skill(s)]


def join_list(items: List[str]) -> str:
    return ", ".join(items)
