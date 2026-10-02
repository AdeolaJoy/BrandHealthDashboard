import streamlit as st
import pandas as pd

from scraper.truxper_scraper import scrape_and_save
from sentiment.sentiment_analyzer import analyze_file
from metrics.brand_health import calculate_brand_health


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Brand Health Dashboard",
    page_icon="📊",
    layout="wide"
)


# -----------------------------
# Dashboard title
# -----------------------------
st.title("📊 Brand Health Dashboard")
st.write("Automated brand health analysis using rule-based sentiment analysis.")

st.divider()


# -----------------------------
# Analyze Brand button
# -----------------------------
if st.button("🔄 Analyze Brand", type="primary"):

    with st.spinner("Scraping brand data..."):
        scrape_and_save()

    with st.spinner("Analyzing sentiment..."):
        analyze_file()

    with st.spinner("Calculating brand health..."):
        results = calculate_brand_health()

    st.success("Brand analysis completed successfully!")


# -----------------------------
# Load analyzed data
# -----------------------------
data = pd.read_csv("data/analyzed_reviews.csv")


# -----------------------------
# Calculate brand health
# -----------------------------
results = calculate_brand_health()


total_mentions = results["total_mentions"]
positive_count = results["positive_count"]
negative_count = results["negative_count"]
neutral_count = results["neutral_count"]

positive_percentage = results["positive_percentage"]
negative_percentage = results["negative_percentage"]
neutral_percentage = results["neutral_percentage"]

net_sentiment = results["net_sentiment"]
brand_health_score = results["brand_health_score"]


# -----------------------------
# Key metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Mentions",
    total_mentions
)

col2.metric(
    "Positive",
    f"{positive_percentage:.1f}%"
)

col3.metric(
    "Negative",
    f"{negative_percentage:.1f}%"
)

col4.metric(
    "Brand Health Score",
    f"{brand_health_score:.1f}/100"
)


st.divider()


# -----------------------------
# Sentiment distribution
# -----------------------------
st.subheader("Sentiment Distribution")

sentiment_data = pd.DataFrame({
    "Sentiment": ["Positive", "Negative", "Neutral"],
    "Percentage": [
        positive_percentage,
        negative_percentage,
        neutral_percentage
    ]
})

st.bar_chart(
    sentiment_data.set_index("Sentiment")
)


# -----------------------------
# Brand health information
# -----------------------------
st.subheader("Brand Health Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Net Sentiment",
        f"{net_sentiment:.1f}%"
    )

with col2:
    st.metric(
        "Neutral Mentions",
        neutral_count
    )


st.divider()


# -----------------------------
# Review data
# -----------------------------
st.subheader("Analyzed Brand Mentions")

st.dataframe(
    data,
    use_container_width=True
)
