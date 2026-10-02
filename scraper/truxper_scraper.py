import requests
from bs4 import BeautifulSoup
import pandas as pd


# -----------------------------------
# Truxper business
# -----------------------------------

url = "https://www.truxper.com/businesses/opay"


def scrape_reviews(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    review_elements = soup.select(
        ".item-review-text"
    )

    results = []

    for review_element in review_elements:

        review_box = review_element.find_parent(
            class_="box"
        )

        if not review_box:
            continue

        # -----------------------------------
        # Review text
        # -----------------------------------

        text = review_element.get_text(
            " ",
            strip=True
        )

        # -----------------------------------
        # Review title
        # -----------------------------------

        title_element = review_box.select_one(
            ".item-review-title"
        )

        title = ""

        if title_element:
            title = title_element.get_text(
                " ",
                strip=True
            )

        # -----------------------------------
        # Rating
        # -----------------------------------

        rating_image = review_box.select_one(
            ".ratings img"
        )

        rating = ""

        if rating_image:
            rating = rating_image.get("alt", "")

        # -----------------------------------
        # Date
        # -----------------------------------

        date_element = review_box.select_one(
            ".item-review-body h6 span"
        )

        date = ""

        if date_element:
            date = date_element.get_text(
                " ",
                strip=True
            )

        # -----------------------------------
        # Reviewer
        # -----------------------------------

        reviewer_element = review_box.select_one(
            ".user-info .fw-medium"
        )

        reviewer = ""

        if reviewer_element:
            reviewer = reviewer_element.get_text(
                " ",
                strip=True
            )

        # -----------------------------------
        # Review URL
        # -----------------------------------

        review_link = review_box.select_one(
            ".item-review-header a.text-muted"
        )

        review_url = ""

        if review_link:
            review_url = review_link.get(
                "href",
                ""
            )

        # -----------------------------------
        # Save review
        # -----------------------------------

        results.append({
            "brand": "OPay",
            "text": text,
            "title": title,
            "rating": rating,
            "date": date,
            "reviewer": reviewer,
            "source": "Truxper",
            "source_type": "Customer Review",
            "url": review_url
        })

    return results


def scrape_and_save(
    output_file="data/scraped_reviews.csv"
):
    results = scrape_reviews(url)

    data = pd.DataFrame(results)

    if not data.empty:
        data.insert(
            0,
            "id",
            range(1, len(data) + 1)
        )

    data.to_csv(
        output_file,
        index=False
    )

    return data


if __name__ == "__main__":

    data = scrape_and_save()

    print("\n" + "=" * 60)
    print("TRUXPER OPay REVIEW SCRAPER")
    print("=" * 60)

    if not data.empty:

        print(
            data[
                [
                    "id",
                    "brand",
                    "text",
                    "rating",
                    "date"
                ]
            ].to_string(index=False)
        )

    else:

        print("No reviews were scraped.")

    print("\n" + "=" * 60)
    print(
        f"Scraped {len(data)} reviews."
    )
    print(
        "Saved to: data/scraped_reviews.csv"
    )
    print("=" * 60)