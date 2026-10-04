import os
from datetime import datetime

import pandas as pd
import streamlit as st

from brands import BRANDS, DEFAULT_BRAND, INDUSTRIES, data_paths
from metrics.brand_health import (
    daily_trend,
    load_analyzed,
    period_change,
    rating_crosscheck,
    summarize,
    top_terms,
)
from scraper.play_store_scraper import scrape_and_save
from sentiment.sentiment_analyzer import analyze_file
from ui import components as ui
from ui.styles import CSS

PAGE = 20

st.set_page_config(
    page_title="Brand Health",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.html(f"<style>{CSS}</style>")


# -----------------------------
# Data
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data(path, modified):
    """Cached per file version, so a refresh is picked up immediately."""
    return load_analyzed(path)


def refresh_data(brand):
    """Scrape, then analyse, one brand. Returns an error message or None."""
    try:
        scrape_and_save(brand)
        analyze_file(brand=brand)
    except Exception as error:  # network, parsing or file problems
        return f"{type(error).__name__}: {error}"
    return None


FILTER_KEYS = ("f_ratings", "f_sentiments", "f_search", "f_sort", "shown")


def reset_filters():
    for key in FILTER_KEYS:
        st.session_state.pop(key, None)
    st.session_state["date_reset"] = st.session_state.get("date_reset", 0) + 1


def pick_industry():
    """Industry changed: jump to its first brand and clear the old filters."""
    st.session_state["brand"] = INDUSTRIES[st.session_state["industry"]][0]["name"]
    reset_filters()


# -----------------------------
# Header, brand picker + refresh
# -----------------------------
if st.session_state.get("brand") not in BRANDS:
    wanted = st.query_params.get("brand", DEFAULT_BRAND)
    st.session_state["brand"] = wanted if wanted in BRANDS else DEFAULT_BRAND
if st.session_state.get("industry") not in INDUSTRIES:
    st.session_state["industry"] = BRANDS[st.session_state["brand"]]["industry"]

left, c_ind, c_brand, right = st.columns(
    [3.2, 1.7, 1.7, 1.1], vertical_alignment="bottom"
)
with c_ind:
    st.selectbox("Industry", list(INDUSTRIES), key="industry", on_change=pick_industry)
with c_brand:
    BRAND = st.selectbox(
        "Brand", [b["name"] for b in INDUSTRIES[st.session_state["industry"]]],
        key="brand", on_change=reset_filters,
    )
st.query_params["brand"] = BRAND
brand_info = BRANDS[BRAND]

raw_file, DATA_FILE = data_paths(BRAND)
exists = os.path.exists(DATA_FILE)
modified = os.path.getmtime(DATA_FILE) if exists else 0
data = load_data(DATA_FILE, modified) if exists else pd.DataFrame()

with left:
    if exists and not data.empty:
        source = data["source"].mode().iloc[0] if "source" in data else "Reviews"
        stamp = datetime.fromtimestamp(modified)
        st.html(ui.header(
            BRAND, source,
            f"Updated {stamp.day} {stamp:%b %Y, %H:%M}"
        ))
    else:
        st.html(ui.header(BRAND, "No data yet", "Not collected"))
with right:
    refresh = st.button(
        "Refresh data",
        type="primary",
        use_container_width=True,
        help=f"Collect the newest public reviews of {BRAND} and re-run the analysis.",
    )

if brand_info["note"]:
    st.caption(brand_info["note"])

if refresh:
    with st.status(f"Collecting {BRAND} reviews and running the analysis…") as status:
        error = refresh_data(BRAND)
        if error:
            status.update(label="Could not refresh. Showing the last saved data.",
                          state="error")
            st.error(error)
        else:
            status.update(label="Up to date", state="complete")
            load_data.clear()
            reset_filters()  # new reviews: show the full, updated date range
            st.rerun()

if data.empty:
    st.html(ui.empty_state(
        "No reviews analysed yet",
        "Choose Refresh data to collect the newest public reviews of "
        f"{BRAND} and run the sentiment analysis. It takes about fifteen seconds.",
    ))
    st.stop()


# -----------------------------
# Filters
# -----------------------------
first_day, last_day = data["date"].min().date(), data["date"].max().date()

c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.6, 1.4], vertical_alignment="top")
with c1:
    # The key includes the brand, the data's date range and a reset counter,
    # so a new brand, newer reviews or "Reset filters" start from the full range
    # instead of a range remembered from earlier.
    picked = st.date_input(
        "Dates", value=(first_day, last_day), min_value=first_day,
        max_value=last_day, format="DD/MM/YYYY",
        key=f"f_dates_{BRAND}_{first_day}_{last_day}_{st.session_state.get('date_reset', 0)}",
    )
with c2:
    ratings = st.pills(
        "Star rating (none selected = all)", [1, 2, 3, 4, 5],
        selection_mode="multi", key="f_ratings",
    )
