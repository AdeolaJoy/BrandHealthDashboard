import requests
from bs4 import BeautifulSoup

url = "https://www.truxper.com/businesses/opay"

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

print("status code:", response.status_code)

print("\nreview count:")
print(
    len(
        soup.select(".item-review-text")
    )
)

print("\npossible pagination links:")

links = soup.find_all("a")

for link in links:

    text = link.get_text(
        " ",
        strip=True
    )

    href = link.get(
        "href",
        ""
    )

    if (
        "page" in href.lower()
        or "next" in text.lower()
        or "previous" in text.lower()
        or "load" in text.lower()
        or "more" in text.lower()
    ):

        print(
            f"text={text!r} | href={href!r}"
        )

print("\nall links near the reviews:")

review = soup.select_one(
    ".item-review-text"
)

if review:

    review_box = review.find_parent(
        class_="box"
    )

    if review_box:

        parent = review_box.parent

        for link in parent.find_all("a"):

            text = link.get_text(
                " ",
                strip=True
            )

            href = link.get(
                "href",
                ""
            )

            if text or href:

                print(
                    f"text={text!r} | href={href!r}"
                )