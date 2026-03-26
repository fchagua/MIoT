import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import pickle


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


def main() -> None:
    df = pd.read_csv("data/sample_cases/training_data.csv")

    x = df[FEATURE_COLUMNS]
    y = df["label"]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(x, y_encoded)

    with open("app/recommender/recommendation_model.pkl", "wb") as model_file:
        pickle.dump(model, model_file)

    with open("app/recommender/label_encoder.pkl", "wb") as encoder_file:
        pickle.dump(encoder, encoder_file)

    print("Model and label encoder saved successfully.")


if __name__ == "__main__":
    main()