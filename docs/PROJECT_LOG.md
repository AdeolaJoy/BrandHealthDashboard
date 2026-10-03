# Project Log: Automated Brand Health Dashboard

**Topic:** Development of an Automated Brand Health Dashboard Using Rule-Based Sentiment Analysis and Python Web Scraping
**Type:** BSc final year project
**Stack:** Python, Streamlit, CSV storage, Git/GitHub

This log records each planning and building step, what was done, and why. It is meant to feed directly into the methodology and implementation chapters of the project report. New entries are added at the bottom as work progresses.

---

## 1. Research definition

**Operational definition of brand health.** The measurable state of a brand's online public perception, represented by the volume and sentiment of publicly available textual mentions and how they change over time.

**Scope limitation.** The system does not measure awareness, loyalty or purchase intent. It covers online textual perception only, using data that can be collected reliably.

**Why this matters.** Brand health is a broad concept. Stating a narrow, measurable definition up front keeps the project achievable and defensible, and tells examiners exactly what the results do and do not claim.

## 2. Agreed pipeline (from the collaboration blueprint)

1. Case-study brand (`brand_config.py`)
2. Public online data source
3. Python web scraper
4. Raw data storage (`data/scraped_reviews.csv`)
5. Data cleaning / preprocessing
6. Brand relevance filter
7. Rule-based sentiment analysis
8. Analyzed data (`data/analyzed_reviews.csv`)
9. Brand health metrics (volume, sentiment %, net sentiment, trends)
10. Streamlit dashboard
11. Interpretation / decision support

**Why this structure.** Each stage reads one file and writes another, so each can be built, tested and explained on its own, and the methodology chapter can follow the same order.

## 3. Starting state of the repository (audit, 2026-10-02)

| Area | Finding |
|---|---|
| `brand_config.py` | `brand_name` is "Opay" but all keywords are MTN-related. Inconsistent. |
| Scraper | Scrapes OPay reviews from Truxper. A Google Play test script also exists. |
| `data/scraped_reviews.csv` | Only about 2 OPay rows. Too small for analysis. |
| `data/analyzed_reviews.csv` | Contains MTN news articles from Nairametrics. Stale and from a different brand and source. |
| `sentiment_analyzer.py` | Core logic works. Has an unreachable duplicated block after `return` in `analyze_file`. Negation only checks the previous word. |
| `metrics/brand_health.py` | Counts, percentages, net sentiment, score `50 + net/2`. Ignores `brand_relevant`. No trend calculation. |
| Cleaning (step 5) | No module exists. |
| `app.py` | Exists, not yet reviewed. |

**Why audit first.** The blueprint requires agreement before changing brand, source or metric formulas. We need to know exactly what is already in place so that we change only what has to change.

## 4. Open decisions (need agreement before building)

| # | Decision | Options | Status |
|---|---|---|---|
| D1 | Case-study brand | MTN Nigeria / OPay / other | OPEN |
| D2 | Production data source | Google Play reviews / Truxper / other | OPEN |
| D3 | Composite score formula | Keep `50 + net/2` or change | OPEN |

**Source-selection criteria** (from the blueprint, used to justify D2):
large enough dataset; publicly accessible; real consumer text; has date and rating; repeatable collection; no bypassing of access restrictions; relevant to the brand; reproducible in the methodology.

**Initial assessment of candidates** (to be confirmed by testing):

| Source | Volume | Real consumer text | Date and rating | Notes |
|---|---|---|---|---|
| Google Play reviews | High | Yes | Yes | Likely best fit. Test script exists. |
| Truxper | Low (a few reviews) | Yes | Yes | Probably too small. |
| Nairametrics news | Medium | No (journalism, not customer opinion) | Date only | Fails the "consumer mentions" criterion. |
| Reddit (PRAW) | Medium to high, depends on brand | Yes | Date yes, rating no | Free official API, easy to defend. Needs API credentials. Posts may be off-topic, so the relevance filter matters more. |

