# -----------------------------------
# Brand registry
# -----------------------------------
#
# Every brand the dashboard can show, grouped by industry. All brands share
# the same pipeline (scrape -> clean -> rule-based sentiment -> metrics) and
# the same sentiment vocabulary (brand_config.py); only the Google Play app
# and the brand keywords differ. Each brand keeps its own files under
# data/<slug>/, so switching brands never mixes or overwrites data.
#
# To add a brand: find its Google Play app id (the `id=` part of the store
# URL), add one entry below, then use Refresh data in the dashboard.

import re

DEFAULT_REVIEW_COUNT = 5000


def _brand(name, app_id, keywords, country="ng", note=None, count=None):
    return {
        "name": name,
        "app_id": app_id,
        "country": country,
        "lang": "en",
        "review_count": count or DEFAULT_REVIEW_COUNT,
        "keywords": keywords,
        "note": note,
    }


INDUSTRIES = {
    "Fintech": [
        _brand("OPay", "team.opay.pay", ["opay", "o-pay", "opay app", "opay wallet", "opay pos"]),
        _brand("PalmPay", "com.transsnet.palmpay", ["palmpay", "palm pay"]),
        _brand("Kuda", "com.kudabank.app", ["kuda", "kuda bank", "kuda app"]),
    ],
    "Food & Restaurants": [
        _brand("KFC", "com.kfc.ghana", ["kfc", "kentucky"], country="gh",
               note="KFC has no Nigerian app on Google Play, so this uses the "
                    "KFC Ghana app (West Africa)."),
        _brand("Chicken Republic", "com.republic.dash.app",
               ["chicken republic", "chickenrepublic", "republic dash"],
               note="Chicken Republic's own app has no reviews on Google Play, "
                    "so this uses Republic Dash, its ordering and delivery app."),
        _brand("Domino's", "com.dominos.ng", ["domino", "dominos", "domino's"]),
    ],
    "Telecommunications": [
        _brand("MTN", "ng.mtn.nextgen", ["mtn", "mymtn", "mtn app"]),
        _brand("Airtel", "com.airtel.africa.selfcare", ["airtel", "myairtel"]),
        _brand("Glo", "net.one97.selfcare.globacom", ["glo", "globacom", "glo cafe"]),
    ],
    "E-commerce": [
        _brand("Jumia", "com.jumia.android", ["jumia"]),
        _brand("Konga", "com.konga.androida", ["konga"]),
    ],
    "Ride-hailing": [
        _brand("Bolt", "ee.mtakso.client", ["bolt"]),
        _brand("Uber", "com.ubercab", ["uber"]),
    ],
    "Airlines": [
        _brand("Air Peace", "com.flyairpeace.app.airpeace", ["air peace", "airpeace"]),
        _brand("Ibom Air", "com.hititcs.ibomair", ["ibom air", "ibomair"]),
    ],
}

BRANDS = {b["name"]: dict(b, industry=ind)
          for ind, brands in INDUSTRIES.items() for b in brands}

DEFAULT_BRAND = "OPay"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def data_paths(name):
    """(raw_file, analyzed_file) for one brand."""
    folder = f"data/{slug(name)}"
    return f"{folder}/scraped_reviews.csv", f"{folder}/analyzed_reviews.csv"


def get_brand(name):
    return BRANDS[name]
