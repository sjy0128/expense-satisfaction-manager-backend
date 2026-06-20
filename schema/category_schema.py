from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryRequest(BaseModel):
    category_name: str
    category_description: Optional[str] = None
    category_color: Optional[str] = Field(min_length=6, max_length=6, default="000000")


class CategoryResponse(CategoryRequest):
    model_config = ConfigDict(from_attributes=True)

    category_id: int


class RecommendCategoryRequest(BaseModel):
    expense_title: str
    goods: str


class RecommendCategoryResponse(RecommendCategoryRequest):
    category_name: str
    confidence: float