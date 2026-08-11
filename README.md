# News Credibility Analyser

An end-to-end NLP/ML system that classifies news articles as **Credible** or **Fake** based on writing style and vocabulary, with every prediction traced back to the specific model coefficients behind it. Built with TF-IDF, Logistic Regression, and a Streamlit front end.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-informational?style=flat-square)

---

## Overview

Fake-news detection is usually framed as if a model can verify facts. This project doesn't do that, and is explicit about it: it's a **supervised text classifier** that learns to distinguish two *writing styles* — the style of the Reuters wire copy and the style of the flagged/fabricated articles in its training set — and scores new text against that learned distinction using TF-IDF features and Logistic Regression.

That's a genuinely useful signal (stylistic tells correlate with fabricated content often enough to be a real classification problem), but it is **not** fact-checking, source verification, or real-time information retrieval. The app is upfront about this distinction in its own UI, and this README carries the same framing through — see [Limitations](#limitations) and [Data Leakage Investigation](#data-leakage-investigation) for exactly where that distinction matters most.

---

## Demo / Screenshots

### Analyse News

![Analyse News](assets/screenshots/analyse.png)

### Prediction & Explainability

![Prediction](assets/screenshots/prediction.png)
![Explainability](assets/screenshots/explainability.png)

Two screenshots that exist in the repository are deliberately **not** shown here: `home.png` and `model_insights.png` both display figures from before a later metrics-correction pass (a stale 99.04% accuracy stat on the Home page; stale 30,915/7,729 train/test counts and the old model-comparison table on Model Insights) that no longer match the numbers reported in [Model Performance](#model-performance). The three screenshots above were checked against the current app and don't show any such discrepancy.

---

## How It Works

```
Article title + body
        │
        ▼
Text preprocessing (app/text_processing.py — clean_text)
  lowercase → strip Reuters dateline/source leak → remove URLs/HTML
  → normalise digits → strip punctuation → tokenise
  → remove stopwords (negations kept) → lemmatise
        │
        ▼
TF-IDF vectorisation (fitted vectorizer.pkl, 30,000 features, unigrams + bigrams)
        │
        ▼
Logistic Regression (model.pkl)
        │
        ▼
Verdict (Credible / Fake) + confidence tier + top contributing terms
  pulled directly from the model's learned coefficients
```

The same `clean_text()` function is imported by both the training notebook and the running app (`app/text_processing.py`) — there is only one implementation, so inference can't silently drift from what the model was actually trained on.

**Confidence tiers**, based on the model's predicted probability for the winning class:

| Probability | Tier | Meaning |
|---|---|---|
| ≥ 85% | High Confidence | Result is reliable |
| 60–85% | Moderate Confidence | Likely correct, treat with caution |
| < 60% | Uncertain | Model isn't sure — verify manually |

---

## Key Features

| Feature | Description |
|---|---|
| Instant prediction | Paste a title + body, get a verdict and confidence score |
| Confidence tiers | High / Moderate / Uncertain, with an explicit warning banner on Uncertain results |
| Explainability | Top contributing terms shown as chips, pulled from real Logistic Regression coefficients — not an LLM-generated explanation |
| Highlighted article view | The same contributing terms highlighted in place inside your actual pasted article |
| Downloadable analysis report | Verdict, confidence, and top terms exported as a `.txt` file |
| Prediction history | Session-based, last 10 predictions, independent of the input form (clearing the form doesn't clear history, and vice versa) |
| Sample articles | One-click fake-style and credible-style examples for demoing without needing to source your own text |
| Input validation | Required-field checks and a soft word-count warning (not a hard block) for very short input |
| Model Insights page | Accuracy/precision/recall/F1/ROC-AUC across all three trained models, confusion matrices, ROC curves, feature importance |
| About page | Full pipeline walkthrough, dataset sources, and the notebooks behind the deployed model |

---

## Machine Learning Pipeline

**Dataset:** ISOT Fake News Dataset (`data/Fake.csv` + `data/True.csv`), 38,639 articles after deduplication.

**Preprocessing** (`app/text_processing.py`): lowercasing; stripping the Reuters wire-service dateline (`CITY (Reuters) -`) and any remaining standalone mentions of "reuters"; URL and HTML removal; digit sequences replaced with a `NUM` placeholder token; Unicode-aware punctuation stripping; tokenisation; stopword removal (negations — "not", "no", "never", "without", "neither", "nor" — are deliberately kept, since they carry meaning); lemmatisation.

**Split:** stratified 80/20 train/test split (30,911 train / 7,728 test articles after preprocessing), `random_state=42`.

**Feature extraction:** `TfidfVectorizer(max_features=30000, ngram_range=(1,2), min_df=3, sublinear_tf=True)`, **fit on the training split only** and applied to the test split with `.transform()` — no test-set leakage into the fitted vocabulary.

**Models compared:** Logistic Regression, Multinomial Naive Bayes, Random Forest — each evaluated with 5-fold stratified cross-validation on the training set, then scored once on the held-out test set.

**Model selection:** highest Test F1 wins; ties within 1% defer to the simplest model. Logistic Regression won outright (see [Model Performance](#model-performance)), so the tie-break rule wasn't even needed here.

**Final artifact:** the selected model (Logistic Regression) is retrained on the *full* 38,639-article dataset (train + test combined) before being serialized — standard practice once the held-out test set has already served its purpose for an unbiased performance estimate. This is why `model.pkl`'s training data differs from what `03_evaluation.ipynb`'s reported test metrics were computed on; the test metrics are the honest, out-of-sample estimate, computed before the final refit.

**Explainability:** no SHAP, no separate explainer model — `get_top_terms()` intersects the TF-IDF features actually present in a given article with the trained Logistic Regression's coefficients (`model.coef_`) and returns the strongest positive (Fake-pushing) and negative (Credible-pushing) terms found in that specific input.

**Inference:** `app/utils.py` loads `model.pkl` and `vectorizer.pkl` (cached via `st.cache_resource`), runs the same `clean_text()` used at training time, transforms with the already-fitted vectorizer, and calls `model.predict_proba()`.

---

## Model Performance

Test-set results from `03_evaluation.ipynb`, evaluated on the held-out 7,728-article test split:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | CV F1 (mean ± std) | Train Time |
|---|---|---|---|---|---|---|---|
| **Logistic Regression** ⭐ | **98.64%** | **98.69%** | **98.57%** | **98.63%** | 0.9986 | 0.9853 ± 0.0010 | 0.79s |
| Random Forest | 97.49% | 97.58% | 97.36% | 97.46% | 0.9972 | 0.9755 ± 0.0013 | 64.27s |
| Multinomial NB | 95.76% | 95.70% | 95.74% | 95.72% | 0.9905 | 0.9577 ± 0.0022 | 0.04s |

**Selected model: Logistic Regression** (confusion matrix on the test set — TN 4,209 / FP 29 / FN 76 / TP 3,414).

These numbers are held-out test performance on the ISOT dataset — they describe how well the model separates *this dataset's* Credible and Fake examples, not real-world accuracy on arbitrary news from the internet. See [Data Leakage Investigation](#data-leakage-investigation) for why that distinction matters concretely here, not just as a disclaimer.

<details>
<summary>Confusion matrices, ROC curves, and feature importance (charts generated by <code>03_evaluation.ipynb</code>)</summary>

![Confusion Matrices](assets/confusion_matrices.png)
![ROC Curves](assets/roc_curves.png)
![Feature Importance](assets/feature_importance.png)

</details>

---

## Why Logistic Regression?

Precision and coefficients aside, Logistic Regression had the **highest Test F1 of the three outright** (98.63%, vs. 97.46% for Random Forest and 95.72% for Multinomial NB) — it didn't need the project's "simplest model within 1% F1" tie-break rule to win, it won on performance alone. On top of that:

- **~80x faster to train** than Random Forest (0.79s vs. 64.27s) and negligible inference latency.
- **Directly interpretable** — each TF-IDF feature has exactly one learned coefficient, so "why did the model say this" has a real, inspectable answer instead of a post-hoc approximation. This is what powers the app's explainability view.

---

## Dataset

**[ISOT Fake News Dataset](https://onlineacademiccommunity.uvic.ca/isot/)** — University of Victoria.

| | Count | Share |
|---|---|---|
| Total articles | 38,639 | 100% |
| Credible (`True.csv`) | 21,191 | 54.8% |
| Fake (`Fake.csv`) | 17,448 | 45.2% |

Credible articles are Reuters wire copy; Fake articles are drawn from a mix of sources flagged as unreliable/fabricated. No independent, non-ISOT validation set was used — the reported metrics are internal to this dataset (see below).

---

## Data Leakage Investigation

This project has a documented dataset-leakage issue that was found and mitigated during development — included here deliberately, not left for someone else to discover.

**Problem** — ISOT's "Credible" class is almost entirely Reuters wire copy; "Fake" comes from differently-formatted sources. A bag-of-words model has no concept of meaning, so TF-IDF + Logistic Regression initially learned to detect *source formatting* instead of *content*.

**How it was found** — by testing the model against a real, legitimately-reported non-Reuters article, which it confidently misclassified as Fake, then confirming the cause by inspecting the model's largest coefficients:

1. The literal word **"reuters"** — nearly every credible article's dateline (`WASHINGTON (Reuters) -`) made this word a near-perfect proxy for the label itself.
2. **Photo-caption artifacts** (`"via"`, `"image"`) — Fake.csv articles were scraped with embedded photo credits (e.g. `Image via Getty`) that Reuters copy never contains; at one point these were the two largest coefficients in the entire model.

**Mitigation** — both patterns are stripped inside `clean_text()`, defined once in `app/text_processing.py` and imported by both `02_feature_model.ipynb` (training) and `app/utils.py` (inference), so the fix can't drift out of sync between training and serving.

**Why it still matters** — there's a structural ceiling here: because the Credible class is essentially Reuters-only, some residual house-style signal (`said`, weekday names from datelines, `minister`, `government`) will always leak through TF-IDF regardless of blocklisting individual words. A genuinely complete fix needs a Credible dataset sourced from multiple outlets, which is outside this project's scope. In practice, this means the model likely generalises worse to non-Reuters credible sources than the test accuracy alone suggests.

---

## Limitations

- **Not a fact-checker.** The model has no access to real-world facts, sources, or events after its training data — it recognises *writing style and vocabulary patterns*, nothing more.
- **Confidence is model confidence, not factual certainty.** A "High Confidence" verdict means the input's style closely resembles one training class; it is not a certainty score about truth.
- **Domain-limited.** Trained and evaluated only on English-language political news; performance on other domains (sports, science, entertainment) or other languages is untested.
- **Source-composition limitation.** Per the leakage investigation above, the Credible class is essentially Reuters-only — the model has learned less about "credible writing" in general than about "Reuters house style" specifically, which is a narrower and more brittle signal.
- **No external validation.** All reported metrics are held-out performance on a split of the same ISOT dataset. No separate, independently-sourced test set has been evaluated.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.11 |
| Web app | Streamlit |
| ML | scikit-learn (TF-IDF, Logistic Regression, Multinomial NB, Random Forest) |
| NLP | NLTK (tokenisation, stopwords, lemmatisation) |
| Data | pandas, NumPy, SciPy |
| Model persistence | joblib |
| Notebook visualisation only | Matplotlib, Seaborn *(used in the notebooks to generate `assets/*.png`; not required to run the app itself)* |

---

## Project Structure

```
News_Credibility/
├── app/
│   ├── app.py                 # Streamlit entry point — page config, tab layout
│   ├── components.py          # UI components (forms, result cards, history, etc.)
│   ├── config.py               # Constants, copy, and the real evaluation metrics
│   ├── styles.py                # Custom CSS
│   ├── text_processing.py       # clean_text() — the single source of truth, shared with the training notebook
│   └── utils.py                  # Model/vectorizer loading, prediction, explainability
├── assets/
│   ├── confusion_matrices.png   # Generated by 03_evaluation.ipynb
│   ├── feature_importance.png
│   ├── roc_curves.png
│   └── screenshots/              # See Demo / Screenshots
├── data/
│   ├── Fake.csv                  # Raw ISOT data
│   ├── True.csv
│   └── processed/                 # cleaned.csv, train.csv, test.csv (gitignored — regenerated by the notebooks)
├── models/
│   ├── model.pkl                  # Trained Logistic Regression (final, full-dataset refit)
│   └── vectorizer.pkl              # Fitted TF-IDF vectorizer
├── notebooks/
│   ├── 01_eda_preprocessing.ipynb
│   ├── 02_feature_model.ipynb
│   └── 03_evaluation.ipynb
├── .streamlit/config.toml          # Theme + toolbar config for the deployed app
├── LICENSE
├── requirements.txt
└── README.md
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/dodiyariya6/News-Credibility-Analyser.git
cd News-Credibility-Analyser

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app/app.py
```

**Requirements:** Python 3.9+ (scikit-learn 1.6.1's minimum; developed and tested on 3.11). An internet connection is needed on first run so NLTK can download `punkt`, `stopwords`, and `wordnet` if they aren't already cached locally — this happens automatically. No environment variables or API keys are required.

---

## Reproducibility

`models/model.pkl` and `models/vectorizer.pkl` were trained with **scikit-learn 1.6.1** — `requirements.txt` pins this exact version (rather than a loose lower bound) because loading these specific artifacts with a materially newer scikit-learn triggers `InconsistentVersionWarning` and risks subtly different behavior. `joblib`, `numpy`, and `scipy` are pinned alongside it to versions verified to satisfy scikit-learn 1.6.1's own requirements and load these artifacts warning-free.

If you retrain the model with a different scikit-learn version, update this pin to match.

---

## Notebooks

| Notebook | What it does |
|---|---|
| `01_eda_preprocessing.ipynb` | Loads and merges `Fake.csv` + `True.csv`, drops label-leaking columns (`subject`, `date`), removes empty/duplicate articles, shuffles, and runs exploratory analysis (class balance, article length, top words, punctuation style) before saving `cleaned.csv`. |
| `02_feature_model.ipynb` | Applies `clean_text()` to the full dataset, splits into stratified train/test sets, fits a `TfidfVectorizer` on the training split only, transforms both splits, and saves `vectorizer.pkl` plus `train.csv`/`test.csv` for the next phase. |
| `03_evaluation.ipynb` | Trains and cross-validates all three candidate models, evaluates them on the held-out test set (accuracy, precision, recall, F1, ROC-AUC, confusion matrices, feature importance), selects the winner by Test F1, retrains that model on the full dataset, and saves the final `model.pkl`. |

All three are written for Google Colab (they mount Google Drive for file paths) but run the same in a local Jupyter environment with the paths adjusted.

**Retraining:** run the three notebooks in order, then copy the resulting `.pkl` files into `models/` and the regenerated `.png` charts into `assets/`, then update the metrics in `app/config.py`'s `MODEL_METRICS`/`DATASET_STATS` (and this README) to match. `clean_text()` lives in exactly one place (`app/text_processing.py`) and is imported by both the app and `02_feature_model.ipynb` — don't reintroduce a second copy of it.

---

## Future Scope

- Evaluate against an independently-sourced, non-ISOT test set to measure real generalisation rather than in-dataset held-out performance.
- Broaden the Credible class beyond Reuters to reduce the source-composition limitation described above.
- Probability calibration (e.g. Platt scaling) if confidence scores need to be interpreted as calibrated probabilities rather than relative rankings.
- Containerised or cloud deployment with the pinned environment from `requirements.txt`.

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Riya Dodiya.

This tool is built for educational and portfolio purposes. It is not a substitute for professional fact-checking — always verify news through trusted, independent sources.

---

## Author

**Riya Dodiya** — B.Tech, Artificial Intelligence & Machine Learning.
