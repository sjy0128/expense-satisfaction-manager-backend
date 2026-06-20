from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from db_connect import Base


class Satisfaction(Base):
    __tablename__ = "satisfactions"

    satisfaction_id = Column(Integer, primary_key=True, autoincrement=True)
    expense = Column(Integer, ForeignKey('expenses.expense_id'), nullable=False, unique=True)
    score = Column(Integer, nullable=False)
    submitted_at = Column(DateTime, nullable=False, default=datetime.now())

    _expense = relationship("Expense", back_populates="satisfaction")