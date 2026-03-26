from app.recommender.schemas import FeatureInput
from app.recommender.service import generate_recommendations
from app.recommender.model import predict_recommendation_type


sample = FeatureInput(
    avg_glucose_24h=190,
    glucose_variability_24h=38,
    high_glucose_event_count_24h=4,
    low_glucose_event_count_24h=1,
    time_in_range_proxy_24h=0.45,
    glucose_trend_3d=12,
    glucose_trend_7d=9,
    steps_today=2500,
    steps_vs_baseline=-0.4,
    sleep_hours_last_night=5,
    sleep_vs_baseline=-2.0,
    missed_log_count=2,
    recommendation_ack_rate=0.3,
    last_recommendation_type=None,
    days_since_last_acknowledged_action=3,
)

# 🔹 ML prediction
ml_prediction = predict_recommendation_type(sample)
print("ML predicted type:", ml_prediction)

# 🔹 Rule-based recommendations
results = generate_recommendations(sample)

print("\nRule-based recommendations:")
for rec in results:
    print(rec.model_dump())