**Other ideas raised (2026-10-02), not yet agreed:**
- **VADER as a baseline.** VADER is a rule-based lexicon, so it fits the method. Because the blueprint specifies a custom vocabulary, replacing it needs agreement. Proposal: keep the custom lexicon as the main method and run VADER on the same data as a comparison baseline.
- **Scheduled automation.** The title says "Automated", but nothing runs on its own yet. Proposal: add a `schedule`/cron job that re-scrapes and re-analyzes periodically, late in the build.
- **Word cloud** on the dashboard as an extra theme view.

Decisions are recorded here once made, with the reasoning.

## 5. Build plan

| Stage | Work | Files | Reason |
|---|---|---|---|
| 0 | Record decisions D1 to D3 | this log | The blueprint requires agreement first. |
| 1 | Make `brand_config.py` consistent with the chosen brand | `brand_config.py` | Wrong keywords would silently filter out the wrong data. |
| 2 | Harden the scraper (retries, error handling, pagination) and standardise the schema `id, brand, text, rating, date, source, url` | `scraper/` | Reliable, repeatable collection is a source criterion. |
| 3 | Add a raw-data inspection script (row count, missing values, date range, duplicates) | `scraper/inspect_data.py` | Blueprint step "inspect the raw dataset". Also gives figures for the report. |
| 4 | Add a cleaning module (normalise text, drop empty and duplicate rows, parse dates) | `sentiment/cleaning.py` | Step 5 of the pipeline is currently missing. |
| 5 | Apply the relevance filter and make metrics use relevant rows only | `sentiment_analyzer.py`, `metrics/brand_health.py` | The filter is computed today but never used. |
| 6 | Improve the sentiment rules (remove dead code, wider negation window, larger vocabulary, intensifiers) | `sentiment_analyzer.py`, `brand_config.py` | Better accuracy within the agreed rule-based method. |
| 7 | Validate sentiment against a manually labelled sample (about 100 rows) and against star ratings | `data/labelled_sample.csv`, `sentiment/validate.py` | Gives a measured accuracy figure for the report. |
| 8 | Add monthly trends, source and rating breakdowns, complaint and praise themes | `metrics/brand_health.py` | Blueprint outputs: trends and theme views. |
| 9 | Update the dashboard (filters, trend charts, themes) | `app.py` | Step 10 of the pipeline. |
| 10 | Add automated tests and run the full pipeline end to end | `tests/` | Reproducibility and proof of correctness. |
| 11 | Commit in small steps, then review with the collaborator | git | Blueprint workflow step 10 and 11. |

## 6. Change rules (from the blueprint)

Agree with the collaborator before: changing the brand, the data source, the sentiment method, the metric formulas, adding ML or an external AI API, changing the dashboard framework, or widening the scope.
Free to improve without further agreement: scraper reliability, cleaning, vocabulary, negation and intensifier handling, validation, themes, trends, dashboard visuals, documentation, tests.

---

## Build log

*(Entries are added here as each stage is completed, in the form: date, what was done, why, result.)*

### 2026-10-02: Planning
- Read the collaboration blueprint and audited the repository (section 3).
- Wrote this log and the build plan.
- **Result:** plan drafted. Waiting on decisions D1 to D3.

### 2026-10-03: Data-source evaluation (tested, not yet decided)
Tested each candidate with a quick script against the blueprint's section 7 criteria.

| Source | Method | Result |
|---|---|---|
| Google Play, static page (`requests` + BeautifulSoup) | Existing `test_google_play.py` approach | 200 OK but only **6 reviews** are in the HTML. Reviews load by scrolling, so this approach cannot reach volume. |
| Google Play, review feed (`google-play-scraper` library) | `reviews()` with paging | **5,000 OPay reviews in about 9 seconds**, covering 2026-09-12 to 2026-10-01 (roughly 250 per day). Fields: text, star rating, date, app version, reviewId, developer reply. No login or access bypass. Stable and repeatable. |
| Truxper | Existing `truxper_scraper.py` | OPay page has **2 reviews**, page 2 is empty. The MTN Nigeria page returned **0**. Too small for the volume criterion. |
| Reddit, anonymous | Public search JSON | **HTTP 403 Forbidden.** Reddit needs official API credentials (PRAW). We will not work around the block. It stays a candidate only if credentials are obtained. |
| Nairametrics news | Already in the repo | Fails the "real consumer text" criterion (journalism, not customer opinion). |

