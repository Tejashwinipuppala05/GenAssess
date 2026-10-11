# GenAssess MVP — Interview Notes

## 1. Problem Statement

GenAssess gives candidates a structured way to practise technical interview answers and receive immediate, explainable feedback. This MVP is the first candidate-side vertical slice of a wider recruitment and interview-assessment vision.

## 2. Architecture

The original Gradio UI has been removed. The interview domain logic remains in `src/`: `InterviewSession` manages state and adaptive progression, while `QuestionGenerator` and `AnswerEvaluator` are separate services. It is not currently connected to the Next.js frontend or FastAPI API.

## 3. How Question Generation Works

With `OPENAI_API_KEY`, `QuestionGenerator` calls an OpenAI-compatible chat-completions endpoint and validates the returned JSON. It passes selected role, topic, difficulty, and optional JD text. Without a key—or after an API/response error—it selects a topic/difficulty question from `src/question_bank.py`. The question model records its source, but there is no current interview UI displaying it.

## 4. How Evaluation Works

With an API key, `AnswerEvaluator` sends the question, reference concepts, ideal answer, and candidate answer to the configured LLM and validates its structured response. Otherwise it performs a transparent rule-based evaluation: it checks for reference-concept strings and adds a small bonus for answers of 25+ words. It labels this result `Rule-based fallback`; it is not presented as advanced AI.

## 5. Why These Technologies?

Python keeps the interview domain logic concise and readable. The current web stack is Next.js, React, TypeScript, and Tailwind CSS with a FastAPI backend. Dataclasses make interview records structured. pytest covers the interview logic and authentication API. The OpenAI SDK remains optional for the interview components, which have local fallbacks.

## 6. Important Technical Decisions

- Interview state remains in memory; authentication users and revocable sessions are persisted in SQLite.
- Made external AI optional: a working local fallback is essential for demos and error resilience.
- Used a deterministic adaptation policy: ≥75 moves up, <45 moves down, otherwise holds.
- Preserved source/method labels so users can distinguish model-driven from fallback behavior.

## 7. Realistic Challenges

- LLM responses may be invalid JSON or fail due to network, quota, or provider changes.
- Keyword matching misses synonyms and can reward superficial wording.
- The local bank intentionally has limited question variety; repeated fallback questions can occur in longer sessions.
- The interview prototype holds sessions only in memory, so it is not a persistent interview workflow.

## 8. Future Improvements

Add persistent history, richer question banks, semantic evaluation with calibration, an adaptive model trained on validated outcomes, JD extraction, resumes, recruiter workflows, and human-review controls.

## 9. Likely Interview Questions

1. **Why did you separate UI and interview logic?** Explain that it makes components testable and replaceable.
2. **How does the app work without an API key?** Describe the local question bank and rule-based evaluator.
3. **How do you avoid falsely claiming AI?** Point to the visible source/method labels.
4. **How is adaptive difficulty implemented?** Explain the three score thresholds.
5. **What data is stored during an interview?** Question, answer, evaluation, and UTC timestamp in memory.
6. **How is the optional JD used?** It is included only in the LLM question-generation prompt.
7. **What happens if the LLM request fails?** The code catches the error and uses its fallback.
8. **Why use dataclasses?** They provide clear typed, structured records with low overhead.
9. **How does fallback scoring work?** It measures reference-concept string matches and a small length signal.
10. **What are the fallback evaluator's limitations?** It cannot reliably understand synonyms or correctness beyond references.
11. **How is the final score calculated?** It is the arithmetic average of evaluated answer scores.
12. **How is skill-gap analysis calculated?** The session average maps to Strong, Moderate, or Needs improvement.
13. **What test cases did you include?** Fallback source, empty answers, score behavior, adaptation, and summary.
14. **Where is data stored?** Authentication users and revocable sessions are in SQLite; the separate interview prototype keeps its session state in memory.
15. **What would you improve first?** Add question variety and semantic, calibrated evaluation with persisted history.
