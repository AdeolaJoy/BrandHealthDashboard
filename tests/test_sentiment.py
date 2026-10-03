import pandas as pd
import pytest

from sentiment.sentiment_analyzer import analyze_sentiment
from sentiment.validate import (
    class_report, confusion, make_sample, rating_agreement, split_of,
)


@pytest.mark.parametrize("text,label", [
    ("great app", "Positive"),
    ("terrible app", "Negative"),
    ("it is an app", "Neutral"),
    # negation, including contractions and a gap of up to 3 words
    ("not good", "Negative"),
    ("this is not very good", "Negative"),
    ("not bad", "Positive"),
    ("I don't like it", "Negative"),
    # phrases
    ("no wahala at all", "Positive"),
    ("can't login to my account", "Negative"),
    ("it is not working", "Negative"),
    ("good app but it keeps crashing", "Negative"),
    # sentiment words must not match inside other words
    ("badminton", "Neutral"),
])
def test_labels(text, label):
    assert analyze_sentiment(text)[0] == label


def test_intensifier_doubles_and_strong_words_weigh_more():
    assert analyze_sentiment("good")[1] == 1
    assert analyze_sentiment("very good")[1] == 2
    assert analyze_sentiment("scam")[1] == -2


def test_repeated_words_count_once():
    assert analyze_sentiment("angry angry angry angry")[1] == -1


def test_negation_window_is_limited():
    # negation 4+ words before the sentiment word no longer applies
    assert analyze_sentiment("not a b c d good")[0] == "Positive"


def test_split_is_stable_and_roughly_even():
    assert split_of("abc") == split_of("abc")
    halves = [split_of(str(i)) for i in range(2000)]
    assert 800 < halves.count("dev") < 1200


def test_rating_agreement():
    df = pd.DataFrame({
        "rating": [5, 5, 1, 1, 3],
        "sentiment": ["Positive", "Neutral", "Negative", "Positive", "Neutral"],
    })
    r = rating_agreement(df)
    assert r["positive_recall_4_5_star"] == 50.0
    assert r["negative_recall_1_2_star"] == 50.0
    assert r["wrong_way_1_2_star_positive"] == 50.0


def test_class_report_and_confusion():
    true = pd.Series(["Positive", "Positive", "Negative", "Neutral"])
    pred = pd.Series(["Positive", "Neutral", "Negative", "Neutral"])
    rep = class_report(true, pred)
    assert rep.loc["Positive", "recall"] == 0.5
    assert rep.loc["Positive", "precision"] == 1.0
    assert confusion(true, pred).loc["Positive", "Neutral"] == 1


def test_sample_is_blind_and_balanced():
    n = 90
    df = pd.DataFrame({
        "id": [str(i) for i in range(n)],
        "text": [f"text {i}" for i in range(n)],
        "clean_text": [f"text {i}" for i in range(n)],
        "rating": [5] * n,
        "sentiment": ["Positive", "Neutral", "Negative"] * (n // 3),
    })
    sample = make_sample(df, n=30)
    assert list(sample.columns) == ["id", "text", "human_label"]   # no rating / rule
    assert len(sample) == 30
    assert (sample["human_label"] == "").all()


def test_evaluate_with_labels(tmp_path):
    from sentiment.validate import evaluate
    pd.DataFrame({"id": ["1", "2", "3", "4"],
                  "sentiment": ["Positive", "Neutral", "Negative", "Negative"]}
                 ).to_csv(tmp_path / "analyzed.csv", index=False)
    pd.DataFrame({"id": ["1", "2", "3", "4"], "text": ["a"] * 4,
                  "human_label": ["positive", "Negative", "Negative", "Neutral"],
                  "labeller_2": ["Positive", "Negative", "Negative", "Negative"]}
                 ).to_csv(tmp_path / "labels.csv", index=False)
    r = evaluate(str(tmp_path / "labels.csv"), str(tmp_path / "analyzed.csv"))
    assert r["labelled_reviews"] == 4
    assert r["accuracy"] == 50.0
    assert r["labeller_agreement"] == 75.0
