from sqlalchemy import Column, Integer, String, Enum as _Enum
from enum import Enum

from sqlalchemy.orm import relationship

from db_connect import Base
from model.expense_model import Expense


class MethodType(Enum):
    CASH = "현금"
    CARD = "카드"
    PAY = "페이"
    ACCOUNT = "계좌"
    PHONE = "휴대폰"
    OTHER = "기타"


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    method_id = Column(Integer, primary_key=True, autoincrement=True)
    method_name = Column(String, nullable=False, unique=True)
    method_type = Column(_Enum(MethodType), nullable=False)
    method_description = Column(String)

    expenses = relationship("Expense", foreign_keys=[Expense.payment_method])