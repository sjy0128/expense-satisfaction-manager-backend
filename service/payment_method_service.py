from fastapi import HTTPException
from sqlalchemy.orm import Session

from data import payment_method_repository as repository
from schema.payment_method_schema import PaymentMethodRequest, PaymentMethodResponse

from model.payment_method_model import MethodType
from data import expense_repository
from schema.expense_schema import ExpenseResponse


def create(db: Session, body: PaymentMethodRequest) -> PaymentMethodResponse:
    payment_method = repository.insert(
        db=db,
        method_name=body.method_name,
        method_type=body.method_type,
        method_description=body.method_description,
    )
    return PaymentMethodResponse.model_validate(payment_method)


def get_all(db: Session) -> list[PaymentMethodResponse]:
    return [PaymentMethodResponse.model_validate(payment_method) for payment_method in repository.find_all(db)]


def get_by_id(db: Session, method_id: int) -> PaymentMethodResponse:
    payment_method = repository.find_by_id(db, method_id)
    if not payment_method:
        raise HTTPException(status_code=404, detail="결제수단을 찾을 수 없습니다.")

    return PaymentMethodResponse.model_validate(payment_method)


def get_by_type(db: Session, _type: MethodType) -> list[PaymentMethodResponse]:
    if not _type:
        return get_all(db)
    return [PaymentMethodResponse.model_validate(payment_method) for payment_method in repository.find_by_type(db, _type)]


def update(db: Session, method_id: int, body: PaymentMethodRequest) -> PaymentMethodResponse:
    payment_method = repository.find_by_id(db, method_id)
    if not payment_method:
        raise HTTPException(status_code=404, detail="결제수단을 찾을 수 없습니다.")

    update_data = body.model_dump(exclude_unset=True)
    updated = repository.update(db, payment_method, **update_data)

    return PaymentMethodResponse.model_validate(updated)


def remove(db: Session, method_id: int) -> None:
    payment_method = repository.find_by_id(db, method_id)
    if not payment_method:
        raise HTTPException(status_code=404, detail="결제수단을 찾을 수 없습니다.")

    expense_repository.deactivate_payment_method(db, method_id)
    repository.delete(db, payment_method)


def get_expenses(db: Session, method_id: int) -> list[ExpenseResponse]:
    payment_method = repository.find_by_id(db, method_id)
    if not payment_method:
        raise HTTPException(status_code=404, detail="결제수단을 찾을 수 없습니다.")

    return [ExpenseResponse.model_validate(expense) for expense in payment_method.expenses]