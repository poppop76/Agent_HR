from pydantic import BaseModel, Field
from typing import Optional, List, Union


class getResume(BaseModel):
    resumeId: int


class InterviewQuestionsRequest(BaseModel):
    candidateId: int
    jobId: Optional[int] = None
    questionCount: Optional[int] = 5
    questionTypes: Optional[List[str]] = None


class ResumeSummaryRequest(BaseModel):
    candidateId: int
    summaryLength: Optional[str] = "medium"


class SalarySuggestionRequest(BaseModel):
    candidateId: int
    jobId: Optional[int] = None


class ChatQueryRequest(BaseModel):
    question: str
    context: Optional[dict] = None


class ReportGenerateRequest(BaseModel):
    reportType: str  # weekly/monthly/quarterly/recruitment
    dateRange: Optional[List[str]] = None
    params: Optional[dict] = None


class CandidateCompareRequest(BaseModel):
    resumeIds: List[int]
    dimensions: Optional[List[str]] = None


class TalentPredictRequest(BaseModel):
    jobId: Union[int, str] = Field(description="岗位 ID")
    topN: Optional[int] = 5


class ChatHistoryRequest(BaseModel):
    """获取会话历史记录请求"""
    session_id: str


class SessionListRequest(BaseModel):
    """获取会话列表请求"""
    user_id: Optional[int] = None


class SessionSwitchRequest(BaseModel):
    """切换会话请求"""
    old_session_id: str
    new_session_id: str
    user_id: Optional[int] = None