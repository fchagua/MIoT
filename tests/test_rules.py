from app.recommender.schemas import FeatureInput
from app.recommender.rules import (
    rule_sustained_high_trend,
    rule_repeated_lows,
)


def test_rule_sustained_high_trend_triggers():
    features = FeatureInput(
        avg_glucose_24h=200,
        glucose_variability_24h=25,
        high_glucose_event_count_24h=3,
        low_glucose_event_count_24h=0,
        time_in_range_proxy_24h=0.4,
        glucose_trend_3d=20,
        glucose_trend_7d=15,
        steps_today=4000,
        steps_vs_baseline=-0.2,
        sleep_hours_last_night=7,
        sleep_vs_baseline=0.0,
        missed_log_count=0,
        recommendation_ack_rate=0.9,
        last_recommendation_type=None,
        days_since_last_acknowledged_action=1,
    )

    rec = rule_sustained_high_trend(features)
    assert rec is not None
    assert rec.type == "glucose_monitoring_reminder"


def test_rule_repeated_lows_triggers():
    features = FeatureInput(
        avg_glucose_24h=120,
        glucose_variability_24h=20,
        high_glucose_event_count_24h=0,
        low_glucose_event_count_24h=2,
        time_in_range_proxy_24h=0.8,
        glucose_trend_3d=0,
        glucose_trend_7d=0,
        steps_today=5000,
        steps_vs_baseline=0.0,
        sleep_hours_last_night=7,
        sleep_vs_baseline=0.0,
        missed_log_count=0,
        recommendation_ack_rate=0.8,
        last_recommendation_type=None,
        days_since_last_acknowledged_action=0,
    )

    rec = rule_repeated_lows(features)
    assert rec is not None
    assert rec.type == "clinician_followup_suggestion"