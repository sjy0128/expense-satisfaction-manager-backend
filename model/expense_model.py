from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Double
from sqlalchemy.orm import relationship

from db_connect import Base
from model.satisfaction_model import Satisfaction


class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    expense_title = Column(String, nullable=False)
    goods = Column(String, nullable=False)
    place = Column(String)
    expensed_at = Column(DateTime, nullable=False)
    price = Column(Double, nullable=False)

    payment_method = Column(Integer, ForeignKey("payment_methods.method_id"))
    category = Column(Integer, ForeignKey("categories.category_id"))

    satisfaction = relationship("Satisfaction", back_populates="_expense", foreign_keys=[Satisfaction.expense], uselist=False)