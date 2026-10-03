import pandas as pd

from metrics.brand_health import calculate_brand_health
from sentiment.sentiment_analyzer import analyze_file, is_brand_relevant


def test_play_store_review_relevant_without_brand_name():
    assert is_brand_relevant("my money", "Google Play")


def test_other_source_needs_keyword():
    assert not is_brand_relevant("MTN data is slow", "Nairametrics")
    assert is_brand_relevant("I use OPay daily", "Nairametrics")


def test_pipeline_filters_and_scores(tmp_path):
    raw = pd.DataFrame({
        "id": ["1", "2", "3", "4"],
        "brand": ["OPay"] * 4,
        "text": ["great and reliable", "terrible and slow",
                 "unrelated news about mtn is bad", "ok"],
        "rating": [5, 1, 3, 3],
        "date": ["2026-10-01"] * 4,
        "source": ["Google Play", "Google Play", "Blog", "Google Play"],
        "source_type": ["Customer Review"] * 4,
        "url": [""] * 4,
    })
    raw_file, out_file = tmp_path / "raw.csv", tmp_path / "out.csv"
    raw.to_csv(raw_file, index=False)

    analyze_file(str(raw_file), str(out_file))
    result = calculate_brand_health(str(out_file))

    assert result["total_mentions"] == 3          # blog row filtered out
    assert result["positive_count"] == 1
    assert result["negative_count"] == 1
    assert result["neutral_count"] == 1