**Findings and what follows from them**
- Google Play meets every criterion for OPay: large, public, consumer text, rating and date, repeatable, no bypass. It is the recommended production source.
- Caveat: the `google-play-scraper` library uses Google's internal review feed, which is not an official API. This should be stated in the methodology as a limitation, together with the collection date.
- Caveat: Play reviews are about the **app** (OPay is a fintech app), not the whole brand. This should also be stated as a scope limit.
- **MTN is harder.** The MTN app search returned no usable app id, and four guesses returned zero reviews. If MTN stays the brand, we must first find its real app id. OPay works today.
- The brand and source decisions are linked: OPay + Google Play is the only combination proven to work so far.

**Open decisions D1 and D2 are still waiting on your collaborator.** Recommended: D1 = OPay, D2 = Google Play.

### 2026-10-03: Stages 1-2 built (config + Google Play scraper)
**Assumption:** OPay + Google Play, pending collaborator agreement (D1, D2). The scraper is isolated, so it is easy to replace.

**What was done**
- `brand_config.py`: brand set to OPay, industry set to Fintech / Mobile Payments, MTN keywords replaced with OPay keywords, and a `play_store` block added (app id, country, language, review count). *Why:* the old config mixed two brands, which would silently filter out the right data. Sentiment word lists are unchanged for now and get expanded in stage 6.
- `scraper/play_store_scraper.py` (new): fetches the newest reviews via `google-play-scraper` and saves them in the standard schema `id, brand, text, rating, date, source, source_type, url`. The id is Google's `reviewId`. *Why:* a fixed schema means any future source can feed the same pipeline.
- Re-running **merges** into the CSV and removes duplicate ids. *Why:* the "Automated" requirement needs repeat runs that build up history without duplicating data.
- `app.py`: import switched from the Truxper scraper to the new scraper so the dashboard button still works. The Truxper scraper stays in the repo for reference.
- `requirements.txt` added (requests, beautifulsoup4, pandas, streamlit, google-play-scraper, pytest). *Why:* reproducibility for examiners.
- Removed the 2 old Truxper rows from the raw file (different date format, source rejected as too small).

**Result:** `data/scraped_reviews.csv` now holds **3000 real OPay reviews** from 2026-09-22 to 2026-10-02, no missing values, ids unique. A second run fetched 500 reviews and the total did not grow, so the merge de-duplicates correctly.

**Observation for stage 4/5:** many Play reviews are very short ("my money", "opay u be BABA") and none need to mention "opay" because every review is about the app. The keyword relevance filter would wrongly drop most of them, so for Google Play the relevance step must use source-based relevance plus off-topic checks.

**Next:** stage 3 (raw-data inspection script), then stage 4 (cleaning).

### 2026-10-03: Stages 3-4 built (raw-data inspection + cleaning)
**Stage 3: `scraper/inspect_data.py`.** Prints row count, unique ids, missing values, date range, rating spread, text length, and counts of very short, repeated and emoji-containing texts. Run: `python -m scraper.inspect_data`. *Why:* the blueprint says to inspect the raw dataset before cleaning, and the figures go straight into the report's data-description section.

**Findings on the raw data (3,000 reviews, 2026-09-22 to 2026-10-02)**
- No missing values, no unparseable dates, all ids unique, one source.
- Median review is only 20 characters. 20 reviews have 3 characters or fewer.
- 725 reviews repeat another review's exact text (e.g. "good", "nice").
- 417 contain emojis or non-ASCII characters.

**Stage 4: `sentiment/cleaning.py`.** `clean_text()` lowercases, removes URLs, maps common emojis to sentiment words, collapses stretched letters ("goooood" becomes "good"), and strips punctuation. `clean_dataframe()` drops unusable rows and returns stats. The original `text` column is kept; the result goes in `clean_text`.

