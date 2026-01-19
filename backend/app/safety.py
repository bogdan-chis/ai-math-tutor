import re
from typing import List

FINAL_CUE_PATTERNS = [
    r"\bfinal answer\b",
    r"\bthe answer is\b",
    r"^\s*answer\s*:\s*",
    r"^\s*solution\s*:\s*",
    r"^\s*final\s*:\s*",
]

def has_final_answer_cue(text: str) -> bool:
    t = text.strip().lower()
    return any(re.search(p, t, flags=re.IGNORECASE) for p in FINAL_CUE_PATTERNS)

def build_bad_words_list() -> List[str]:
    return ["final answer", "the answer is", "Answer:", "Solution:", "Final:"]
