from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

class AptitudeSessionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    target_role: str = Field(min_length=2, max_length=100, alias="targetRole")
    company_type: str | None = Field(default=None, max_length=80, alias="companyType")
    experience_level: Literal["Fresher", "Experienced"] = Field(alias="experienceLevel")

    @field_validator("target_role")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 2:
            raise ValueError("Enter at least two characters.")
        return normalized

    @field_validator("company_type")
    @classmethod
    def normalize_company_type(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class AptitudeSessionConfigResponse(BaseModel):
    question_count: int = Field(serialization_alias="questionCount")
    estimated_duration_seconds: int = Field(serialization_alias="estimatedDurationSeconds")
    category_counts: dict[str, int] = Field(serialization_alias="categoryCounts")
    difficulty_distribution: dict[str, int] = Field(serialization_alias="difficultyDistribution")
    categories: tuple[str, ...]

    model_config = ConfigDict(populate_by_name=True)


class AptitudeQuestionResponse(BaseModel):
    id: str
    question: str
    options: list[str]
    topic: str
    subtopic: str
    category: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    estimated_time_seconds: int = Field(serialization_alias="estimatedTimeSeconds")
    source_type: str = Field(serialization_alias="sourceType")
    tags: list[str]
    selected_answer: int | None = Field(default=None, serialization_alias="selectedAnswer")
    marked_for_review: bool = Field(default=False, serialization_alias="markedForReview")

    model_config = ConfigDict(populate_by_name=True)


class AptitudeSessionResponse(BaseModel):
    id: str
    status: Literal["IN_PROGRESS", "COMPLETED"]
    target_role: str = Field(serialization_alias="targetRole")
    company_type: str | None = Field(serialization_alias="companyType")
    experience_level: str = Field(serialization_alias="experienceLevel")
    started_at: int = Field(serialization_alias="startedAt")
    expires_at: int = Field(serialization_alias="expiresAt")
    server_time: int = Field(serialization_alias="serverTime")
    duration_seconds: int = Field(serialization_alias="durationSeconds")
    total_questions: int = Field(serialization_alias="totalQuestions")
    questions: list[AptitudeQuestionResponse]

    model_config = ConfigDict(populate_by_name=True)


class AptitudeAnswerUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    selected_answer: int | None = Field(default=None, ge=0, le=3, alias="selectedAnswer")
    marked_for_review: bool = Field(default=False, alias="markedForReview")


class AptitudeCategoryResult(BaseModel):
    category: str
    total: int
    correct: int
    incorrect: int
    unanswered: int
    accuracy: float


class AptitudeTopicResult(BaseModel):
    topic: str
    category: str
    total: int
    correct: int
    incorrect: int
    unanswered: int
    accuracy: float


class AptitudeDifficultyResult(BaseModel):
    difficulty: str
    total: int
    correct: int
    incorrect: int
    unanswered: int
    accuracy: float


class AptitudeAnswerReview(BaseModel):
    question_id: str = Field(serialization_alias="questionId")
    question: str
    options: list[str]
    selected_answer: int | None = Field(serialization_alias="selectedAnswer")
    correct_answer: int = Field(serialization_alias="correctAnswer")
    is_correct: bool | None = Field(serialization_alias="isCorrect")
    explanation: str
    topic: str
    subtopic: str
    category: str
    difficulty: str

    model_config = ConfigDict(populate_by_name=True)


class AptitudeResultResponse(BaseModel):
    session_id: str = Field(serialization_alias="sessionId")
    target_role: str = Field(serialization_alias="targetRole")
    company_type: str | None = Field(serialization_alias="companyType")
    experience_level: str = Field(serialization_alias="experienceLevel")
    total_questions: int = Field(serialization_alias="totalQuestions")
    correct_answers: int = Field(serialization_alias="correctAnswers")
    incorrect_answers: int = Field(serialization_alias="incorrectAnswers")
    unanswered_questions: int = Field(serialization_alias="unansweredQuestions")
    score: int
    accuracy: float
    time_taken_seconds: int = Field(serialization_alias="timeTakenSeconds")
    duration_seconds: int = Field(serialization_alias="durationSeconds")
    completed_at: int = Field(serialization_alias="completedAt")
    category_performance: list[AptitudeCategoryResult] = Field(serialization_alias="categoryPerformance")
    topic_performance: list[AptitudeTopicResult] = Field(serialization_alias="topicPerformance")
    difficulty_performance: list[AptitudeDifficultyResult] = Field(serialization_alias="difficultyPerformance")
    strong_topics: list[str] = Field(serialization_alias="strongTopics")
    weak_topics: list[str] = Field(serialization_alias="weakTopics")
    recommendation: str
    answers: list[AptitudeAnswerReview]

    model_config = ConfigDict(populate_by_name=True)


class AptitudeHistoryItem(BaseModel):
    session_id: str = Field(serialization_alias="sessionId")
    target_role: str = Field(serialization_alias="targetRole")
    company_type: str | None = Field(serialization_alias="companyType")
    experience_level: str = Field(serialization_alias="experienceLevel")
    status: Literal["IN_PROGRESS", "COMPLETED"]
    started_at: int = Field(serialization_alias="startedAt")
    total_questions: int = Field(serialization_alias="totalQuestions")
    correct_answers: int | None = Field(serialization_alias="correctAnswers")
    accuracy: float | None
    time_taken_seconds: int | None = Field(serialization_alias="timeTakenSeconds")

    model_config = ConfigDict(populate_by_name=True)
