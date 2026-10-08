from pydantic import BaseModel, Field
import uuid


class MinimalSource(BaseModel):
    """MinimalSource model"""
    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """UnansweredQuestion model"""
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """AnsweredQuestion model"""
    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """RagDataset model"""
    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """MinimalSearchResults model"""
    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """MinimalAnswer model"""
    answer: str


class StudentSearchResults(BaseModel):
    """StudentSearchResults model"""
    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """StudentSearchResultsAndAnswer model"""
    search_results: list[MinimalAnswer]
    k: int
