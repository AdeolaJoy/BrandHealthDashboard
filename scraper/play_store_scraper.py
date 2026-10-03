"""
Google Play review scraper (production data source).

Collects public user reviews of the case-study brand's app and saves them
to data/scraped_reviews.csv using the project's standard raw-data schema.
Re-running merges new reviews into the existing file (no duplicates).
"""

import argparse
import os

import pandas as pd
from google_play_scraper import Sort, reviews

from brand_config import brand_config

OUTPUT_FILE = "data/scraped_reviews.csv"

# Standard raw-data schema shared by every scraper
COLUMNS = [
    "id", "brand", "text", "rating", "date",
    "source", "source_type", "url",
]


def fetch_reviews(app_id, count, lang, country):
    """Download up to `count` newest reviews from Google Play."""
    results, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=count,
    )
    return results


def to_records(raw_reviews, app_id, lang, country):
    """Convert library output into the standard schema."""
    url = (
        f"https://play.google.com/store/apps/details"
        f"?id={app_id}&hl={lang}&gl={country}"
    )
    return [
        {
            "id": r["reviewId"],
            "brand": brand_config["brand_name"],
            "text": r["content"],
            "rating": r["score"],
            "date": r["at"].strftime("%Y-%m-%d"),
            "source": "Google Play",
            "source_type": "Customer Review",
            "url": url,
        }
        for r in raw_reviews
    ]


def save_records(records, output_file=OUTPUT_FILE):
    """Merge new records into the CSV, keeping one row per review id."""
    new = pd.DataFrame(records, columns=COLUMNS)

    if os.path.exists(output_file):
        old = pd.read_csv(output_file, dtype={"id": str})
        # Older files (e.g. a different source) may have other columns
        old = old.reindex(columns=COLUMNS)
        new = pd.concat([old, new], ignore_index=True)

    new = new.drop_duplicates(subset="id", keep="last")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    new.to_csv(output_file, index=False)
    return len(new)


def scrape_and_save(
    app_id=None,
    count=None,
    output_file=OUTPUT_FILE,
):
    cfg = brand_config["play_store"]
    app_id = app_id or cfg["app_id"]
    count = count or cfg["review_count"]

    raw = fetch_reviews(app_id, count, cfg["lang"], cfg["country"])
    records = to_records(raw, app_id, cfg["lang"], cfg["country"])
    total = save_records(records, output_file)
    return len(records), total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", help="Google Play app id")
    parser.add_argument("--count", type=int, help="reviews to fetch")
    parser.add_argument("--out", default=OUTPUT_FILE)
    args = parser.parse_args()

    fetched, total = scrape_and_save(args.app_id, args.count, args.out)
    print(f"Fetched {fetched} reviews; {total} stored in {args.out}")
