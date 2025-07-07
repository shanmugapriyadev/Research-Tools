"""Create narration script from MCQ data."""
from typing import Dict


def build_script(row: Dict[str, str]) -> str:
    question = row.get("Question", "")
    answer = row.get("Answer", "")
    explanation = row.get("Explanation", "")
    tip = row.get("Strategy Tip", "")
    script = (
        f"Question: {question}. "
        f"The correct answer is {answer}. "
        f"Explanation: {explanation}. "
        f"Strategy tip: {tip}."
    )
    return script
