"""
HTML builders for the dashboard views.

Each function returns an HTML string for st.html(). Charts are plain
HTML/SVG styled by CSS variables, so they follow the light and dark
themes, stay crisp at any width and need no charting library. Every
piece of user-supplied text goes through html.escape.
"""

from html import escape
from urllib.parse import quote

import pandas as pd

MIN_DAY_MENTIONS = 20      # fewer reviews than this: day is not plotted
STAR_POINTS = (
    "6,0.8 7.7,4.4 11.6,4.9 8.7,7.6 9.5,11.5 "
    "6,9.6 2.5,11.5 3.3,7.6 0.4,4.9 4.3,4.4"
)


# Streamlit's HTML sanitiser removes inline <svg> and data-URI <img>, so graphics are embedded
# as CSS background data URIs. The SVG carries its own light/dark colours through
# prefers-color-scheme, matching the page tokens.
SVG_STYLE = (
    ".grid{stroke:#ECECE7;stroke-width:1;vector-effect:non-scaling-stroke}"
    ".zero{stroke:#656C75;stroke-width:1;stroke-dasharray:3 4;opacity:.6;"
    "vector-effect:non-scaling-stroke}"
    ".line{fill:none;stroke:#121417;stroke-width:2;stroke-linejoin:round;"
    "stroke-linecap:round;vector-effect:non-scaling-stroke}"
    ".ma{fill:none;stroke:#656C75;stroke-width:1.25;stroke-dasharray:2 3;"
    "vector-effect:non-scaling-stroke}"
    ".on{fill:#4A5058}.off{fill:#E2E2DC}"
    "@media (prefers-color-scheme:dark){"
    ".grid{stroke:#1F2226}.zero{stroke:#8D949C}.line{stroke:#F2F3F4}"
    ".ma{stroke:#8D949C}.on{fill:#B4BAC1}.off{fill:#2A2D32}}"
)


def svg_image(inner, view_box, style, alt="", preserve=""):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}"{preserve}>'
        f"<style>{SVG_STYLE}</style>{inner}</svg>"
    )
    uri = "data:image/svg+xml;utf8," + quote(svg, safe="")
    bg = "background:url(\"" + uri + "\") center/100% 100% no-repeat"
    return (
        f'<div role="img" aria-label="{escape(alt)}" '
        f"style='{style};{bg}'></div>"
    )


# -----------------------------
# Formatting helpers
# -----------------------------

def signed(value, digits=0):
    """+12 / −3 with a real minus sign."""
    text = f"{abs(value):.{digits}f}"
    return f"+{text}" if value >= 0 else f"−{text}"


def short_date(ts):
    return f"{ts.day} {ts:%b}"


def long_date(ts):
    return f"{ts:%a} {ts.day} {ts:%b}"


def span_label(start, end):
    if start.year == end.year:
        return f"{short_date(start)} – {short_date(end)} {end.year}"
    return f"{short_date(start)} {start.year} – {short_date(end)} {end.year}"


# -----------------------------
# Header and headline
# -----------------------------

def header(brand, source, updated_text):
    return (
        '<div class="bh-header">'
        f'<span class="bh-brand">{escape(brand)}</span>'
        '<span class="bh-sub">Brand health</span>'
        f'<span class="bh-meta">{escape(source)} · {escape(updated_text)}</span>'
        "</div>"
    )


def headline(summary, start, end, filtered_total=None):
    net = summary["net_sentiment"]
    n = summary["total_mentions"]
    scope = f"{n:,} review{'s' if n != 1 else ''}"
    if filtered_total is not None and filtered_total != n:
        scope += f' <span class="muted">of {filtered_total:,}</span>'
    return (
        f'<h1 class="bh-headline">Net sentiment is {signed(net)} '
        f'across {scope} '
        f'<span class="muted">from {escape(span_label(start, end))}</span></h1>'
    )


