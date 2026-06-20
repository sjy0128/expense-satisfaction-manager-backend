from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ExpenseRequest(BaseModel):
    expense_title: str
    goods: str
    place: Optional[str] = None
    expensed_at: Optional[datetime] = None
    price: float
    payment_method: Optional[int] = None
    category: Optional[int] = None


class GetExpenseRequest(BaseModel):
    keyword: Optional[str] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    payment_method: Optional[int] = None,
    category: Optional[int] = None,
    order_by: Optional[str] = None,
    order_direction: Optional[str] = None,


class ExpenseResponse(ExpenseRequest):
    model_config = ConfigDict(from_attributes=True)

    expense_id: int


class StatRequest(BaseModel):
    payment_method: Optional[int] = None
    category: Optional[int] = None


class StatResponse(StatRequest):
    count: int
    satisfaction_sum: float
    satisfaction_average: float
    satisfaction_max: float
    satisfaction_min: float
    price_sum: float
    price_average: float
    price_max: float
    price_min: float