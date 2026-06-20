from transformers import pipeline
from schema.category_schema import RecommendCategoryRequest, RecommendCategoryResponse

classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")


def recommend_categories(
    params: RecommendCategoryRequest,
    categories: list[str]
) -> list[RecommendCategoryResponse]:
    sentence = params.expense_title + " " + params.goods
    if not categories:
        return []

    outputs = classifier(sentence, candidate_labels=categories)

    labels = outputs["labels"]
    confidences = outputs["scores"]

    results = [
        RecommendCategoryResponse(
            expense_title=params.expense_title,
            goods=params.goods,
            category_name=labels[i],
            confidence=float(confidences[i]),
        ) for i in range(len(categories))
    ]

    sorted_results = sorted(results, key=lambda x: x.confidence, reverse=True)

    return sorted_results[: min(5, len(categories))]