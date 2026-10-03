"""
Data cleaning / preprocessing (pipeline step 5).

Raw review text is normalised so the rule-based analyser sees consistent
input. The original text column is left untouched; cleaned text goes in a
new `clean_text` column.
"""

import re

import pandas as pd

# Small, documented emoji lexicon. Emojis carry a lot of sentiment in app
# reviews, and the rule-based analyser only reads words, so each common
# emoji is replaced by an equivalent word from the sentiment vocabulary.
EMOJI_WORDS = {
    "👍": " good ", "👌": " good ", "❤": " love ", "😍": " love ",
    "🥰": " love ", "😊": " happy ", "😀": " happy ", "😃": " happy ",
    "😁": " happy ", "🙏": " thanks ", "🔥": " great ", "💯": " excellent ",
    "👎": " bad ", "😡": " angry ", "😠": " angry ", "🤬": " angry ",
    "😭": " sad ", "😢": " sad ", "😞": " disappointed ", "🤮": " horrible ",
    "💔": " disappointed ",
}

URL_RE = re.compile(r"https?://\S+|www\.\S+")
NON_TEXT_RE = re.compile(r"[^a-z0-9\s']")
REPEAT_RE = re.compile(r"(.)\1{2,}")  # soooo -> soo


def clean_text(text):
    """Return normalised text, or an empty string if nothing usable."""
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = URL_RE.sub(" ", text)

    for emoji, word in EMOJI_WORDS.items():
        text = text.replace(emoji, word)

    text = text.replace("’", "'")
    text = REPEAT_RE.sub(r"\1\1", text)   # "goooood" -> "good"
    text = NON_TEXT_RE.sub(" ", text)     # drop punctuation/other symbols
    return re.sub(r"\s+", " ", text).strip()


def clean_dataframe(data):
    """
    Clean a raw reviews DataFrame.

    Returns (cleaned_data, stats). Rows are dropped only when they have no
    usable text or no valid date. Repeated identical texts ("good", "nice")
    are KEPT: they are separate customers, so removing them would understate
    how common an opinion is. Exact duplicates are removed by review id.
    """
    stats = {"rows_in": len(data)}

    data = data.drop_duplicates(subset="id", keep="last").copy()
    stats["duplicate_ids_removed"] = stats["rows_in"] - len(data)

    data["clean_text"] = data["text"].apply(clean_text)
    data["date"] = pd.to_datetime(data["date"], errors="coerce")

    # Usable = at least 2 letters/digits of text
    usable = data["clean_text"].str.count(r"[a-z0-9]") >= 2
    stats["unusable_text_removed"] = int((~usable).sum())

    valid_date = data["date"].notna()
    stats["invalid_date_removed"] = int((usable & ~valid_date).sum())

    data = data[usable & valid_date].reset_index(drop=True)
    stats["rows_out"] = len(data)
    return data, stats
