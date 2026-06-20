from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db_connect import get_db
from schema.category_schema import CategoryRequest, CategoryResponse, RecommendCategoryRequest, RecommendCategoryResponse
from service import category_service as service

from schema.expense_schema import ExpenseResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(body: CategoryRequest, db: Session = Depends(get_db)):
    return service.create(db, body)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(keyword: str = Query(None), db: Session = Depends(get_db)):
    return service.get_by_keyword(db, keyword)


@router.get("/recommend", response_model=list[RecommendCategoryResponse])
def get_recommendation(params: RecommendCategoryRequest = Depends(), db: Session = Depends(get_db)):
    return service.get_category_recommendation(db, params)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return service.get_by_id(db, category_id)


@router.get("/{category_id}/expenses", response_model=list[ExpenseResponse])
def get_expenses(category_id: int, db: Session = Depends(get_db)):
    return service.get_expenses(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, body: CategoryRequest, db: Session = Depends(get_db)):
    return service.update(db, category_id, body)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    service.remove(db, category_id)