**Design decisions and reasons**
1. **Repeated identical texts are kept.** 725 reviews say things like "good". These are separate customers, so removing them would understate how common an opinion is. Duplicates are removed by review id only.
2. **Emojis are mapped to words, not deleted.** The analyser reads words only, and app reviews carry much of their sentiment in emojis (👍, ❤️, 😡). The map is small and listed in `EMOJI_WORDS` so it can be explained and extended. This stays within the agreed rule-based method, since it extends the lexicon.
3. **The original text is preserved.** The dashboard can show the real review, and the cleaning can be audited.
4. **A row is dropped only if it has under 2 letters or digits, or an invalid date.** Short reviews like "great" are real opinions and carry a rating.

**Result:** 3,000 rows in, **2,992 usable rows out** (8 dropped as unusable text, 0 duplicates, 0 invalid dates). `tests/test_cleaning.py` has 6 passing tests.

**Next:** stage 5, which wires cleaning and relevance into the analyser and makes the metrics use only relevant rows.

### 2026-10-03: Stage 5 built (cleaning + relevance wired into the pipeline)
**What was done**
- `sentiment/sentiment_analyzer.py`: `analyze_file()` now runs cleaning, then the relevance filter, then sentiment on `clean_text`. The output keeps the original `text`, `clean_text`, `rating`, `date`, `brand_relevant`, `sentiment` and `score`. *Why:* the blueprint pipeline (steps 5 to 8) was only partly connected; cleaning did not exist and the relevance flag was never used.
- Removed the unreachable duplicated block that sat after `return` in the old file.
- `is_brand_relevant(text, source)`: a mention is relevant if it contains a brand keyword **or** comes from a brand-specific source. New config key `brand_specific_sources: ["Google Play"]`. *Why:* a review on OPay's own Play page is about OPay even when it just says "my money". A keyword-only rule would have discarded most of the data.
- `metrics/brand_health.py`: counts only rows with `brand_relevant == True`. *Why:* irrelevant mentions would distort volume and sentiment.
- `tests/test_pipeline.py`: 3 new tests (relevance rules, and an end-to-end check on a small dataset that the irrelevant row is excluded and the counts are right). All 9 tests pass.

**First full-pipeline result (2,992 reviews)**
Positive 1,601 (53.5%), Neutral 1,358 (45.4%), Negative 33 (1.1%). Net sentiment +52.4, score 76.2/100.

**Problem found: the current vocabulary badly under-detects negativity.** There are 165 reviews with 1 or 2 stars, but only 33 reviews are classed Negative. Many 1 and 2 star reviews fall into Neutral because the word lists (about 15 words each) do not contain words customers actually use for a payments app ("scam", "stuck", "pending", "frozen", "debited", "refund", "fraud", "restricted", "useless"). This inflates the health score. It is the main target of stage 6 and is exactly what the manual validation in stage 7 will measure.

**Next:** stage 6, improve the sentiment rules (wider negation window, handle contractions such as "don't", larger OPay-specific vocabulary), then re-run and compare against star ratings.

### 2026-10-03: Stage 9 (early): dashboard frontend redesign
**Why now.** The first dashboard showed 4 numbers, one bar chart and a raw table. The blueprint asks for KPIs, charts, trends, tables and filters, so the interface was rebuilt before more analysis work.

**Constraints respected**
- The framework stays **Streamlit** (the blueprint requires agreement to change it). All custom design is injected CSS and HTML inside Streamlit.
- No metric formula changed. Everything new is a view of existing data, or an added breakdown.
- Design tools used: the `taste-skill` and `impeccable` design skills (installed with `npx`), plus `PRODUCT.md`, which records who the dashboard is for. Facts in `PRODUCT.md` that were inferred, not confirmed, are marked as such.

