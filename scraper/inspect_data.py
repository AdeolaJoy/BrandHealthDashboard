"""
Raw-data inspection report (pipeline step 4 -> 5 checkpoint).

Prints size, missing values, date range, rating spread and text-length
statistics so the dataset can be checked before cleaning and analysis.
"""

import sys

import pandas as pd

INPUT_FILE = "data/scraped_reviews.csv"


def inspect(input_file=INPUT_FILE):
    data = pd.read_csv(input_file)
    text = data["text"].fillna("").astype(str)
    dates = pd.to_datetime(data["date"], errors="coerce")

    report = {
        "rows": len(data),
        "unique_ids": data["id"].nunique(),
        "missing_by_column": data.isna().sum().to_dict(),
        "empty_text": int((text.str.strip() == "").sum()),
        "unparseable_dates": int(dates.isna().sum()),
        "date_min": str(dates.min().date()),
        "date_max": str(dates.max().date()),
        "reviews_per_source": data["source"].value_counts().to_dict(),
        "rating_counts": data["rating"].value_counts().sort_index().to_dict(),
        "text_length": text.str.len().describe().round(1).to_dict(),
        "very_short_text(<=3 chars)": int((text.str.strip().str.len() <= 3).sum()),
        "repeated_text(not removed)": int(
            text.str.lower().str.strip().duplicated().sum()
        ),
        "contains_non_ascii(emoji/accents)": int(
            text.str.contains(r"[^\x00-\x7f]").sum()
        ),
    }
    return report


if __name__ == "__main__":
    # Windows consoles may not print emoji; never crash on output
    sys.stdout.reconfigure(errors="replace")
    path = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    print(f"RAW DATA REPORT: {path}\n" + "=" * 50)
    for key, value in inspect(path).items():
        print(f"{key}: {value}")
