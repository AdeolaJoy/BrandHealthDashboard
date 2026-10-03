import re
import pandas as pd

from brand_config import brand_config
from sentiment.cleaning import clean_dataframe





# -----------------------------
# Sentiment vocabulary
# -----------------------------

# word -> weight (+1/-1 normal, +2/-2 strong). Strong lists win on overlap.
WORD_WEIGHTS = {}
for _word in brand_config["positive_words"]:
    WORD_WEIGHTS[_word] = 1
for _word in brand_config["negative_words"]:
    WORD_WEIGHTS[_word] = -1
for _word in brand_config["strong_positive_words"]:
    WORD_WEIGHTS[_word] = 2
for _word in brand_config["strong_negative_words"]:
    WORD_WEIGHTS[_word] = -2

# phrase -> weight (+2/-2). Longest phrases are tried first.
PHRASE_WEIGHTS = {phrase: 2 for phrase in brand_config["positive_phrases"]}
PHRASE_WEIGHTS.update({phrase: -2 for phrase in brand_config["negative_phrases"]})
PHRASE_RE = re.compile(
    r"(?<![a-z0-9])(?:"
    + "|".join(re.escape(p) for p in sorted(PHRASE_WEIGHTS, key=len, reverse=True))
    + r")(?![a-z0-9])"
)

NEGATION_WORDS = set(brand_config["negation_words"])
INTENSIFIERS = set(brand_config["intensifiers"])

NEGATION_WINDOW = 3     # a negation within 3 words before flips a word
INTENSIFIER_WINDOW = 2  # an intensifier within 2 words before doubles it

# -----------------------------
# Brand Relevance Check
# -----------------------------

def is_brand_relevant(text, source=None):
    """
    Check whether a mention is relevant to the selected brand.

    A mention is relevant when it names a brand keyword, OR when it comes
    from a brand-specific source (e.g. the brand's own Google Play page),
    where every review is about the brand even if the name is not repeated.
    """

    if source in brand_config.get("brand_specific_sources", []):
        return True

    text = str(text).lower()

    for keyword in brand_config["brand_keywords"]:
        if keyword.lower() in text:
            return True

    return False


def normalise(text):
    """Lowercase; drop apostrophes ("can't" -> "cant"); keep letters/digits."""
    text = str(text).lower().replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def analyze_sentiment(text):
    """
    Rule-based sentiment of one review. Returns (label, score).

    1. Multi-word phrases ("not working", "no wahala") are scored first
       at +/-2 and removed, so their words are not counted again.
    2. Each remaining word found in the vocabulary scores its weight
       (+/-1, or +/-2 for strong words).
    3. A negation word ("not", "cant", "never"...) in the 3 words before
       flips the sign; an intensifier ("very", "so"...) in the 2 words
       before doubles the strength.
    4. A positive total is Positive, a negative total is Negative and
       zero is Neutral.
    """

    text = normalise(text)
    score = 0

    # Step 1: phrases
    def take_phrase(match):
        nonlocal score
        score += PHRASE_WEIGHTS[match.group(0)]
        return " _ "

    text = PHRASE_RE.sub(take_phrase, text)

    # Words repeated back-to-back ("angry angry angry") count once
    tokens = []
    for word in text.split():
        if not tokens or tokens[-1] != word:
            tokens.append(word)

    # Steps 2 and 3: single words with negation and intensifier handling
    for i, word in enumerate(tokens):
        weight = WORD_WEIGHTS.get(word)
        if weight is None:
            continue

        if any(t in INTENSIFIERS for t in tokens[max(0, i - INTENSIFIER_WINDOW):i]):
            weight *= 2

        if any(t in NEGATION_WORDS for t in tokens[max(0, i - NEGATION_WINDOW):i]):
            weight = -weight

        score += weight

    # Step 4: classify
    if score > 0:
        return "Positive", score
    if score < 0:
        return "Negative", score
    return "Neutral", score


def analyze_file(
    input_file="data/scraped_reviews.csv",
    output_file="data/analyzed_reviews.csv"
):
    """
    Load scraped data, clean it, check brand relevance,
    perform sentiment analysis, and save results.
    """

    data = pd.read_csv(input_file, dtype={"id": str})

    if "text" not in data.columns:
        raise ValueError(
            "Input CSV must contain a 'text' column."
        )

    # Step 5: cleaning / preprocessing
    data, stats = clean_dataframe(data)

    # Step 6: brand relevance
    source = data["source"] if "source" in data.columns else None
    data["brand_relevant"] = [
        is_brand_relevant(text, src)
        for text, src in zip(
            data["text"],
            source if source is not None else [None] * len(data)
        )
    ]

    # Step 7: rule-based sentiment on the cleaned text
    results = data["clean_text"].apply(analyze_sentiment)

    data["sentiment"] = results.apply(lambda result: result[0])
    data["score"] = results.apply(lambda result: result[1])

    data.to_csv(output_file, index=False)

    return data


# -----------------------------
# Run directly for testing
# -----------------------------
if __name__ == "__main__":

    data = analyze_file()

    print("Analysis complete!")
    print(f"Rows analysed:      {len(data)}")
    print(f"Brand relevant:     {int(data['brand_relevant'].sum())}")
    print(data["sentiment"].value_counts().to_string())
    print("Results saved to: data/analyzed_reviews.csv")
