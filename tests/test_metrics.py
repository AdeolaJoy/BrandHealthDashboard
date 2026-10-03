import pandas as pd

from metrics.brand_health import (
    daily_trend, period_change, rating_crosscheck, summarize, top_terms,
)


def make(rows):
    df = pd.DataFrame(rows, columns=["date", "sentiment", "rating", "clean_text"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_daily_trend_fills_gap_days_and_computes_net():
    df = make([
        ("2026-10-01", "Positive", 5, "good"),
        ("2026-10-01", "Negative", 1, "bad"),
        ("2026-10-01", "Positive", 5, "good"),
        ("2026-10-03", "Negative", 1, "bad"),
    ])
    t = daily_trend(df)
    assert list(t["mentions"]) == [3, 0, 1]          # 2 Oct present, empty
    assert round(t.loc[0, "net_sentiment"], 1) == 33.3
    assert pd.isna(t.loc[1, "net_sentiment"])        # no reviews: no value


def test_period_change_requires_enough_reviews():
    df = make([("2026-10-01", "Positive", 5, "good")] * 5)
    assert period_change(df) is None


def test_period_change_compares_weeks():
    old = [("2026-09-20", "Negative", 1, "bad")] * 40
    new = [("2026-10-02", "Positive", 5, "good")] * 40
    change = period_change(make(old + new))
    assert change["recent_score"] > change["previous_score"]
    assert change["change"] == change["recent_score"] - change["previous_score"]


def test_rating_crosscheck_shares():
    df = make([
        ("2026-10-01", "Positive", 5, "x"),
        ("2026-10-01", "Neutral", 5, "x"),
        ("2026-10-01", "Negative", 1, "x"),
        ("2026-10-01", "Neutral", 2, "x"),
    ])
    c = rating_crosscheck(df)
    assert c["high_positive_share"] == 50.0
    assert c["low_negative_share"] == 50.0
    assert c["table"].loc[5, "Positive"] == 1


def test_top_terms_counts_once_per_review_and_skips_stopwords():
    df = make([
        ("2026-10-01", "Positive", 5, "fast fast fast and the best"),
        ("2026-10-01", "Positive", 5, "fast transfer"),
    ])
    terms = dict(top_terms(df))
    assert terms["fast"] == 2          # once per review, not 4
    assert "the" not in terms and "and" not in terms


def test_summarize_empty_is_safe():
    assert summarize(make([]))["total_mentions"] == 0