**What was built**
| File | Purpose |
|---|---|
| `ui/styles.py` | Design tokens (colour, type, spacing) and CSS. Light and dark themes follow the operating system. One sans family (Geist, system fallback). |
| `ui/components.py` | HTML builders for the header, headline, stat strip, sentiment mix bar, trend chart, rating cross-check, word lists, review list and method note. |
| `metrics/brand_health.py` | New functions: `daily_trend`, `period_change`, `rating_crosscheck`, `top_terms`. `calculate_brand_health` now uses `summarize` so the dashboard can compute the same metrics on filtered data. |
| `.streamlit/config.toml` | Theme and minimal toolbar. |
| `app.py` | Rewritten page: filters (dates, star rating, sentiment, text search), overview, trend, rating check, words, review explorer, data table and CSV export, empty and error states. |
| `tests/test_metrics.py` | 6 tests for the new metric functions. All 15 tests pass. |

**Design decisions and reasons**
1. **Headline sentence first** ("Net sentiment is +52 across 4,986 reviews..."): a reader gets the answer in seconds. Four stat columns separated by hairlines follow, with no card grid.
2. **The trend chart shows a 7-day line over a dotted daily line, with review volume underneath.** Daily values alone are noisy. Days with under 20 reviews are left off the line, because a daily figure from 3 reviews is misleading (the last day of data is partial). The tooltip works with mouse or keyboard.
3. **Charts are hand-built HTML/SVG**, not a chart library. This keeps them sharp, theme-aware, free of extra dependencies, and easy to explain. Streamlit's sanitiser strips inline `<svg>` and data-URI images, so the SVG is delivered as a CSS background image.
4. **Colour only carries sentiment.** Positive is green, negative is red-orange, neutral is grey, and every colour is paired with a word, so nothing relies on colour alone. The buttons and chrome are neutral ink.
5. **A "Do the rules agree with star ratings?" panel** was added on purpose. It compares the rule-based sentiment with each review's star rating, an independent signal. It currently shows that only 11% of 1 to 2 star reviews are classed Negative, and the page says so in plain words (the note appears only while that share is below 50%). Showing this is more credible than hiding it, and it gives the validation chapter a concrete baseline for stage 6 to improve.
6. **Word lists are grouped by star rating**, not by the sentiment rules, so they stay meaningful while the rules are weak.
7. **A "How this is measured" note** states the data, the rules, the formulas and the limits. Examiners can read the method without opening the code.
8. **Filters apply to every view**, with a reset button and an empty state. A text search across the review text was added.

**Checked in a real browser (Chrome via Playwright):** desktop light, desktop dark and 390 px phone width; the chart tooltip; the rating filter (211 one-star reviews: net sentiment +13); a search with no matches (empty state); reset; "Show 20 more". No browser console errors.

**Bugs found and fixed during testing**
- The trend line and star icons were invisible, because Streamlit removes inline `<svg>` and data-URI `<img>`. Fixed with CSS background images.
- In dark mode the Refresh button label was invisible. Fixed by targeting the button's real attributes.
- First stat column was indented by Streamlit's default list padding.

**Known gaps**
- Complaint and praise **themes** are word counts only. Real themes (for example "transfer failed", "customer service") come with the vocabulary work.
- The score and Negative share are still too optimistic until stage 6.
- The font loads from Google Fonts. Offline, the system font is used instead.

**Housekeeping:** installing the design skills created `.agents/`, `.claude/` and `skills-lock.json` in the project folder. Decide with your collaborator whether to commit them or add them to `.gitignore`.

### 2026-10-03: Stage 6 built (sentiment rules v2) and Stage 7 tooling built
**Problem being solved.** After the first full run, only 11% of 1 to 2 star reviews were classed Negative and 22% were classed Positive. The vocabulary (about 15 words per side) and the one-word negation check were too weak for a payments app.

**Method: keep the research honest.** Reviews were split into a **development half** (2,470) and a **test half** (2,516) by a hash of the review id. Vocabulary was chosen by reading only the development half (plus general knowledge of app-review language). Results are reported on **both** halves. If the test half improves by about the same amount, the rules are not just memorising the reviews they were tuned on.

