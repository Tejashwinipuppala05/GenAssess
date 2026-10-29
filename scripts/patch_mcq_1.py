p='src/rounds/routes.py'
s=open(p).read()
s=s.replace(
'''class RoundQuestion(BaseModel):
    id: str
    question: str
    topic: str
    category: str
    difficulty: str
    source: str
    license: str
    test_cases: list[str] | None = None
    follow_up_dimensions: list[str] | None = None''',
'''class RoundQuestion(BaseModel):
    id: str
    question: str
    topic: str
    category: str
    difficulty: str
    source: str
    license: str
    options: list[str] | None = None
    test_cases: list[str] | None = None
    follow_up_dimensions: list[str] | None = None''')
s=s.replace(
'''class EvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    question_id: str = Field(alias="questionId")
    answer: str''',
'''class EvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    question_id: str = Field(alias="questionId")
    answer: str = ""
    selected_answer: int | None = Field(default=None, alias="selectedAnswer")''')
s=s.replace(
"evaluator = AnswerEvaluator()",
"evaluator = AnswerEvaluator()\n_TECHNICAL_OPTION_ANSWERS: dict[str, int] = {}")
open(p,'w').write(s)
print('done')