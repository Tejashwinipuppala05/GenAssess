from __future__ import annotations

from .models import BankQuestion

_SOURCE = "MBPP sanitized train split"
_LICENSE = "CC-BY-4.0"


def _mbpp_question(
    task_id: int,
    topic: str,
    difficulty: str,
    prompt: str,
    solution: str,
    tests: list[str],
    *,
    imports: list[str] | None = None,
) -> BankQuestion:
    return {
        "id": f"mbpp-sanitized-{task_id}",
        "round": "coding",
        "question": prompt,
        "category": "Coding Challenge",
        "topic": topic,
        "difficulty": difficulty,
        "source": f"{_SOURCE}, task {task_id}",
        "license": _LICENSE,
        "attribution": (
            f"Mostly Basic Python Problems (MBPP), Google Research; "
            f"Austin et al. (2021), task {task_id}."
        ),
        "estimated_time_seconds": 900,
        "reference_solution": solution,
        "test_cases": tests,
        "test_imports": imports or [],
        "tags": ["python", topic.lower(), "mbpp"],
    }


CODING_QUESTIONS: list[BankQuestion] = [
    _mbpp_question(
        602,
        "Strings",
        "Easy",
        "Write a python function to find the first repeated character in a given string.",
        '''def first_repeated_char(str1):
    for index, c in enumerate(str1):
        if str1[:index + 1].count(c) > 1:
            return c''',
        [
            'assert first_repeated_char("abcabc") == "a"',
            'assert first_repeated_char("abc") == None',
            'assert first_repeated_char("123123") == "1"',
        ],
    ),
    _mbpp_question(
        604,
        "Strings",
        "Easy",
        "Write a function to reverse words seperated by spaces in a given string.",
        '''def reverse_words(s):
    return " ".join(reversed(s.split()))''',
        [
            'assert reverse_words("python program")==("program python")',
            'assert reverse_words("java language")==("language java")',
            'assert reverse_words("indian man")==("man indian")',
        ],
    ),
    _mbpp_question(
        606,
        "Mathematics",
        "Easy",
        "Write a function to convert degrees to radians.",
        '''import math

def radian_degree(degree):
    radian = degree * (math.pi / 180)
    return radian''',
        [
            "assert radian_degree(90)==1.5707963267948966",
            "assert radian_degree(60)==1.0471975511965976",
            "assert radian_degree(120)==2.0943951023931953",
        ],
    ),
    _mbpp_question(
        608,
        "Dynamic Programming",
        "Medium",
        "Write a python function to find nth bell number.",
        '''def bell_Number(n):
    bell = [[0 for i in range(n + 1)] for j in range(n + 1)]
    bell[0][0] = 1
    for i in range(1, n + 1):
        bell[i][0] = bell[i - 1][i - 1]
        for j in range(1, i + 1):
            bell[i][j] = bell[i - 1][j - 1] + bell[i][j - 1]
    return bell[n][0] ''',
        [
            "assert bell_Number(2) == 2",
            "assert bell_Number(3) == 5",
            "assert bell_Number(4) == 15",
        ],
    ),
    _mbpp_question(
        611,
        "Matrices",
        "Easy",
        "Write a function which given a matrix represented as a list of lists returns the max of the n'th column.",
        '''def max_of_nth(test_list, N):
    res = max([sub[N] for sub in test_list])
    return res ''',
        [
            "assert max_of_nth([[5, 6, 7], [1, 3, 5], [8, 9, 19]], 2) == 19",
            "assert max_of_nth([[6, 7, 8], [2, 4, 6], [9, 10, 20]], 1) == 10",
            "assert max_of_nth([[7, 8, 9], [3, 5, 7], [10, 11, 21]], 1) == 11",
        ],
    ),
]
# Load additional validated MBPP records from the local validated dataset format.
import json
from pathlib import Path

_MBPP_VALIDATED_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "question_banks" / "mbpp_validated.json"
)
if _MBPP_VALIDATED_PATH.exists():
    for _record in json.loads(_MBPP_VALIDATED_PATH.read_text(encoding="utf-8")):
        CODING_QUESTIONS.append(
            _mbpp_question(
                _record["task_id"],
                _record["topic"],
                _record["difficulty"],
                _record["prompt"],
                _record["solution"],
                _record["tests"],
                imports=_record.get("test_imports") or [],
            )
        )