**What changed (still rule-based, no ML, formulas unchanged)**
| Area | Before | After |
|---|---|---|
| Vocabulary | 15 positive and 16 negative words | About 60 positive and 80 negative single words, plus 25 positive and 55 negative multi-word phrases ("not working", "can't login", "no wahala", "money stuck") |
| Strength | Every word scored 1 | Normal words 1, strong words ("scam", "excellent") 2, phrases 2 |
| Negation | Only the one word before; "don't" was split into "don" and "t" | Any negation in the 3 words before, and contractions are normalised ("can't" becomes "cant") |
| Intensifiers | Only the one word before; 6 words | Within 2 words before; 13 words ("so", "too", "super"...) |
| Repetition | "angry angry angry" counted three times | Back-to-back repeats count once |
| Matching | Plain word split | Phrases matched with word boundaries first, so "badminton" does not match "bad" |

The lists live in `brand_config.py` and the logic in `sentiment/sentiment_analyzer.py`. One bare "ok" was deliberately left out because it is usually neutral; only "not ok" counts.

**Results: agreement with star ratings** (`python -m sentiment.validate ratings`)
| Measure | Before (all) | After: development half | After: test half |
|---|---|---|---|
| 4-5 star reviews classed Positive | 55.3% | 84.1% | **83.9%** |
| 1-2 star reviews classed Negative | 11.2% | 41.6% | **37.7%** |
| 1-2 star reviews classed Positive (wrong way) | 22.0% | 30.9% | 29.5% |
| 4-5 star reviews classed Negative (wrong way) | 0.5% | 1.9% | 1.6% |
| Reviews left Neutral | 45.8% | 15.2% | 16.0% |

Headline dashboard numbers moved from Positive 53% / Negative 1.2% / score 75.9 to Positive 80% / Negative 4.4% / **score 87.8**.

**How to read this honestly**
- The gains are real and hold on the unseen test half (test positive recall 54.8% to 83.9%, test negative recall 13.0% to 37.7%). The test half is a little lower than the development half on negatives (37.7% vs 41.6%), which is the expected size of the small tuning advantage.
- **Star ratings are a noisy yardstick.** Reading the development reviews showed many 1 to 2 star reviews whose text is clearly positive ("excellent", "fantastic", "good app"), so part of the "wrong way" 30% is customers giving a wrong star rating, not rule errors. Negative reviews that stay Neutral are mostly indirect complaints with no complaint word ("it takes time to install", "palmpay is better than you guys"). This is why a human-labelled check (stage 7) is needed for the real accuracy.
- The score rose to 87.8 mainly because most reviews are genuinely positive: 84% of reviews are 4 to 5 stars. It should still be read with the known limits (negativity is under-detected, roughly 4 in 10 low-rated reviews are found).
- A rule-based method will always miss sarcasm and indirect complaints. This belongs in the limitations section.

**Stage 7: validation tooling (human labels still to be collected)**
- `sentiment/validate.py` with three commands: `ratings` (automatic check above), `make-sample` (writes a blind sample) and `evaluate` (accuracy, precision, recall, F1 per class, a confusion matrix, and Cohen's kappa if a second person labelled the same reviews).
- `data/labelled_sample.csv`: **100 reviews, blind** (text only; star rating and rule result are hidden so they cannot bias the labeller), drawn evenly from reviews the rules called Positive, Neutral and Negative so the rare Negative class has enough examples. `make-sample` refuses to overwrite a file that already contains labels unless `--force` is given.
- `docs/LABELLING_GUIDE.md`: definitions of Positive, Neutral and Negative and how to label.
- `tests/test_sentiment.py`: tests for the rules (negation, phrases, intensifiers, word boundaries), the split, the rating check, the confusion matrix and the evaluation. All 35 tests pass.

**Not done yet, and cannot be done by the tool: the human labels.** No accuracy figure from human labels exists yet. The 100 reviews must be labelled by you and your collaborator (ideally each person independently, for an agreement score). Then run `python -m sentiment.validate evaluate`. I did not label the sample myself, because AI-written labels presented as human ground truth would invalidate the validation.

**Next:** (1) label the sample and run `evaluate`; (2) if recall of Negative is still low, add words from the **development** half only and re-check on the **test** half; (3) stage 8: complaint and praise themes, which can now reuse the phrase lists.
