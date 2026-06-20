from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SatisfactionRequest(BaseModel):
    expense: int
    score: int = Field(ge=0, le=100)


class SatisfactionResponse(SatisfactionRequest):
    model_config = ConfigDict(from_attributes=True)

    satisfaction_id: int
    submitted_at: datetime