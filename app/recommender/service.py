from datetime import datetime, UTC
from uuid import uuid4

from app.recommender.schemas import FeatureInput, Recommendation
from app.recommender.rules import run_all_rules
from app.recommender.constraints import validate_safe_output
from app.recommender.model import predict_recommendation_type

ALLOWED_ML_INJECTION_TYPES = {
    "activity_prompt",
    "adherence_reminder",
    "sleep_lifestyle_nudge",
    "glucose_monitoring_reminder",
}

def generate_recommendations(features: FeatureInput) -> list[Recommendation]:
    raw_recommendations = run_all_rules(features)
    ml_predicted_type = predict_recommendation_type(features)

    # Inject ML recommendation if not already present
    if (
    ml_predicted_type in ALLOWED_ML_INJECTION_TYPES
    and ml_predicted_type not in [r.type for r in raw_recommendations]
):
        ml_rec = Recommendation(
            recommendation_id=str(uuid4()),
            type=ml_predicted_type,
            priority=3,
            message="Based on recent patterns, this recommendation may be relevant.",
            explanation="Machine learning model suggested this recommendation based on historical patterns.",
            confidence=0.6,
            triggered_features=["ml_prediction"],
            timestamp=datetime.now(UTC),
        )
        raw_recommendations.append(ml_rec)

    safe_recommendations = []
    seen_types = set()

    for rec in raw_recommendations:
        if rec.type in seen_types:
            continue

        validated = validate_safe_output(rec)

        if validated.type == ml_predicted_type:
            validated.confidence = min(validated.confidence + 0.15, 1.0)
        else:
            validated.confidence = max(validated.confidence - 0.05, 0.0)

        safe_recommendations.append(validated)
        seen_types.add(validated.type)

    safe_recommendations.sort(
        key=lambda recommendation: (recommendation.priority, recommendation.confidence),
        reverse=True,
    )

    return safe_recommendations[:3]