from datetime import datetime
from pydantic import BaseModel


class CategoryResultOut(BaseModel):
    key: str
    name: str
    score: float
    max_score: int
    issues: list[str]
    evidence: list[dict]


class ScorecardOut(BaseModel):
    restaurant_id: str
    restaurant_name: str
    score: float
    max_score: int
    status: str
    passing_threshold: int
    categories: list[CategoryResultOut]
    disclaimer: str
    computed_at: datetime


class CategoryDefOut(BaseModel):
    key: str
    name: str
    max_score: int


class HygieneAssessmentOut(BaseModel):
    id: str
    restaurant_id: str | None
    facility: str | None
    overall_score: float
    status: str
    passing_threshold: int
    categories: list[CategoryResultOut]
    created_at: datetime
