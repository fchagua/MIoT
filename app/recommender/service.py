from app.recommender.schemas import FeatureInput, Recommendation
from app.recommender.rules import run_all_rules
from app.recommender.constraints import validate_safe_output
from app.recommender.model import predict_recommendation_type


def generate_recommendations(features: FeatureInput) -> list[Recommendation]:
    raw_recommendations = run_all_rules(features)
    ml_predicted_type = predict_recommendation_type(features)

    safe_recommendations = []
    seen_types = set()

    for rec in raw_recommendations:
        if rec.type in seen_types:
            continue

        validated = validate_safe_output(rec)

        if validated.type == ml_predicted_type:
            validated.confidence = min(validated.confidence + 0.10, 1.0)

        safe_recommendations.append(validated)
        seen_types.add(validated.type)

    safe_recommendations.sort(
        key=lambda recommendation: (recommendation.priority, recommendation.confidence),
        reverse=True,
    )

    return safe_recommendations[:3]