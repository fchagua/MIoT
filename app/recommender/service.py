from app.recommender.schemas import FeatureInput, Recommendation
from app.recommender.rules import run_all_rules
from app.recommender.constraints import validate_safe_output


def generate_recommendations(features: FeatureInput) -> list[Recommendation]:
    raw_recommendations = run_all_rules(features)

    safe_recommendations = []
    seen_types = set()

    for rec in raw_recommendations:
        if rec.type in seen_types:
            continue

        validated = validate_safe_output(rec)
        safe_recommendations.append(validated)
        seen_types.add(rec.type)

    safe_recommendations.sort(
        key=lambda recommendation: (recommendation.priority, recommendation.confidence),
        reverse=True,
    )

    return safe_recommendations[:3]