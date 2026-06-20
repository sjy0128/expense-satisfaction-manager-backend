from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db_connect import get_db
from schema.expense_schema import ExpenseRequest, GetExpenseRequest, ExpenseResponse, StatRequest, StatResponse
from schema.satisfaction_schema import SatisfactionRequest, SatisfactionResponse
from service import expense_service as service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(body: ExpenseRequest, db: Session = Depends(get_db)):
    return service.create(db, body)


@router.post("/{expense_id}/satisfactions", response_model=SatisfactionResponse)
def create_satisfaction(expense_id: int, score: int = Query(), db: Session = Depends(get_db)):
    return service.create_satisfaction(db, SatisfactionRequest(expense=expense_id, score=score))


@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(params: GetExpenseRequest = Depends(), db: Session = Depends(get_db)):
    return service.get_by_condition(db, params)


@router.get("/stats", response_model=StatResponse)
def get_stats(params: StatRequest = Depends(), db: Session = Depends(get_db)):
    return service.get_stats(db, params)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return service.get_by_id(db, expense_id)


@router.get("/{expense_id}/satisfactions", response_model=SatisfactionResponse)
def get_satisfaction(expense_id: int, db: Session = Depends(get_db)):
    return service.get_satisfaction(db, expense_id)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, body: ExpenseRequest, db: Session = Depends(get_db)):
    return service.update(db, expense_id, body)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    service.remove(db, expense_id)