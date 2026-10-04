"""
Validation of the rule-based sentiment analysis (pipeline stage 7).

Two independent checks:

1. Star-rating agreement (automatic). Customers write their own star
   rating, so it is a free, independent signal. It is imperfect (a
   3-star review can be positive or negative), so only the clear ends
   are used: 4-5 stars should be Positive and 1-2 stars Negative.

2. Manually labelled sample (human ground truth). `make-sample` writes a
   blind sample (no rating, no rule result shown) for people to label;
   `evaluate` then reports accuracy, per-class precision/recall/F1 and a
   confusion matrix.

Development/test split: reviews are divided in two halves by a hash of
the review id. Vocabulary is chosen by reading only the development half,
and results are reported on the test half as well, so the improvement is
not just the rules memorising the reviews they were tuned on.

Usage:
    python -m sentiment.validate ratings
    python -m sentiment.validate make-sample [--n 100]
    python -m sentiment.validate evaluate [--labels data/labelled_sample.csv]
"""

import argparse
import hashlib
import os

import pandas as pd

ANALYZED_FILE = "data/opay/analyzed_reviews.csv"
SAMPLE_FILE = "data/labelled_sample.csv"
LABELS = ["Positive", "Neutral", "Negative"]


# -----------------------------
# Development / test split
# -----------------------------

def split_of(review_id):
    """'dev' or 'test', stable for a given review id."""
    digest = hashlib.md5(str(review_id).encode("utf-8")).hexdigest()
    return "dev" if int(digest, 16) % 2 == 0 else "test"


def add_split(data):
    data = data.copy()
    data["split"] = data["id"].map(split_of)
    return data


# -----------------------------
# 1. Star-rating agreement
# -----------------------------

def rating_agreement(data):
    """Agreement between rule-based sentiment and clear star ratings."""
    high = data[data["rating"] >= 4]
    low = data[data["rating"] <= 2]
    predicted_negative = data[data["sentiment"] == "Negative"]

    def share(frame, label):
        return float((frame["sentiment"] == label).mean() * 100) if len(frame) else None

    return {
        "reviews": len(data),
        "positive_recall_4_5_star": share(high, "Positive"),
        "negative_recall_1_2_star": share(low, "Negative"),
        "wrong_way_4_5_star_negative": share(high, "Negative"),
        "wrong_way_1_2_star_positive": share(low, "Positive"),
        "negative_precision": (
            float((predicted_negative["rating"] <= 2).mean() * 100)
            if len(predicted_negative) else None
        ),
        "neutral_share": share(data, "Neutral"),
    }


def print_ratings(data):
    data = add_split(data)
    rows = {"all": data, "dev": data[data["split"] == "dev"],
            "test": data[data["split"] == "test"]}
    table = pd.DataFrame({k: rating_agreement(v) for k, v in rows.items()})
    print(table.round(1).to_string())


# -----------------------------
# 2. Manually labelled sample
# -----------------------------

