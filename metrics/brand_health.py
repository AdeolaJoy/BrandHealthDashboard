import pandas as pd


def calculate_brand_health(input_file="data/analyzed_reviews.csv"):
    # Load analyzed sentiment data
    data = pd.read_csv(input_file)

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
