from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db_connect import Base
from model.expense_model import Expense


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False, unique=True)
    category_description = Column(String)
    category_color = Column(String)

    expenses = relationship("Expense", foreign_keys=[Expense.category])