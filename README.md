# MIoT Recommender System
A rule-based and extensible machine learning recommendation engine for patient monitoring using IoT data (glucose, activity, sleep, and adherence signals).

## Overview
This module analyzes patient-generated health data and produces personalized, non-diagnostic recommendations to support better self-management and clinical awareness. By synthesizing multiple data streams, it identifies behavioral patterns and physiological trends to provide timely, actionable nudges.

## API
### Endpoint
POST /recommendations

## Request Format
The API expects a JSON payload with engineered features representing the patient's state over various windows (24h, 3d, 7d):

JSON
{
  "avg_glucose_24h": 190,
  "glucose_variability_24h": 38,
  "high_glucose_event_count_24h": 4,
  "low_glucose_event_count_24h": 1,
  "time_in_range_proxy_24h": 0.45,
  "glucose_trend_3d": 12,
  "glucose_trend_7d": 9,
  "steps_today": 2500,
  "steps_vs_baseline": -0.4,
  "sleep_hours_last_night": 5,
  "sleep_vs_baseline": -2.0,
  "missed_log_count": 2,
  "recommendation_ack_rate": 0.3,
  "last_recommendation_type": null,
  "days_since_last_acknowledged_action": 3
}
## Response Format
Returns a list of recommendation objects:

JSON
[
  {
    "recommendation_id": "string",
    "type": "glucose_monitoring_reminder",
    "priority": 5,
    "message": "Your recent glucose pattern has been running higher than usual.",
    "explanation": "Average glucose is elevated and trend is increasing.",
    "confidence": 0.88,
    "triggered_features": ["avg_glucose_24h", "glucose_trend_3d"],
    "timestamp": "2026-03-25T22:58:23Z",
    "safe_for_display": true,
    "requires_clinician_followup": false
  }
]
## Constraints & Logic
Capacity: Maximum of 3 recommendations per request.

Ranking: Results are sorted by priority (1-10) and confidence (0.0-1.0).

Safety: Outputs are strictly non-diagnostic (no prescriptions or medical decisions).

Validation: Invalid inputs (e.g., missing fields or out-of-range values) return a 422 Unprocessable Entity error.

## Recommendation Types
The engine categorizes nudges into the following functional types:

adherence_reminder: Prompted when logging or medication windows are missed.

activity_prompt: Triggered by significant drops in step count vs. baseline.

meal_consistency_prompt: Suggested when glucose spikes correlate with irregular timing.

glucose_monitoring_reminder: High-priority nudge for frequent OOR (Out of Range) readings.

sleep_lifestyle_nudge: Behavioral advice when sleep debt impacts glucose stability.

clinician_followup_suggestion: Escalation when 7-day trends show persistent degradation.

## Getting Started
### 1. Clone the repository
Bash
git clone <your-repo-url>
cd <your-repo-name>
### 2. Create and activate virtual environment
Bash
python -m venv venv
Windows: venv\Scripts\activate

Mac/Linux: source venv/bin/activate

### 3. Install dependencies
Bash
pip install -r requirements.txt
## Running the API
Start the local development server using Uvicorn:

Bash
uvicorn app.main:app --reload
## API Documentation
Once the server is running, you can access the interactive documentation at:

### Swagger UI: http://127.0.0.1:8000/docs

### ReDoc: http://127.0.0.1:8000/redoc