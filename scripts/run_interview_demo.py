import os
from src.interview import InterviewSession

role = os.getenv("INTERVIEW_ROLE", "Software Engineer")
topic = os.getenv("INTERVIEW_TOPIC", "Python")
difficulty = os.getenv("INTERVIEW_DIFFICULTY", "Easy")
count = int(os.getenv("INTERVIEW_QUESTION_COUNT", "3"))

session = InterviewSession(role, topic, difficulty, count)
session.start()

for i in range(count):
    print(f"\nQuestion {i + 1}: {session.current_question.prompt}")
    answer = input("Your answer: ")
    result = session.submit(answer)
    print(f"Score: {result.score}/100 | Method: {result.method}")
    print(f"Suggestions: {result.suggestions}")

final = session.finalize()
print("\nFinal score:", final["average_score"])