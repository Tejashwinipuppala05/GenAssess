from __future__ import annotations

from .models import BankQuestion

_RUBRIC = [
    "Specific situation and context",
    "Candidate's own actions and reasoning",
    "Outcome and evidence of impact",
    "Reflection or learning",
]


def _questions(category: str, topic: str, prompts: tuple[str, ...]) -> list[BankQuestion]:
    return [
        {
            "id": f"bh-{category.lower().replace('/', '-').replace(' ', '-')}-{index:02d}",
            "round": "behavioral",
            "question": prompt,
            "category": category,
            "topic": topic,
            "difficulty": "Medium",
            "source": "Original GenAssess question",
            "license": "GenAssess original; no separate public license",
            "estimated_time_seconds": 120,
            "follow_up_dimensions": ["context", "individual contribution", "outcome", "reflection"],
            "evaluation_criteria": _RUBRIC.copy(),
            "tags": ["behavioral", category.lower()],
        }
        for index, prompt in enumerate(prompts, start=1)
    ]


BEHAVIORAL_QUESTIONS: list[BankQuestion] = [
    *_questions(
        "Introduction",
        "Introduction",
        (
            "Tell me about yourself and the experiences that best prepare you for this role.",
            "Which project or experience are you most proud of, and what was your contribution?",
            "What strengths would your teammates say you bring to a project?",
            "What kind of work motivates you, and why?",
            "What would you like us to understand about your background that is not clear from your resume?",
        ),
    ),
    *_questions(
        "Teamwork",
        "Teamwork",
        (
            "Describe a time you helped a team deliver a shared goal.",
            "Tell me about a time you had to coordinate work with someone whose working style differed from yours.",
            "How have you handled a situation where a teammate needed support to complete their work?",
            "Describe a time you changed your approach after receiving input from your team.",
            "What role do you naturally take when a team is deciding how to divide a project?",
        ),
    ),
    *_questions(
        "Leadership",
        "Leadership",
        (
            "Tell me about a time you took initiative without being asked.",
            "Describe a time you helped a group make progress when no one had clear ownership.",
            "How have you helped a peer learn a skill or become more confident?",
            "Tell me about a decision you made with incomplete information.",
            "Describe how you kept a group focused when priorities changed.",
        ),
    ),
    *_questions(
        "Conflict Resolution",
        "Conflict Resolution",
        (
            "Describe a work or study disagreement and how you worked toward a resolution.",
            "Tell me about a time you received feedback you initially disagreed with.",
            "How have you handled a misunderstanding that affected a team's progress?",
            "Describe a time you had to raise a concern about a proposed decision.",
            "Tell me about a time you helped two people with different views find common ground.",
        ),
    ),
    *_questions(
        "Problem Solving",
        "Problem Solving",
        (
            "Describe a difficult problem you broke into manageable steps.",
            "Tell me about a time you used evidence to choose between possible solutions.",
            "Describe a situation where your first solution did not work. What did you try next?",
            "Tell me about a time you had to learn something quickly to solve a problem.",
            "How have you balanced a quick fix with a more durable solution?",
        ),
    ),
    *_questions(
        "Communication",
        "Communication",
        (
            "Tell me about a time you explained a complex idea to someone unfamiliar with it.",
            "Describe a time you had to communicate a delay or setback.",
            "How have you adapted your communication for different audiences?",
            "Tell me about a time asking a clarifying question prevented rework.",
            "Describe a time you documented a decision so others could act on it.",
        ),
    ),
    *_questions(
        "Adaptability",
        "Adaptability",
        (
            "Tell me about a time priorities changed unexpectedly. How did you respond?",
            "Describe a situation where you had to work effectively with limited resources.",
            "Tell me about a time you adapted to a new tool, process, or team.",
            "How have you handled a task whose requirements changed while you were working on it?",
            "Describe a time you had to adjust your plan after new information became available.",
        ),
    ),
    *_questions(
        "Failure/Learning",
        "Failure and Learning",
        (
            "Tell me about a mistake you made and how you addressed its impact.",
            "Describe a goal you did not meet. What did you learn from the experience?",
            "Tell me about a time you received constructive criticism and acted on it.",
            "What is a skill you deliberately improved after identifying a gap?",
            "Describe a lesson from a setback that changed how you work.",
        ),
    ),
    *_questions(
        "Workplace Situations",
        "Workplace Situations",
        (
            "If two urgent tasks had competing deadlines, how would you decide what to do first?",
            "How would you respond if you noticed a possible mistake shortly before a delivery?",
            "What would you do if you were blocked and your usual point of contact was unavailable?",
            "How would you handle a request that conflicts with an agreed team process?",
            "What steps would you take if you realized you had misunderstood an assignment?",
        ),
    ),
    *_questions(
        "Role-Specific Situations",
        "Role-Specific Situations",
        (
            "Describe how you would clarify success criteria before starting an unfamiliar role-specific task.",
            "How would you explain a technical trade-off to a stakeholder focused on a business outcome?",
            "What would you do if a proposed solution met the immediate need but created a maintenance risk?",
            "How would you approach a task where the available data was incomplete or inconsistent?",
            "Describe how you would make a role-specific recommendation when stakeholders have different priorities.",
        ),
    ),
]
