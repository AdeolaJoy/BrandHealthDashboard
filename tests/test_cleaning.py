import pandas as pd

from sentiment.cleaning import clean_dataframe, clean_text


def test_lowercase_and_punctuation():
    assert clean_text("Great App!!!") == "great app"


def test_url_removed():
    assert clean_text("see https://x.com/a now") == "see now"


def test_repeated_letters_collapsed():
    assert clean_text("sooooo goooood") == "soo good"


def test_emoji_becomes_word():
    assert "good" in clean_text("👍")
    assert "love" in clean_text("opay ❤️")


def test_missing_text_is_empty():
    assert clean_text(None) == ""
    assert clean_text(float("nan")) == ""


def test_dataframe_keeps_repeated_text_drops_unusable():
    df = pd.DataFrame({
        "id": ["1", "2", "3", "4", "4"],
        "text": ["good", "good", "!!!", "ok app", "ok app"],
        "date": ["2026-10-01"] * 3 + ["not a date", "not a date"],
    })
    out, stats = clean_dataframe(df)
    assert list(out["id"]) == ["1", "2"]          # repeated "good" kept
    assert stats["duplicate_ids_removed"] == 1
    assert stats["unusable_text_removed"] == 1    # "!!!"
    assert stats["invalid_date_removed"] == 1     # bad date
