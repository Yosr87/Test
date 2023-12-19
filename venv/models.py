from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class RequestCreate(BaseModel):
    author: int
    vacation_start_date: datetime
    vacation_end_date: datetime

class RequestResponse(RequestCreate):
    id: int
    status: str
    resolved_by: Optional[int]
    request_created_at: datetime