from sqlalchemy.orm import Session

from model.payment_method_model import PaymentMethod, MethodType


def insert(db: Session,
    method_name: str,
    method_type: MethodType,
    method_description: str,
) -> PaymentMethod:
    payment_method = PaymentMethod(
        method_name=method_name,
        method_type=method_type,
        method_description=method_description,
    )
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    return payment_method


def find_all(db: Session) -> list[PaymentMethod]:
    return db.query(PaymentMethod).all()


def find_by_type(db: Session, _type: MethodType) -> list[PaymentMethod]:
    return db.query(PaymentMethod).filter(PaymentMethod.method_type == _type).all()


def find_by_id(db: Session, method_id: int) -> PaymentMethod | None:
    return db.query(PaymentMethod).filter(PaymentMethod.method_id == method_id).first()


def update(db: Session, payment_method: PaymentMethod, **kwargs):
    for key, value in kwargs.items():
        setattr(payment_method, key, value)

    db.commit()
    db.refresh(payment_method)
    return payment_method


def delete(db: Session, payment_method: PaymentMethod) -> None:
    db.delete(payment_method)
    db.commit()