from fastapi import HTTPException
from sqlalchemy.orm import Session

from data import expense_repository as repository
from schema.expense_schema import ExpenseRequest, GetExpenseRequest, ExpenseResponse, StatRequest, StatResponse

from schema.satisfaction_schema import SatisfactionResponse
from service.satisfaction_service import create as create_satisfaction


def create(db: Session, body: ExpenseRequest) -> ExpenseResponse:
    expense = repository.insert(
        db=db,
        expense_title=body.expense_title,
        goods=body.goods,
        place=body.place,
        expensed_at=body.expensed_at,
        price=body.price,
        payment_method=body.payment_method,
        category=body.category,
    )
    return ExpenseResponse.model_validate(expense)


def get_all(db: Session) -> list[ExpenseResponse]:
    return [ExpenseResponse.model_validate(expense) for expense in repository.find_all(db)]


def get_by_id(db: Session, expense_id: int) -> ExpenseResponse:
    expense = repository.find_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="지출내역을 찾을 수 없습니다.")

    return ExpenseResponse.model_validate(expense)


def get_by_condition(db: Session, params: GetExpenseRequest) -> list[ExpenseResponse]:
    return [ExpenseResponse.model_validate(expense) for expense in repository.find_expenses(
        db=db,
        keyword=params.keyword,
        page=params.page,
        size=params.size,
        payment_method=params.payment_method,
        category=params.category,
        order_by=params.order_by,
        order_direction=params.order_direction
    )]


def update(db: Session, expense_id: int, body: ExpenseRequest) -> ExpenseResponse:
    expense = repository.find_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="지출내역을 찾을 수 없습니다.")

    update_data = body.model_dump(exclude_unset=True)
    updated = repository.update(db, expense, **update_data)

    return ExpenseResponse.model_validate(updated)


def remove(db: Session, expense_id: int) -> None:
    expense = repository.find_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="지출내역을 찾을 수 없습니다.")

    repository.delete(db, expense)


def get_satisfaction(db: Session, expense_id: int) -> SatisfactionResponse:
    expense = repository.find_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="지출내역을 찾을 수 없습니다.")
    satisfaction = expense.satisfaction
    if not satisfaction:
        raise HTTPException(status_code=404, detail="만족도를 찾을 수 없습니다.")
    return SatisfactionResponse.model_validate(satisfaction)


def get_stats(db: Session, params: StatRequest) -> StatResponse:
    return StatResponse.model_validate(
        repository.calculate_stats(
            db=db,
            method_id=params.payment_method,
            category_id=params.category
        )
    )