with c3:
    sentiments = st.pills(
        "Sentiment (none selected = all)", ["Positive", "Neutral", "Negative"],
        selection_mode="multi", key="f_sentiments",
    )
with c4:
    query = st.text_input(
        "Search", placeholder="Search review text", key="f_search",
    ).strip()

start, end = (picked if isinstance(picked, tuple) and len(picked) == 2
              else (first_day, last_day))

view = data[
    (data["date"].dt.date >= start) & (data["date"].dt.date <= end)
]
if ratings:
    view = view[view["rating"].isin(ratings)]
if sentiments:
    view = view[view["sentiment"].isin(sentiments)]
if query:
    view = view[view["text"].str.contains(query, case=False, na=False, regex=False)]

filtered = len(view) != len(data)

if view.empty:
    st.html(ui.empty_state(
        "No reviews match these filters",
        "Widen the date range, include more ratings or sentiments, or clear the search.",
    ))
    st.button("Reset filters", on_click=reset_filters)
    st.stop()


# -----------------------------
# Overview
# -----------------------------
summary = summarize(view)
trend = daily_trend(view)
change = period_change(view)
v_start, v_end = view["date"].min(), view["date"].max()

st.html(
    '<div class="bh-section" style="padding-top:28px">'
    + ui.headline(summary, v_start, v_end, len(data) if filtered else None)
    + ui.stat_strip(summary, change)
    + ui.mix_bar(summary)
    + "</div>"
)
if filtered:
    st.button("Reset filters", on_click=reset_filters, type="secondary")


# -----------------------------
# Trend
# -----------------------------
st.html(ui.section(
    "Sentiment over time",
    "Net sentiment per day: positive reviews minus negative reviews, as a "
    "share of all reviews that day. Above zero means positive reviews "
    "outnumber negative ones. Days with fewer than "
    f"{ui.MIN_DAY_MENTIONS} reviews are left off the line.",
    ui.trend_chart(trend),
))


# -----------------------------
# Rating cross-check + words
# -----------------------------
check = rating_crosscheck(view)
praise = top_terms(view[view["rating"] >= 4], n=6)
complaints = top_terms(view[view["rating"] <= 2], n=6)

left_html = (
    "<div><h2>Do the rules agree with star ratings?</h2>"
    '<p class="bh-lede">Each bar splits the reviews at one star rating by the '
    "sentiment the rules gave them. The star rating is written by the "
    "customer, so it is an independent check.</p>"
    + (ui.rating_rows(check) + ui.rating_note(check) if check else "")
    + "</div>"
)
right_html = (
    "<div><h2>What reviewers mention</h2>"
    '<p class="bh-lede">The most common words, counted once per review. '
    "Grouped by star rating, not by the sentiment rules.</p>"
    + ui.term_list("In 4–5 star reviews", praise)
    + '<div style="height:18px"></div>'
    + ui.term_list("In 1–2 star reviews", complaints)
    + "</div>"
)
st.html(
    '<section class="bh-section"><div class="bh-two">'
    + left_html + right_html + "</div></section>"
)


# -----------------------------
# Reviews
# -----------------------------
st.html(ui.section(
    "Reviews",
    f"{len(view):,} review{'s' if len(view) != 1 else ''} match the current "
    "filters. Read the real text behind the numbers.",
    "",
))

SORTS = {
    "Newest": ("date", False),
    "Lowest rating": ("rating", True),
    "Highest rating": ("rating", False),
    "Most negative": ("score", True),
    "Most positive": ("score", False),
}
order = st.segmented_control(
    "Sort by", list(SORTS), default="Newest", key="f_sort",
) or "Newest"
column, ascending = SORTS[order]
ordered = view.sort_values([column, "date"], ascending=[ascending, False])

shown = min(st.session_state.get("shown", PAGE), len(ordered))
st.html(ui.review_list(ordered.head(shown)))

more, _ = st.columns([1, 3])
with more:
    if shown < len(ordered):
        if st.button(f"Show {min(PAGE, len(ordered) - shown)} more",
                     type="secondary", use_container_width=True):
            st.session_state["shown"] = shown + PAGE
            st.rerun()

with st.expander("Data table and export"):
    table = ordered[["date", "rating", "sentiment", "score", "text"]]
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "date": st.column_config.DateColumn("Date", format="D MMM YYYY"),
            "rating": st.column_config.NumberColumn("Stars", format="%d"),
            "sentiment": "Sentiment",
            "score": st.column_config.NumberColumn("Rule score", format="%d"),
            "text": st.column_config.TextColumn("Review", width="large"),
        },
    )
    st.download_button(
        "Download filtered reviews (CSV)",
        table.to_csv(index=False).encode("utf-8"),
        file_name=f"{BRAND.lower()}_reviews_filtered.csv",
        mime="text/csv",
    )

st.html(ui.method_note(
    data["source"].mode().iloc[0] if "source" in data else "review",
    v_start, v_end, len(view),
))