def stat_strip(summary, change):
    score = summary["brand_health_score"]
    if change is None:
        score_foot = "Needs 30+ reviews in each of two weeks to compare"
    else:
        delta = change["change"]
        cls = "up" if delta > 0.05 else "down" if delta < -0.05 else ""
        score_foot = (
            f'<span class="{cls}">{signed(delta, 1)}</span> '
            f'vs previous {change["days"]} days'
        )

    def item(label, value, unit, foot):
        return (
            f'<div class="bh-stat"><dt>{label}</dt>'
            f"<dd>{value}<small>{unit}</small></dd>"
            f'<div class="foot">{foot}</div></div>'
        )

    return (
        '<dl class="bh-stats" style="margin:0;padding:0">'
        + item("Brand health score", f"{score:.1f}", "/100", score_foot)
        + item("Net sentiment", signed(summary["net_sentiment"], 1), "pts",
               "Positive % minus negative %")
        + item("Positive", f"{summary['positive_percentage']:.1f}", "%",
               f"{summary['positive_count']:,} reviews")
        + item("Negative", f"{summary['negative_percentage']:.1f}", "%",
               f"{summary['negative_count']:,} reviews")
        + "</dl>"
    )


def mix_bar(summary):
    parts = [
        ("pos", "Positive", summary["positive_percentage"], summary["positive_count"]),
        ("neu", "Neutral", summary["neutral_percentage"], summary["neutral_count"]),
        ("neg", "Negative", summary["negative_percentage"], summary["negative_count"]),
    ]
    bar = "".join(
        f'<i class="c-{k}" style="width:{pct:.2f}%"></i>'
        for k, _, pct, _ in parts if pct > 0
    )
    legend = "".join(
        f'<span><i class="dot c-{k}"></i>{label} <b>{pct:.1f}%</b></span>'
        for k, label, pct, _ in parts
    )
    return (
        f'<div class="bh-mix" role="img" aria-label="Sentiment mix: '
        + ", ".join(f"{label} {pct:.1f}%" for _, label, pct, _ in parts)
        + f'">{bar}</div><div class="bh-legend">{legend}</div>'
    )


# -----------------------------
# Trend chart
# -----------------------------

def _runs(points):
    """Split [(x, y) or None, ...] into runs of consecutive points."""
    run, runs = [], []
    for p in points:
        if p is None:
            if len(run) > 1:
                runs.append(run)
            run = []
        else:
            run.append(p)
    if len(run) > 1:
        runs.append(run)
    return runs


def _path(run):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in run)


