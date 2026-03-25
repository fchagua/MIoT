from datetime import datetime, UTC
from uuid import uuid4
from typing import List

from app.recommender.schemas import FeatureInput, Recommendation


def rule_sustained_high_trend(features: FeatureInput) -> Recommendation | None:
    if features.avg_glucose_24h > 180 and features.glucose_trend_3d > 10:
        return Recommendation(
            recommendation_id=str(uuid4()),
            type="glucose_monitoring_reminder",
            priority=5,
            message="Your recent glucose pattern has been running higher than usual. Continue monitoring closely today.",
            explanation="Average glucose over the last 24 hours is elevated and the 3-day trend is increasing.",
            confidence=0.88,
            triggered_features=["avg_glucose_24h", "glucose_trend_3d"],
            timestamp=datetime.now(UTC),
            requires_clinician_followup=False,
        )
    return None


def rule_repeated_lows(features: FeatureInput) -> Recommendation | None:
    if features.low_glucose_event_count_24h >= 2:
        return Recommendation(
            recommendation_id=str(uuid4()),
            type="clinician_followup_suggestion",
            priority=5,
            message="You have had several low-glucose events recently. Monitor closely and consider contacting your clinician if this pattern continues.",
            explanation="Multiple low-glucose events were detected in the last 24 hours.",
            confidence=0.92,
            triggered_features=["low_glucose_event_count_24h"],
            timestamp=datetime.now(UTC),
            requires_clinician_followup=True,
        )
    return None


def rule_low_activity(features: FeatureInput) -> Recommendation | None:
    if features.steps_vs_baseline < -0.3:
        return Recommendation(
            recommendation_id=str(uuid4()),
            type="activity_prompt",
            priority=3,
            message="Your activity today is below your usual level. A light walk or gentle movement may help support your routine.",
            explanation="Step count is significantly below your personal baseline.",
            confidence=0.76,
            triggered_features=["steps_vs_baseline"],
            timestamp=datetime.now(UTC),
        )
    return None


def rule_poor_sleep_and_variability(features: FeatureInput) -> Recommendation | None:
    if features.sleep_vs_baseline < -1.5 and features.glucose_variability_24h > 35:
        return Recommendation(
            recommendation_id=str(uuid4()),
            type="sleep_lifestyle_nudge",
            priority=4,
            message="Your recent sleep was lower than usual. Try to maintain a steady routine and keep monitoring your glucose pattern.",
            explanation="Sleep dropped below baseline and glucose variability is elevated.",
            confidence=0.81,
            triggered_features=["sleep_vs_baseline", "glucose_variability_24h"],
            timestamp=datetime.now(UTC),
        )
    return None


def rule_low_adherence(features: FeatureInput) -> Recommendation | None:
    if features.missed_log_count >= 2 or features.recommendation_ack_rate < 0.4:
        return Recommendation(
            recommendation_id=str(uuid4()),
            type="adherence_reminder",
            priority=4,
            message="A few recent care-tracking actions seem to have been missed. Try to keep your logs and check-ins consistent.",
            explanation="Low acknowledgement rate or missed logs suggest reduced adherence to routine tracking.",
            confidence=0.79,
            triggered_features=["missed_log_count", "recommendation_ack_rate"],
            timestamp=datetime.now(UTC),
        )
    return None


def run_all_rules(features: FeatureInput) -> List[Recommendation]:
    recommendations = []

    for rule in [
        rule_sustained_high_trend,
        rule_repeated_lows,
        rule_low_activity,
        rule_poor_sleep_and_variability,
        rule_low_adherence,
    ]:
        result = rule(features)
        if result is not None:
            recommendations.append(result)

    return recommendations