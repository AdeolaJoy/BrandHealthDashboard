import re
import pandas as pd

from brand_config import brand_config





# -----------------------------
# Sentiment vocabulary
# -----------------------------

positive_words = set(
    brand_config["positive_words"]
)

negative_words = set(
    brand_config["negative_words"]
)

# -----------------------------
# Brand Relevance Check
# -----------------------------

def is_brand_relevant(text):
    """
    Check whether a piece of text is relevant
    to the selected brand.
    """

    text = str(text).lower()

    brand_keywords = brand_config["brand_keywords"]

    for keyword in brand_keywords:
        if keyword.lower() in text:
            return True

    return False


def analyze_sentiment(text):
    """
    Analyze text using a rule-based sentiment approach
    with negation and intensifier handling.
    """

    # Convert text to lowercase
    text = str(text).lower()

    # Extract words
    words = re.findall(r"\b\w+\b", text)

    # Negation words
    negation_words = {
        "not",
        "no",
        "never",
        "neither",
        "hardly"
    }

    # Intensifier words
    intensifiers = {
        "very",
        "extremely",
        "really",
        "highly",
        "absolutely",
        "incredibly"
    }

    positive_score = 0
    negative_score = 0

    for i, word in enumerate(words):

        # Check whether the current word is positive
        if word in positive_words:

            # Check previous word for negation
            if i > 0 and words[i - 1] in negation_words:
                negative_score += 1

            # Check previous word for intensifier
            elif i > 0 and words[i - 1] in intensifiers:
                positive_score += 2

            else:
                positive_score += 1

        # Check whether the current word is negative
        elif word in negative_words:

            # Check previous word for negation
            if i > 0 and words[i - 1] in negation_words:
                positive_score += 1

            # Check previous word for intensifier
            elif i > 0 and words[i - 1] in intensifiers:
                negative_score += 2

            else:
                negative_score += 1

    # Calculate overall score
    sentiment_score = positive_score - negative_score

    # Classify sentiment
    if sentiment_score > 0:
        sentiment = "Positive"

    elif sentiment_score < 0:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    return sentiment, sentiment_score
def analyze_file(
    input_file="data/scraped_reviews.csv",
    output_file="data/analyzed_reviews.csv"
):
    """
    Load scraped data, check brand relevance,
    perform sentiment analysis, and save results.
    """

    data = pd.read_csv(input_file)

    if "text" not in data.columns:
        raise ValueError(
            "Input CSV must contain a 'text' column."
        )

    # Check whether each mention is relevant to the brand
    data["brand_relevant"] = data["text"].apply(
        is_brand_relevant
    )

    # Perform sentiment analysis
    results = data["text"].apply(
        analyze_sentiment
    )

    data["sentiment"] = results.apply(
        lambda result: result[0]
    )

    data["score"] = results.apply(
        lambda result: result[1]
    )

    data.to_csv(
        output_file,
        index=False
    )

    return data
    """
    Load scraped data, perform sentiment analysis,
    and save the analyzed results.
    """

    # Load scraped data
    data = pd.read_csv(input_file)

    # Make sure the text column exists
    if "text" not in data.columns:
        raise ValueError(
            "Input CSV must contain a 'text' column."
        )

    # Apply sentiment analysis
    results = data["text"].apply(analyze_sentiment)

    # Extract sentiment and score
    data["sentiment"] = results.apply(
        lambda result: result[0]
    )

    data["score"] = results.apply(
        lambda result: result[1]
    )

    # Save analyzed results
    data.to_csv(
        output_file,
        index=False
    )

    return data


# -----------------------------
# Run directly for testing
# -----------------------------
if __name__ == "__main__":

    data = analyze_file()

    print("\n" + "=" * 60)
    print("ANALYZED BRAND MENTIONS")
    print("=" * 60)

    print(
        data[
            ["id", "text", "sentiment", "brand_relevant", "score"]
        ]
    )

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print(
        "Results saved to: data/analyzed_reviews.csv"
    )
    print("=" * 60)