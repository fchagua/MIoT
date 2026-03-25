from app.recommender.schemas import Recommendation

UNSAFE_TERMS = [
    "diagnose",
    "prescribe",
    "increase dose",
    "decrease dose",
    "change medication",
    "stop medication",
    "start medication",
]


def validate_safe_output(recommendation: Recommendation) -> Recommendation:
    text = f"{recommendation.message} {recommendation.explanation}".lower()

    for term in UNSAFE_TERMS:
        if term in text:
            raise ValueError(f"Unsafe recommendation language detected: {term}")

    return recommendation