from typing import List
from pydantic import BaseModel


class MatchingRunSchema(BaseModel):
    jobId: int
    resumeIds: List[int]
