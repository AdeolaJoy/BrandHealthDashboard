import requests
from bs4 import BeautifulSoup


url = "https://play.google.com/store/apps/details?gl=NG&hl=en&id=team.opay.pay"

headers = {
    "User-Agent": "Mozilla/5.0"
}


response = requests.get(
    url,
    headers=headers,
    timeout=15
)

response.raise_for_status()


soup = BeautifulSoup(
    response.text,
    "html.parser"
)


element = soup.select_one(
    "[data-review-id]"
)


print("status code:", response.status_code)


if element:

    review_id = element.get(
        "data-review-id",
        ""
    )

    print("\nreview ID:")
    print(review_id)

    print("\nPARENT HIERARCHY:")
    print("=" * 70)

    current = element

    for level in range(1, 9):

        current = current.parent

        if not current:
            break

        print(
            f"\nLEVEL {level}"
        )

        print(
            "tag:",
            current.name
        )

        print(
            "classes:",
            current.get("class")
        )

        text = current.get_text(
            " ",
            strip=True
        )

        print(
            "text length:",
            len(text)
        )

        print(
            "text preview:"
        )

        print(
            text[:500]
        )

else:

    print(
        "No data-review-id element found."
    )