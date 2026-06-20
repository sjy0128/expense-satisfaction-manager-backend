"""
기존 지출 내역 + 만족도 데이터를 기반으로,
- 상품명(goods) 유사도
- 가격(price) 유사도
- 장소(place) 일치 여부
- 카테고리(category) 일치 여부
- 결제수단(payment_method) 일치 여부

각 항목별로 "유사한 과거 지출들의 평균 만족도"를 구한 뒤,
가중합으로 최종 만족도를 예측합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from fastapi import HTTPException
from typing import Optional

from model.satisfaction_model import Satisfaction
from schema.expense_schema import ExpenseRequest


# ── 설정값: 필요에 따라 조정 가능 ──
MIN_DATA_COUNT = 5          # 이 개수 이하이면 예측 자체를 거부
PRICE_TOLERANCE = 0.2       # 가격 유사 판정 기준 (±20%)
GOODS_SIMILARITY_THRESHOLD = 0.4  # 상품명 유사도 최소 기준 (0~1)
PLACE_SIMILARITY_THRESHOLD = 0.4  # 장소 유사도 최소 기준 (0~1)

# 항목별 기본 가중치 (합 1.0). 매칭 데이터가 없는 항목은 제외 후 재정규화됨.
DEFAULT_WEIGHTS = {
    "goods": 0.30,
    "price": 0.15,
    "place": 0.15,
    "category": 0.20,
    "payment_method": 0.20,
}


@dataclass
class FeatureResult:
    score: Optional[float]      # 해당 항목의 평균 만족도 (매칭 없으면 None)
    matched_count: int          # 매칭된 과거 지출 개수
    weight_used: float = 0.0    # 재정규화 후 실제 적용된 가중치


@dataclass
class PredictionResult:
    predicted_score: float
    used_sample_count: int  # 만족도가 등록된 전체 지출 건수(전체 후보군 크기, 실제 매칭 건수는 breakdown[*].matched_count 참고)
    breakdown: dict = field(default_factory=dict)  # 항목명 -> FeatureResult


def _text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _weighted_avg(pairs: list[tuple[float, float]]) -> Optional[float]:
    """(score, weight) 쌍 리스트를 받아 가중평균 계산. weight는 유사도 등으로 사용 가능."""
    total_weight = sum(w for _, w in pairs)
    if total_weight <= 0:
        return None
    return sum(s * w for s, w in pairs) / total_weight


def _fetch_history(satisfactions: list[Satisfaction]) -> list[Satisfaction]:
    """입력받은 satisfaction 리스트를 그대로 반환 (필요 없는 항목 필터링 등 확장 지점)"""
    return list(satisfactions)


def _score_by_goods(target_goods: str, satisfactions: list[Satisfaction]) -> FeatureResult:
    pairs = []
    matched = 0
    for satisfaction in satisfactions:
        sim = _text_similarity(target_goods, satisfaction._expense.goods)
        if sim >= GOODS_SIMILARITY_THRESHOLD:
            pairs.append((satisfaction.score, sim))
            matched += 1
    return FeatureResult(score=_weighted_avg(pairs), matched_count=matched)


def _score_by_price(target_price: float, satisfactions: list[Satisfaction]) -> FeatureResult:
    pairs = []
    matched = 0
    if target_price <= 0:
        return FeatureResult(score=None, matched_count=0)
    for satisfaction in satisfactions:
        expense_price = satisfaction._expense.price
        if expense_price is None:
            continue
        diff_ratio = abs(expense_price - target_price) / target_price
        if diff_ratio <= PRICE_TOLERANCE:
            # 차이가 적을수록 가중치를 높게 (1에 가까울수록 유사)
            closeness = 1.0 - (diff_ratio / PRICE_TOLERANCE)
            pairs.append((satisfaction.score, max(closeness, 0.01)))
            matched += 1
    return FeatureResult(score=_weighted_avg(pairs), matched_count=matched)


def _score_by_place(target_place: Optional[str], satisfactions: list[Satisfaction]) -> FeatureResult:
    if not target_place:
        return FeatureResult(score=None, matched_count=0)
    pairs = []
    matched = 0
    for satisfaction in satisfactions:
        expense_place = satisfaction._expense.place
        if not expense_place:
            continue
        sim = _text_similarity(target_place, expense_place)
        if sim >= PLACE_SIMILARITY_THRESHOLD:
            pairs.append((satisfaction.score, sim))
            matched += 1
    return FeatureResult(score=_weighted_avg(pairs), matched_count=matched)


def _score_by_category(target_category: Optional[int], satisfactions: list[Satisfaction]) -> FeatureResult:
    if target_category is None:
        return FeatureResult(score=None, matched_count=0)
    pairs = []
    matched = 0
    for satisfaction in satisfactions:
        if satisfaction._expense.category == target_category:
            pairs.append((satisfaction.score, 1.0))
            matched += 1
    return FeatureResult(score=_weighted_avg(pairs), matched_count=matched)


def _score_by_payment_method(target_method: Optional[int], satisfactions: list[Satisfaction]) -> FeatureResult:
    if target_method is None:
        return FeatureResult(score=None, matched_count=0)
    pairs = []
    matched = 0
    for satisfaction in satisfactions:
        if satisfaction._expense.payment_method == target_method:
            pairs.append((satisfaction.score, 1.0))
            matched += 1
    return FeatureResult(score=_weighted_avg(pairs), matched_count=matched)


def predict_satisfaction(
    satisfactions: list[Satisfaction],
    target: ExpenseRequest,
) -> PredictionResult:
    """
    지출 예정 항목(target)에 대해 예상 만족도를 예측합니다.

    Args:
        satisfactions: 만족도가 등록된 Satisfaction 객체 리스트.
                        각 Satisfaction은 ._expense relationship으로 연결된 지출 정보를 가지고 있어야 합니다.
                        예: db.query(Satisfaction).all()
        target: 예측 대상 지출 정보 (ExpenseRequest)

    Returns:
        PredictionResult: 예측 점수와 항목별 근거

    Raises:
        InsufficientDataError: 학습 가능한 만족도 데이터가 MIN_DATA_COUNT 이하이거나,
                                어떤 항목도 유사/일치하는 과거 지출이 없을 때
    """
    rows = _fetch_history(satisfactions)

    if len(rows) <= MIN_DATA_COUNT:
        raise HTTPException(
            status_code=422,
            detail=f"만족도 예측을 위한 데이터가 부족합니다. (현재 {len(rows)}건, 최소 {MIN_DATA_COUNT + 1}건 필요)"
        )

    results: dict[str, FeatureResult] = {
        "goods": _score_by_goods(target.goods, rows),
        "price": _score_by_price(target.price, rows),
        "place": _score_by_place(target.place, rows),
        "category": _score_by_category(target.category, rows),
        "payment_method": _score_by_payment_method(target.payment_method, rows),
    }

    # 매칭된 항목만 남기고 가중치 재정규화
    available = {k: v for k, v in results.items() if v.score is not None}

    if not available:
        # 어떤 항목도 유사/일치하는 과거 지출이 없으면 예측 불가로 처리
        raise HTTPException(status_code=422, detail="유사한 과거 지출 내역이 없어 만족도를 예측할 수 없습니다.")

    total_base_weight = sum(DEFAULT_WEIGHTS[k] for k in available)
    final_score = 0.0
    for key, feature in available.items():
        normalized_weight = DEFAULT_WEIGHTS[key] / total_base_weight
        feature.weight_used = round(normalized_weight, 4)
        final_score += feature.score * normalized_weight

    final_score = max(0.0, min(100.0, final_score))

    return PredictionResult(
        predicted_score=round(final_score, 2),
        used_sample_count=len(rows),
        breakdown=results,
    )