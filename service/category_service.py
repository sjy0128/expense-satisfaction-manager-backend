from fastapi import HTTPException
from sqlalchemy.orm import Session

from data import category_repository as repository
from schema.category_schema import CategoryRequest, CategoryResponse, RecommendCategoryRequest, RecommendCategoryResponse
from service.category_recommend import recommend_categories

from data import expense_repository
from schema.expense_schema import ExpenseResponse


def create(db: Session, body: CategoryRequest) -> CategoryResponse:
    if len(body.category_color) != 6:
        raise HTTPException(status_code=422, detail="색상값은 6자리여야 합니다.")
    category = repository.insert(
        db=db,
        category_name=body.category_name,
        category_description=body.category_description,
        category_color=body.category_color,
    )
    return CategoryResponse.model_validate(category)


def get_all(db: Session) -> list[CategoryResponse]:
    return [CategoryResponse.model_validate(category) for category in repository.find_all(db)]


def get_by_id(db: Session, category_id: int) -> CategoryResponse:
    category = repository.find_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

    return CategoryResponse.model_validate(category)


def get_by_keyword(db: Session, keyword: str) -> list[CategoryResponse]:
    if not keyword:
        return get_all(db)
    return [CategoryResponse.model_validate(category) for category in repository.find_by_keyword(db, keyword)]


def update(db: Session, category_id: int, body: CategoryRequest) -> CategoryResponse:
    category = repository.find_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
    if len(body.category_color) != 6:
        raise HTTPException(status_code=422, detail="색상값은 6자리여야 합니다.")

    update_data = body.model_dump(exclude_unset=True)
    updated = repository.update(db, category, **update_data)

    return CategoryResponse.model_validate(updated)


def remove(db: Session, category_id: int) -> None:
    category = repository.find_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

    expense_repository.deactivate_category(db, category_id)
    repository.delete(db, category)


def get_expenses(db: Session, category_id: int) -> list[ExpenseResponse]:
    category = repository.find_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

    return [ExpenseResponse.model_validate(expense) for expense in category.expenses]


def get_category_recommendation(db: Session, params: RecommendCategoryRequest) -> list[RecommendCategoryResponse]:
    return recommend_categories(params, [category.category_name for category in get_all(db)])