def make_sample(data, n=100, seed=42):
    """
    Blind sample for human labelling.

    Drawn evenly from what the rules called Positive, Neutral and
    Negative, so the rare Negative class gets enough examples to measure.
    The file shows ONLY the review text, so labellers are not influenced
    by the star rating or the rule result. Distinct texts only.
    """
    pool = data.drop_duplicates(subset="text")
    pool = pool[pool["clean_text"].str.len() >= 3]

    per_class = -(-n // 3)   # round up so the total reaches n
    parts = [
        pool[pool["sentiment"] == label].sample(
            min(per_class, (pool["sentiment"] == label).sum()), random_state=seed
        )
        for label in LABELS
    ]
    sample = pd.concat(parts).sample(frac=1, random_state=seed).head(n)
    sample = sample[["id", "text"]].copy()
    sample["human_label"] = ""
    return sample


# -----------------------------
# Evaluation against human labels
# -----------------------------

def confusion(true, predicted):
    return pd.crosstab(
        pd.Categorical(true, LABELS), pd.Categorical(predicted, LABELS),
        rownames=["Human"], colnames=["Rules"], dropna=False,
    )


def class_report(true, predicted):
    rows = {}
    for label in LABELS:
        tp = int(((true == label) & (predicted == label)).sum())
        fp = int(((true != label) & (predicted == label)).sum())
        fn = int(((true == label) & (predicted != label)).sum())
        precision = tp / (tp + fp) if tp + fp else float("nan")
        recall = tp / (tp + fn) if tp + fn else float("nan")
        f1 = (2 * precision * recall / (precision + recall)
              if precision == precision and recall == recall and precision + recall else float("nan"))
        rows[label] = {"support": int((true == label).sum()),
                       "precision": precision, "recall": recall, "f1": f1}
    return pd.DataFrame(rows).T


def evaluate(labels_file=SAMPLE_FILE, analyzed_file=ANALYZED_FILE):
    labelled = pd.read_csv(labels_file, dtype={"id": str}, encoding="utf-8-sig")
    labelled["human_label"] = labelled["human_label"].astype(str).str.strip().str.capitalize()
    labelled = labelled[labelled["human_label"].isin(LABELS)]
    if labelled.empty:
        raise SystemExit(f"No labels found in {labels_file}. Fill the human_label column "
                         "with Positive, Neutral or Negative.")

    analyzed = pd.read_csv(analyzed_file, dtype={"id": str})[["id", "sentiment"]]
    merged = labelled.merge(analyzed, on="id", how="inner")
    true, predicted = merged["human_label"], merged["sentiment"]

    result = {
        "labelled_reviews": len(merged),
        "accuracy": float((true == predicted).mean() * 100),
        "per_class": class_report(true, predicted),
        "confusion": confusion(true, predicted),
    }

    # Optional: a second person labelled the same reviews independently
    if "labeller_2" in merged.columns:
        second = merged["labeller_2"].astype(str).str.strip().str.capitalize()
        both = second.isin(LABELS)
        if both.any():
            result["labeller_agreement"] = float((true[both] == second[both]).mean() * 100)
            result["cohens_kappa"] = cohens_kappa(true[both], second[both])
    return result


def cohens_kappa(a, b):
    """Agreement between two labellers beyond what chance would give."""
    observed = float((a == b).mean())
    expected = sum(
        float((a == label).mean()) * float((b == label).mean()) for label in LABELS
    )
    return (observed - expected) / (1 - expected) if expected < 1 else 1.0


def print_evaluation(result):
    print(f"Labelled reviews: {result['labelled_reviews']}")
    print(f"Accuracy: {result['accuracy']:.1f}%\n")
    print(result["per_class"].round(2).to_string(), "\n")
    print(result["confusion"].to_string())
    if "cohens_kappa" in result:
        print(f"\nLabeller agreement: {result['labeller_agreement']:.1f}% "
              f"(Cohen's kappa {result['cohens_kappa']:.2f})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["ratings", "make-sample", "evaluate"])
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--labels", default=SAMPLE_FILE)
    parser.add_argument("--force", action="store_true",
                        help="make-sample: overwrite a file that already has labels")
    args = parser.parse_args()

    if args.command == "ratings":
        print_ratings(pd.read_csv(ANALYZED_FILE, dtype={"id": str}))
    elif args.command == "make-sample":
        if os.path.exists(args.labels) and not args.force:
            existing = pd.read_csv(args.labels, encoding="utf-8-sig")
            if existing.get("human_label", pd.Series(dtype=str)).notna().any():
                raise SystemExit(f"{args.labels} already contains labels. "
                                 "Copy it first, or pass --force to overwrite.")
        sample = make_sample(pd.read_csv(ANALYZED_FILE, dtype={"id": str}), args.n)
        sample.to_csv(args.labels, index=False, encoding="utf-8-sig")
        print(f"Wrote {len(sample)} reviews to {args.labels}. Fill the human_label "
              "column (Positive / Neutral / Negative) without looking at star ratings. "
              "A second person can fill labeller_2 (add the column) for an agreement score.")
    else:
        print_evaluation(evaluate(args.labels))
