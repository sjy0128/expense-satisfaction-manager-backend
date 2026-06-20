from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db_connect import get_db
from schema.expense_schema import ExpenseResponse
from schema.payment_method_schema import PaymentMethodRequest, PaymentMethodResponse
from service import payment_method_service as service

from model.payment_method_model import MethodType

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])


@router.post("/", response_model=PaymentMethodResponse, status_code=201)
def create_method(body: PaymentMethodRequest, db: Session = Depends(get_db)):
    return service.create(db, body)


@router.get("/", response_model=list[PaymentMethodResponse])
def get_methods(_type: MethodType = Query(None), db: Session = Depends(get_db)):
    return service.get_by_type(db, _type)


@router.get("/{method_id}", response_model=PaymentMethodResponse)
def get_method(method_id: int, db: Session = Depends(get_db)):
    return service.get_by_id(db, method_id)


@router.get("/{method_id}/expenses", response_model=list[ExpenseResponse])
def get_expenses(method_id: int, db: Session = Depends(get_db)):
    return service.get_expenses(db, method_id)


@router.put("/{method_id}", response_model=PaymentMethodResponse)
def update_method(method_id: int, body: PaymentMethodRequest, db: Session = Depends(get_db)):
    return service.update(db, method_id, body)


@router.delete("/{method_id}", status_code=204)
def delete_method(method_id: int, db: Session = Depends(get_db)):
    service.remove(db, method_id)