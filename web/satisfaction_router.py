from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db_connect import get_db
from schema.satisfaction_schema import SatisfactionResponse
from service import satisfaction_service as service

from schema.expense_schema import ExpenseRequest

router = APIRouter(prefix="/satisfactions", tags=["satisfactions"])


@router.get("/predict", response_model=dict)
def predict_satisfaction(params: ExpenseRequest = Depends(), db: Session = Depends(get_db)):
    return {"prediction": service.get_satisfaction_prediction(db, params)}


@router.patch("/{satisfaction_id}", response_model=SatisfactionResponse)
def update_satisfaction_score(satisfaction_id: int, db: Session = Depends(get_db), score: int = Query()):
    return service.update_score(db, satisfaction_id, score)