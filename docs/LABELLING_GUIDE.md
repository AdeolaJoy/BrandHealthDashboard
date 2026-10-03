# Labelling guide: validating the sentiment rules

**Goal.** Create a human "ground truth" for 100 reviews so the project can report how accurate the rule-based sentiment analysis really is.

**File.** `data/labelled_sample.csv` (open in Excel or Google Sheets; it is saved so emojis display correctly).

| Column | What to do |
|---|---|
| `id` | Leave as is. |
| `text` | The review. Read only this. |
| `human_label` | Type exactly one of: `Positive`, `Neutral`, `Negative`. |
| `labeller_2` | Optional. A second person adds this column and labels the same reviews **independently** (do not compare until both are finished). |

## Rules for labelling

Judge **only the words written by the customer**, as if you had never seen a star rating.

- **Positive.** The customer expresses satisfaction, praise, thanks or approval of the app or service ("fast and reliable", "no wahala", an approving emoji).
- **Negative.** The customer expresses a complaint, problem, frustration or distrust ("can't login", "money stuck", "scam", an angry emoji).
- **Neutral.** No opinion about the service: a question, a request for help with no complaint, a name, gibberish, or one word that carries no feeling ("opay").
- **Mixed review** ("good app but I can't withdraw"): label the **overall** impression. If it truly cannot be decided, use `Neutral`.
- Do not use the star rating, and do not try to guess what the rules would say.

## Why it is done this way

- The sample hides the star rating and the rules' answer, so neither can bias the labeller.
- It is drawn evenly from reviews the rules called Positive, Neutral and Negative. That gives enough of the rare Negative reviews to measure how well they are found. Because of this, the headline accuracy on this sample is **not** the accuracy over all reviews; the per-class precision and recall are the numbers to report.
- Two independent labellers let the report give an agreement score (Cohen's kappa), which shows the labels themselves are reliable.

## Running the check

```bash
python -m sentiment.validate evaluate
```

It prints accuracy, precision, recall and F1 for each class, a confusion matrix (rows = human, columns = rules) and, if `labeller_2` exists, the agreement between labellers.

Other commands:

```bash
python -m sentiment.validate ratings        # automatic check against star ratings
python -m sentiment.validate make-sample    # regenerate the blank sample (overwrites labels!)
```

**Warning:** `make-sample` overwrites `data/labelled_sample.csv`. Copy the file first if it already holds labels.