def trend_chart(trend, plot_height=200):
    n = len(trend)
    if n < 2:
        return (
            '<p class="bh-lede">Not enough days of data to draw a trend. '
            "Collect more reviews or widen the date range.</p>"
        )

    ok = trend["mentions"] >= MIN_DAY_MENTIONS

    # Trailing 7-day net sentiment, weighted by review volume
    window = trend[["positive", "negative", "mentions"]].rolling(7, min_periods=3).sum()
    avg = ((window["positive"] - window["negative"]) / window["mentions"] * 100)

    values = list(trend.loc[ok, "net_sentiment"]) + list(avg.dropna()) + [0]
    # Keep zero as the floor unless the data really goes negative
    lo = 0 if min(values) >= 0 else (int((min(values) - 5) // 25)) * 25
    hi = (int((max(values) + 5) // 25) + 1) * 25
    step = 25 if hi - lo <= 150 else 50
    span = hi - lo

    def x(i):
        return (i + 0.5) / n * 100

    def y(v):
        return (hi - v) / span * 100

    ticks = list(range(lo, hi + 1, step))
    grid = "".join(
        f'<line class="{"zero" if t == 0 else "grid"}" x1="0" x2="100" '
        f'y1="{y(t):.2f}" y2="{y(t):.2f}"/>'
        for t in ticks
    )
    yaxis = "".join(
        f'<span style="top:{y(t):.2f}%">{signed(t) if t else "0"}</span>'
        for t in ticks
    )

    daily = [
        (x(i), y(v)) if good else None
        for i, (v, good) in enumerate(zip(trend["net_sentiment"], ok))
    ]
    smooth = [
        (x(i), y(v)) if pd.notna(v) else None for i, v in enumerate(avg)
    ]
    daily_paths = "".join(f'<path class="ma" d="{_path(r)}"/>' for r in _runs(daily))
    smooth_paths = "".join(f'<path class="line" d="{_path(r)}"/>' for r in _runs(smooth))

    peak = max(trend["mentions"].max(), 1)
    bars = "".join(
        f'<i style="height:{max(m / peak * 100, 1.5):.1f}%"></i>'
        for m in trend["mentions"]
    )

    hits = []
    for i, row in trend.iterrows():
        edge = " edge-l" if i < n * 0.2 else " edge-r" if i > n * 0.8 else ""
        net = row["net_sentiment"]
        if pd.isna(net):
            net_text, dot = "–", ""
        else:
            net_text = signed(net, 1)
            dot = f'<i class="pt" style="top:{y(net) * plot_height / 100:.1f}px"></i>'
        few = (
            '<div class="row"><span>Too few reviews to plot</span><span></span></div>'
            if not ok.iloc[i] else ""
        )
        hits.append(
            f'<div class="bh-hit{edge}" tabindex="0" '
            f'aria-label="{long_date(row["date"])}: {int(row["mentions"])} reviews, '
            f'net sentiment {net_text}">{dot}'
            f'<div class="tip"><b>{long_date(row["date"])}</b>'
            f'<div class="row"><span>Reviews</span><span>{int(row["mentions"]):,}</span></div>'
            f'<div class="row"><span>Net sentiment</span><span>{net_text}</span></div>'
            f'<div class="row"><span>Positive</span><span>{int(row["positive"]):,}</span></div>'
            f'<div class="row"><span>Neutral</span><span>{int(row["neutral"]):,}</span></div>'
            f'<div class="row"><span>Negative</span><span>{int(row["negative"]):,}</span></div>'
            f"{few}</div></div>"
        )

    label_idx = sorted({round(i * (n - 1) / 4) for i in range(5)})
    xlabels = "".join(
        f'<span style="position:absolute;left:{x(i):.2f}%;'
        f'transform:translateX({"0" if i == 0 else "-100%" if i == n - 1 else "-50%"})">'
        f'{short_date(trend["date"].iloc[i])}</span>'
        for i in label_idx
    )

    return (
        f'<div class="bh-chart" role="group" aria-label="Net sentiment by day">'
        f'<div class="bh-yaxis" style="height:{plot_height}px">{yaxis}</div>'
        '<div class="bh-plot">'
        + svg_image(
            f"{grid}{daily_paths}{smooth_paths}", "0 0 100 100",
            f"display:block;width:100%;height:{plot_height}px",
            preserve=' preserveAspectRatio="none"',
        ) +
        f'<div class="bh-bars" aria-hidden="true">{bars}</div>'
        f'<div class="bh-hits">{"".join(hits)}</div></div>'
        f'<div class="bh-xaxis" style="position:relative;height:18px">{xlabels}</div>'
        "</div>"
        '<div class="bh-key">'
        '<span><i class="sw"></i>7-day net sentiment</span>'
        '<span><i class="sw dash"></i>Daily net sentiment</span>'
        '<span><i class="sw bar"></i>Reviews per day</span></div>'
    )


# -----------------------------
# Rating cross-check and terms
# -----------------------------

def rating_rows(check):
    table = check["table"]
    rows = []
    for stars in (5, 4, 3, 2, 1):
        pos, neu, neg = (int(table.loc[stars, c]) for c in ("Positive", "Neutral", "Negative"))
        total = pos + neu + neg
        if total:
            segs = "".join(
                f'<i class="c-{k}" style="width:{v / total * 100:.2f}%" '
                f'title="{label}: {v:,} ({v / total * 100:.0f}%)"></i>'
                for k, label, v in (("pos", "Positive", pos),
                                    ("neu", "Neutral", neu),
                                    ("neg", "Negative", neg)) if v
            )
        else:
            segs = ""
        rows.append(
            f'<div class="bh-rate"><span class="lbl">{stars} star{"s" if stars > 1 else ""}</span>'
            f'<div class="bh-bar" role="img" aria-label="{stars} star reviews: '
            f'{pos} positive, {neu} neutral, {neg} negative">{segs}</div>'
            f'<span class="n">{total:,}</span></div>'
        )

    legend = (
        '<div class="bh-legend" style="margin-top:10px">'
        '<span><i class="dot c-pos"></i>Positive</span>'
        '<span><i class="dot c-neu"></i>Neutral</span>'
        '<span><i class="dot c-neg"></i>Negative</span></div>'
    )
    return "".join(rows) + legend


def rating_note(check):
    high, low = check["high_positive_share"], check["low_negative_share"]
    if high is None or low is None:
        return ""
    text = (
        f"<b>{high:.0f}%</b> of 4–5 star reviews are classed Positive. "
        f"<b>{low:.0f}%</b> of 1–2 star reviews are classed Negative."
    )
    if low < 50:
        text += (
            " Negative reviews are being under-detected, so the negative "
            "share and the health score above probably look better than "
            "they should. The rule vocabulary is still being expanded."
        )
    return f'<div class="bh-note">{text}</div>'


def term_list(title, terms):
    if not terms:
        return (
            f'<h3 class="bh-sub-h">{escape(title)}</h3>'
            '<p class="bh-lede">No reviews in this group for the current filters.</p>'
        )
    peak = terms[0][1]
    rows = "".join(
        f'<div class="bh-term"><span class="w">{escape(word)}</span>'
        f'<span class="t"><i style="width:{count / peak * 100:.1f}%"></i></span>'
        f'<span class="n">{count:,}</span></div>'
        for word, count in terms
    )
    return f'<h3 class="bh-sub-h">{escape(title)}</h3>{rows}'


# -----------------------------
# Reviews
# -----------------------------

def stars_svg(rating):
    try:
        filled = int(round(float(rating)))
    except (TypeError, ValueError):
        return ""
    shapes = "".join(
        f'<polygon class="{"on" if i < filled else "off"}" points="{STAR_POINTS}" '
        f'transform="translate({i * 13},0)"/>'
        for i in range(5)
    )
    return svg_image(
        shapes, "0 0 64 12", "display:block;width:64px;height:12px",
        alt=f"{filled} out of 5 stars",
    )


def review_list(data):
    if data.empty:
        return ""
    cls = {"Positive": "pos", "Negative": "neg", "Neutral": "neu"}
    rows = []
    for _, r in data.iterrows():
        sentiment = r["sentiment"]
        k = cls.get(sentiment, "neu")
        rows.append(
            '<article class="bh-review">'
            f'<div class="d">{short_date(r["date"])}</div>'
            f'<div><span class="pill {k}"><i class="dot c-{k}"></i>{escape(sentiment)}</span>'
            f'<div class="stars">{stars_svg(r.get("rating"))}</div></div>'
            f'<div class="tx">{escape(str(r["text"]))}</div></article>'
        )
    return f'<div class="bh-reviews">{"".join(rows)}</div>'


# -----------------------------
# Static blocks
# -----------------------------

def section(title, lede, body):
    lede_html = f'<p class="bh-lede">{lede}</p>' if lede else ""
    return f'<section class="bh-section"><h2>{escape(title)}</h2>{lede_html}{body}</section>'


def empty_state(title, text):
    return f'<div class="bh-empty"><h2>{escape(title)}</h2><p>{escape(text)}</p></div>'


def method_note(source, start, end, total):
    return (
        '<details class="bh-method"><summary>How this is measured</summary><ul>'
        f"<li><b>Data.</b> {total:,} public {escape(source)} reviews, "
        f"{escape(span_label(start, end))}. Reviews describe the app, not the whole company.</li>"
        "<li><b>Sentiment.</b> Each review is cleaned, then scored with a "
        "word list. Common phrases (“not working”, “no wahala”) "
        "score two. Other words score one, or two for strong words "
        "(“scam”, “excellent”). A negation in the three words "
        "before (“not good”, “can’t”) flips a word and an "
        "intensifier (“very”) doubles it. A total above zero is "
        "Positive, below zero Negative, zero Neutral. No machine learning.</li>"
        "<li><b>Net sentiment.</b> Positive % minus Negative %.</li>"
        "<li><b>Brand health score.</b> <code>50 + net sentiment / 2</code>, "
        "kept between 0 and 100. 50 means balanced.</li>"
        "<li><b>Limits.</b> Rules miss sarcasm, slang and local phrasing. "
        "Star ratings are shown beside the rules as an independent check. "
        "Online reviews measure public perception only, not awareness, "
        "loyalty or purchase intent.</li></ul></details>"
    )
