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

from brands import DEFAULT_BRAND, data_paths, get_brand

OUTPUT_FILE = data_paths(DEFAULT_BRAND)[0]

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


def to_records(raw_reviews, app_id, lang, country, brand_name):
    """Convert library output into the standard schema."""
    url = (
        f"https://play.google.com/store/apps/details"
        f"?id={app_id}&hl={lang}&gl={country}"
    )
    return [
        {
            "id": r["reviewId"],
            "brand": brand_name,
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
    brand=DEFAULT_BRAND,
    count=None,
    output_file=None,
    app_id=None,
):
    """Scrape one brand's Google Play reviews into its own raw-data file."""
    cfg = get_brand(brand)
    app_id = app_id or cfg["app_id"]
    count = count or cfg["review_count"]
    output_file = output_file or data_paths(brand)[0]

    raw = fetch_reviews(app_id, count, cfg["lang"], cfg["country"])
    records = to_records(raw, app_id, cfg["lang"], cfg["country"], cfg["name"])
    total = save_records(records, output_file)
    return len(records), total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand", default=DEFAULT_BRAND, help="brand name from brands.py")
    parser.add_argument("--app-id", help="Google Play app id (overrides the brand's)")
    parser.add_argument("--count", type=int, help="reviews to fetch")
    parser.add_argument("--out", help="output CSV (default: the brand's data folder)")
    args = parser.parse_args()

    fetched, total = scrape_and_save(args.brand, args.count, args.out, args.app_id)
    print(f"Fetched {fetched} reviews; {total} stored in "
          f"{args.out or data_paths(args.brand)[0]}")
