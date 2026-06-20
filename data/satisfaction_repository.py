from datetime import datetime
from sqlalchemy.orm import Session

from model.satisfaction_model import Satisfaction


def insert(db: Session,
    expense:int,
    score:int,
) -> Satisfaction:
    satisfaction = Satisfaction(
        expense=expense,
        score=score,
    )
    db.add(satisfaction)
    db.commit()
    db.refresh(satisfaction)
    return satisfaction


def get_all(db: Session) -> list[Satisfaction]:
    return db.query(Satisfaction).all()


def get_by_id(db: Session, satisfaction_id: int) -> Satisfaction | None:
    return db.query(Satisfaction).filter(Satisfaction.satisfaction_id == satisfaction_id).first()


def update_score(db: Session, satisfaction: Satisfaction, score: int) -> Satisfaction:
    satisfaction.score = score
    satisfaction.submitted_at = datetime.now()
    db.commit()
    return satisfaction