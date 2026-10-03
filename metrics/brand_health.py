import re

import pandas as pd


def load_analyzed(input_file="data/analyzed_reviews.csv"):
    """Load analyzed reviews, keeping only brand-relevant mentions."""
    data = pd.read_csv(input_file, dtype={"id": str}, parse_dates=["date"])

    if "brand_relevant" in data.columns:
        data = data[data["brand_relevant"].astype(str) == "True"]

    return data.reset_index(drop=True)


def calculate_brand_health(input_file="data/analyzed_reviews.csv"):
    return summarize(load_analyzed(input_file))


def summarize(data):
    """Headline brand-health metrics for a DataFrame of analyzed mentions."""
    # Count total mentions
    total_mentions = len(data)

    # Prevent division by zero
    if total_mentions == 0:
        return {
            "total_mentions": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "positive_percentage": 0,
            "negative_percentage": 0,
            "neutral_percentage": 0,
            "net_sentiment": 0,
            "brand_health_score": 50
        }

    # Count each sentiment
    positive_count = (data["sentiment"] == "Positive").sum()
    negative_count = (data["sentiment"] == "Negative").sum()
    neutral_count = (data["sentiment"] == "Neutral").sum()

    # Calculate percentages
    positive_percentage = (positive_count / total_mentions) * 100
    negative_percentage = (negative_count / total_mentions) * 100
    neutral_percentage = (neutral_count / total_mentions) * 100

    # Calculate net sentiment
    net_sentiment = positive_percentage - negative_percentage

    # Calculate Brand Health Score
    brand_health_score = 50 + (net_sentiment / 2)

    # Keep score within 0–100
    brand_health_score = max(0, min(100, brand_health_score))

    # Return all results
    return {
        "total_mentions": total_mentions,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "positive_percentage": positive_percentage,
        "negative_percentage": negative_percentage,
        "neutral_percentage": neutral_percentage,
        "net_sentiment": net_sentiment,
        "brand_health_score": brand_health_score
    }



# -----------------------------
# Trend and breakdown metrics (dashboard views; formulas above unchanged)
# -----------------------------

def daily_trend(data):
    """Per-day volume, sentiment counts, net sentiment and score."""
    if data.empty:
        return pd.DataFrame(
            columns=["date", "mentions", "positive", "negative",
                     "neutral", "net_sentiment", "score"]
        )

    day = data["date"].dt.normalize()
    counts = (
        pd.crosstab(day, data["sentiment"])
        .reindex(columns=["Positive", "Negative", "Neutral"], fill_value=0)
    )
    # Include days with no reviews so the time axis has no hidden gaps
    counts = counts.reindex(
        pd.date_range(counts.index.min(), counts.index.max()), fill_value=0
    )

    out = pd.DataFrame({
        "date": counts.index,
        "mentions": counts.sum(axis=1).values,
        "positive": counts["Positive"].values,
        "negative": counts["Negative"].values,
        "neutral": counts["Neutral"].values,
    })
    has_data = out["mentions"] > 0
    out["net_sentiment"] = float("nan")
    out.loc[has_data, "net_sentiment"] = (
        (out["positive"] - out["negative"]) / out["mentions"] * 100
    )[has_data]
    out["score"] = (50 + out["net_sentiment"] / 2).clip(0, 100)
    return out


def period_change(data, days=7, min_mentions=30):
    """
    Score of the latest `days` days vs the `days` before them.

    Returns None when either period has fewer than `min_mentions` reviews,
    because a change computed from a handful of reviews is noise.
    """
    if data.empty:
        return None

    end = data["date"].max().normalize()
    recent_start = end - pd.Timedelta(days=days - 1)
    previous_start = recent_start - pd.Timedelta(days=days)

    recent = data[data["date"] >= recent_start]
    previous = data[
        (data["date"] >= previous_start) & (data["date"] < recent_start)
    ]
    if len(recent) < min_mentions or len(previous) < min_mentions:
        return None

    recent_score = summarize(recent)["brand_health_score"]
    previous_score = summarize(previous)["brand_health_score"]
    return {
        "days": days,
        "recent_score": float(recent_score),
        "previous_score": float(previous_score),
        "change": float(recent_score - previous_score),
    }


def rating_crosscheck(data):
    """
    Compare rule-based sentiment with the star rating.

    Returns the sentiment mix for each star rating, plus the share of
    4-5 star reviews classed Positive and of 1-2 star reviews classed
    Negative. Star ratings are an independent signal, so this is a
    simple, honest check on the word rules.
    """
    if data.empty or "rating" not in data.columns:
        return None

    table = (
        pd.crosstab(data["rating"], data["sentiment"])
        .reindex(index=[1, 2, 3, 4, 5], columns=["Positive", "Neutral", "Negative"],
                 fill_value=0)
    )

    high = data[data["rating"] >= 4]
    low = data[data["rating"] <= 2]
    return {
        "table": table,
        "high_rated": len(high),
        "high_positive_share": (
            float((high["sentiment"] == "Positive").mean() * 100) if len(high) else None
        ),
        "low_rated": len(low),
        "low_negative_share": (
            float((low["sentiment"] == "Negative").mean() * 100) if len(low) else None
        ),
    }


STOPWORDS = set("""
a about after all also am an and any app are as at be because been but by can
could did do does don dont for from get got had has have he her him his i if in
into is it its ive just me more most my no not now of on one only or other our
out over so some than that the their them then there these they this to too up
us very was we were what when which who why will with would you your youre
opay o pay money it's don't can't i'm didn't doesn't won't isn't should like
""".split())


def top_terms(data, n=8, min_length=3):
    """Most frequent meaningful words across the cleaned review text."""
    if data.empty or "clean_text" not in data.columns:
        return []

    counts = {}
    for text in data["clean_text"].dropna():
        # Count each word once per review so one long review cannot dominate
        for word in set(re.findall(r"[a-z']+", text)):
            word = word.strip("'")
            if len(word) >= min_length and word not in STOPWORDS:
                counts[word] = counts.get(word, 0) + 1

    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:n]


# Run directly if this file is executed
if __name__ == "__main__":
    results = calculate_brand_health()

    print("\n" + "=" * 50)
    print("           BRAND HEALTH ANALYSIS")
    print("=" * 50)

    print(f"Total Mentions:        {results['total_mentions']}")
    print(f"Positive Mentions:     {results['positive_count']}")
    print(f"Negative Mentions:     {results['negative_count']}")
    print(f"Neutral Mentions:      {results['neutral_count']}")

    print("\nSENTIMENT DISTRIBUTION")
    print("-" * 50)

    print(f"Positive:              {results['positive_percentage']:.2f}%")
    print(f"Negative:              {results['negative_percentage']:.2f}%")
    print(f"Neutral:               {results['neutral_percentage']:.2f}%")

    print("\nBRAND HEALTH")
    print("-" * 50)

    print(f"Net Sentiment:         {results['net_sentiment']:.2f}%")
    print(f"Brand Health Score:    {results['brand_health_score']:.2f}/100")

    print("=" * 50)
