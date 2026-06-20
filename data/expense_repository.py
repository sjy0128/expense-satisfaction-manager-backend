from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from model.expense_model import Expense
from model.satisfaction_model import Satisfaction


def insert(db: Session,
    expense_title: str,
    goods: str,
    place: str,
    expensed_at: datetime,
    price: float,
    payment_method: int,
    category: int,
) -> Expense:
    expense = Expense(
        expense_title=expense_title,
        goods=goods,
        place=place,
        expensed_at=expensed_at,
        price=price,
        payment_method=payment_method,
        category=category,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def find_all(db: Session) -> list[Expense]:
    return db.query(Expense).all()


def find_expenses(
    db: Session,
    keyword: str = None,
    page: int = None,
    size: int = None,
    payment_method: int = None,
    category: int = None,
    order_by: str = None,
    order_direction: str = None
) -> list[Expense]:
    query = db.query(Expense)
    if keyword is not None:
        query = query.filter(Expense.expense_title.like(f"%{keyword}%") | Expense.goods.like(f"%{keyword}%"))
    if payment_method is not None:
        query = query.filter(Expense.payment_method == payment_method)
    if category is not None:
        query = query.filter(Expense.category == category)
    if order_by is not None:
        if order_direction == "desc":
            query = query.order_by(getattr(Expense, order_by, Expense.expense_id).desc())
        else:
            query = query.order_by(getattr(Expense, order_by, Expense.expense_id).asc())
    else:
        query = query.order_by(Expense.expense_id.desc())
    if page is not None and size is not None:
        query = query.offset((page - 1) * size).limit(size)

    return query.all()


def find_by_id(db: Session, expense_id: int) -> Expense | None:
    return db.query(Expense).filter(Expense.expense_id == expense_id).first()


def update(db: Session, expense: Expense, **kwargs):
    for key, value in kwargs.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


def deactivate_payment_method(db: Session, method_id: int) -> None:
    db.query(Expense).filter(Expense.payment_method == method_id).update({"payment_method": None})


def deactivate_category(db: Session, category_id: int) -> None:
    db.query(Expense).filter(Expense.category == category_id).update({"category": None})


def delete(db: Session, expense: Expense) -> None:
    db.delete(expense)
    db.commit()


def calculate_stats(db: Session, method_id: int, category_id: int) -> dict[str, int | float]:
    query = db.query(
        func.count(Expense.expense_id).label("count"),
        func.sum(Satisfaction.score).label("satisfaction_sum"),
        func.avg(Satisfaction.score).label("satisfaction_average"),
        func.max(Satisfaction.score).label("satisfaction_max"),
        func.min(Satisfaction.score).label("satisfaction_min"),
        func.sum(Expense.price).label("price_sum"),
        func.avg(Expense.price).label("price_average"),
        func.max(Expense.price).label("price_max"),
        func.min(Expense.price).label("price_min"),
    ).join(Expense.satisfaction)
    if method_id is not None:
        query = query.filter(Expense.payment_method == method_id)
    if category_id is not None:
        query = query.filter(Expense.category == category_id)
    return dict(query.first()._mapping)