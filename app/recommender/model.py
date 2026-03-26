import pickle
from pathlib import Path

import pandas as pd

from app.recommender.schemas import FeatureInput


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "recommendation_model.pkl"
ENCODER_PATH = BASE_DIR / "label_encoder.pkl"

FEATURE_COLUMNS = [
    "avg_glucose_24h",
    "glucose_variability_24h",
    "high_glucose_event_count_24h",
    "low_glucose_event_count_24h",
    "time_in_range_proxy_24h",
    "glucose_trend_3d",
    "glucose_trend_7d",
    "steps_today",
    "steps_vs_baseline",
    "sleep_hours_last_night",
    "sleep_vs_baseline",
    "missed_log_count",
    "recommendation_ack_rate",
    "days_since_last_acknowledged_action",
]


def load_model():
    with open(MODEL_PATH, "rb") as model_file:
        model = pickle.load(model_file)
    return model


def load_label_encoder():
    with open(ENCODER_PATH, "rb") as encoder_file:
        encoder = pickle.load(encoder_file)
    return encoder


def feature_input_to_dict(features: FeatureInput) -> dict:
    return {
        "avg_glucose_24h": features.avg_glucose_24h,
        "glucose_variability_24h": features.glucose_variability_24h,
        "high_glucose_event_count_24h": features.high_glucose_event_count_24h,
        "low_glucose_event_count_24h": features.low_glucose_event_count_24h,
        "time_in_range_proxy_24h": features.time_in_range_proxy_24h,
        "glucose_trend_3d": features.glucose_trend_3d,
        "glucose_trend_7d": features.glucose_trend_7d,
        "steps_today": features.steps_today,
        "steps_vs_baseline": features.steps_vs_baseline,
        "sleep_hours_last_night": features.sleep_hours_last_night,
        "sleep_vs_baseline": features.sleep_vs_baseline,
        "missed_log_count": features.missed_log_count,
        "recommendation_ack_rate": features.recommendation_ack_rate,
        "days_since_last_acknowledged_action": features.days_since_last_acknowledged_action,
    }


def predict_recommendation_type(features: FeatureInput) -> str:
    model = load_model()
    encoder = load_label_encoder()

    row_dict = feature_input_to_dict(features)
    row_df = pd.DataFrame([row_dict], columns=FEATURE_COLUMNS)

    prediction = model.predict(row_df)[0]
    decoded_label = encoder.inverse_transform([prediction])[0]

    return decoded_label