import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

from app.recommender.schemas import FeatureInput
from app.recommender.service import generate_recommendations


DATA_PATH = "data/sample_cases/training_data.csv"


def row_to_feature_input(row: pd.Series) -> FeatureInput:
    return FeatureInput(
        avg_glucose_24h=row["avg_glucose_24h"],
        glucose_variability_24h=row["glucose_variability_24h"],
        high_glucose_event_count_24h=row["high_glucose_event_count_24h"],
        low_glucose_event_count_24h=row["low_glucose_event_count_24h"],
        time_in_range_proxy_24h=row["time_in_range_proxy_24h"],
        glucose_trend_3d=row["glucose_trend_3d"],
        glucose_trend_7d=row["glucose_trend_7d"],
        steps_today=row["steps_today"],
        steps_vs_baseline=row["steps_vs_baseline"],
        sleep_hours_last_night=row["sleep_hours_last_night"],
        sleep_vs_baseline=row["sleep_vs_baseline"],
        missed_log_count=row["missed_log_count"],
        recommendation_ack_rate=row["recommendation_ack_rate"],
        last_recommendation_type=None,
        days_since_last_acknowledged_action=row["days_since_last_acknowledged_action"],
    )


def evaluate() -> None:
    df = pd.read_csv(DATA_PATH)

    X = df.drop(columns=["label"])
    y = df["label"]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test, y_labels_train, y_labels_test = train_test_split(
        X, y_encoded, y, test_size=0.3, random_state=42
    )

    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred_labels = encoder.inverse_transform(y_pred)

    hybrid_preds = []
    for _, row in X_test.iterrows():
        features = row_to_feature_input(row)
        hybrid_results = generate_recommendations(features)
        hybrid_top = hybrid_results[0].type if hybrid_results else "no_recommendation"
        hybrid_preds.append(hybrid_top)

    print("ML Test Accuracy:", accuracy_score(y_labels_test, y_pred_labels))
    print("Hybrid Test Accuracy:", accuracy_score(y_labels_test, hybrid_preds))

    print("\nML Classification Report:")
    print(classification_report(y_labels_test, y_pred_labels, zero_division=0))

    print("\nHybrid Classification Report:")
    print(classification_report(y_labels_test, hybrid_preds, zero_division=0))


if __name__ == "__main__":
    evaluate()