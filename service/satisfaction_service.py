from fastapi import HTTPException
from sqlalchemy.orm import Session

from data import satisfaction_repository as repository
from schema.expense_schema import ExpenseRequest
from schema.satisfaction_schema import SatisfactionRequest, SatisfactionResponse
from service.satisfaction_predict import predict_satisfaction

from data import expense_repository


def create(db: Session, body: SatisfactionRequest) -> SatisfactionResponse:
    expense = expense_repository.find_by_id(db, body.expense)
    if not expense:
        raise HTTPException(status_code=404, detail="지출내역을 찾을 수 없습니다.")
    if expense.satisfaction:
        raise HTTPException(status_code=409, detail="이미 만족도조사를 한 지출입니다.")
    if not 100 >= body.score >= 0:
        raise HTTPException(status_code=422, detail="만족도 점수는 0 이상 100 이하여야 합니다.")
    satisfaction = repository.insert(
        db=db,
        expense=body.expense,
        score=body.score,
    )
    return SatisfactionResponse.model_validate(satisfaction)


def update_score(db: Session, satisfaction_id: int, score: int) -> SatisfactionResponse:
    satisfaction = repository.get_by_id(db, satisfaction_id)
    if not satisfaction:
        raise HTTPException(status_code=404, detail="만족도를 찾을 수 없습니다.")
    if not 100 >= score >= 0:
        raise HTTPException(status_code=422, detail="만족도 점수는 0 이상 100 이하여야 합니다.")
    updated = repository.update_score(db, satisfaction, score)
    return SatisfactionResponse.model_validate(updated)


def get_satisfaction_prediction(db: Session, params: ExpenseRequest) -> float:
    return predict_satisfaction(repository.get_all(db), params).predicted_score