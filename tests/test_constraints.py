from datetime import datetime
import pytest

from app.recommender.schemas import Recommendation
from app.recommender.constraints import validate_safe_output


def test_validate_safe_output_rejects_unsafe_terms():
    rec = Recommendation(
        recommendation_id="1",
        type="adherence_reminder",
        priority=3,
        message="You should increase dose immediately.",
        explanation="Unsafe wording example.",
        confidence=0.8,
        triggered_features=["test_feature"],
        timestamp=datetime.now(),
    )

    with pytest.raises(ValueError):
        validate_safe_output(rec)