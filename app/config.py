"""
config.py — Central constants and settings for News Credibility Analyser.
All paths, copy, and stats live here so the app can be reconfigured without
touching UI or logic code.
"""

import os

# ── Model Paths ──────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH      = os.path.join(BASE_DIR, "models", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")
ASSETS_DIR      = os.path.join(BASE_DIR, "assets")

# ── Labels ───────────────────────────────────────────────────────────────────
LABEL_MAP = {0: "Credible News", 1: "Fake News"}

# ── Confidence Tiers ─────────────────────────────────────────────────────────
TIER_HIGH_THRESHOLD     = 0.85   # >= this  -> High Confidence
TIER_MODERATE_THRESHOLD = 0.60   # >= this  -> Moderate Confidence
                                  # <  0.60  -> Uncertain

TIER_HIGH      = "High Confidence"
TIER_MODERATE  = "Moderate Confidence"
TIER_UNCERTAIN = "Uncertain"

# ── UI Copy ──────────────────────────────────────────────────────────────────
APP_TITLE       = "News Credibility Analyser"
APP_SUBTITLE    = "Classify news articles as Credible or Fake using Machine Learning"
APP_DESCRIPTION = (
    "Paste any news article below. The model will analyse the text and return "
    "a prediction along with a confidence score to help you gauge reliability."
)

DISCLAIMER = (
    "This tool is built for educational purposes as part of a portfolio project. "
    "It is not a substitute for professional fact-checking. Always verify news through "
    "trusted, independent sources."
)

DATASET_CREDIT = (
    "Dataset: ISOT Fake News Dataset — University of Victoria. "
    "38,639 real and fake articles sourced from Reuters and PolitiFact."
)

# ── Input Limits ─────────────────────────────────────────────────────────────
MIN_BODY_WORDS = 20  # warn user if article body is too short

# ── Real Evaluation Results (03_evaluation.ipynb) — exact notebook output ────
DATASET_STATS = {
    "total_articles": 38639,
    "credible_count": 21191,
    "fake_count": 17448,
    "train_size": 30911,
    "test_size": 7728,
    "vocab_size": 30000,
}

MODEL_METRICS = {
    "Logistic Regression": {
        "accuracy": 0.9864,
        "precision": 0.9869,
        "recall": 0.9857,
        "f1": 0.9863,
        "roc_auc": 0.9986,
        "cv_f1_mean": 0.9853,
        "cv_f1_std": 0.0010,
        "train_time_s": 0.79,
        "confusion_matrix": {"tn": 4209, "fp": 29, "fn": 76, "tp": 3414},
        "selected": True,
    },
    "Multinomial NB": {
        "accuracy": 0.9576,
        "precision": 0.9570,
        "recall": 0.9574,
        "f1": 0.9572,
        "roc_auc": 0.9905,
        "cv_f1_mean": 0.9577,
        "cv_f1_std": 0.0022,
        "train_time_s": 0.04,
        "confusion_matrix": {"tn": 4064, "fp": 174, "fn": 154, "tp": 3336},
        "selected": False,
    },
    "Random Forest": {
        "accuracy": 0.9749,
        "precision": 0.9758,
        "recall": 0.9736,
        "f1": 0.9746,
        "roc_auc": 0.9972,
        "cv_f1_mean": 0.9755,
        "cv_f1_std": 0.0013,
        "train_time_s": 64.27,
        "confusion_matrix": {"tn": 4183, "fp": 55, "fn": 139, "tp": 3351},
        "selected": False,
    },
}

SELECTED_MODEL_NAME = "Logistic Regression"
MODEL_SELECTION_RATIONALE = (
    "Logistic Regression had the highest Test F1 of the three (98.63%, vs. 97.46% "
    "for Random Forest and 95.72% for Multinomial NB) — so no simplicity tie-break "
    "was even needed. It also trains roughly 80x faster than Random Forest (0.79s "
    "vs. 64.27s) and its coefficients directly explain each prediction, making it "
    "the clear choice on both performance and interpretability."
)

# Static evaluation charts generated in 03_evaluation.ipynb — used as-is so
# figures always match the notebook exactly.
ASSET_CONFUSION_MATRICES = os.path.join(ASSETS_DIR, "confusion_matrices.png")
ASSET_FEATURE_IMPORTANCE = os.path.join(ASSETS_DIR, "feature_importance.png")
ASSET_ROC_CURVES         = os.path.join(ASSETS_DIR, "roc_curves.png")

# ── Sample Articles (for the "Try a sample" feature) ─────────────────────────
SAMPLE_FAKE_ARTICLE = {
    "title": "BREAKING: Secret Government Memo Reveals Shocking Plan You Won't Believe",
    "body": (
        "You won't believe what insiders are saying after this leaked memo surfaced "
        "online today. According to anonymous sources close to the situation, officials "
        "have been secretly planning something that mainstream media refuses to report. "
        "Share this before it gets taken down! Wake up, America — the truth is finally "
        "coming out and they don't want you to know about it. Multiple patriots online "
        "are calling this the biggest cover-up of the decade, and the silence from "
        "official channels only proves they are hiding something huge."
    ),
}

SAMPLE_CREDIBLE_ARTICLE = {
    "title": "Senate Committee Advances Infrastructure Funding Bill After Bipartisan Vote",
    "body": (
        "WASHINGTON (Reuters) - The Senate Appropriations Committee voted 21-9 on "
        "Wednesday to advance a $1.2 billion infrastructure funding bill, sending the "
        "measure to the full chamber for consideration. The bill, which allocates funds "
        "for bridge repairs and public transit upgrades across 14 states, received "
        "support from members of both parties following weeks of negotiation. "
        "Committee chairwoman said in a statement that the bill reflects a compromise "
        "reached after input from state transportation officials. The legislation is "
        "expected to reach the Senate floor for a full vote next month."
    ),
}

# ── Home Page Copy ────────────────────────────────────────────────────────────
HERO_EYEBROW = "AI · NLP · Machine Learning"
HERO_HEADLINE_MAIN = "Analyse News Credibility"
HERO_HEADLINE_ITALIC = "Using NLP & Machine Learning"
HERO_SUBTEXT = (
    "An NLP classifier that reads any news article and tells you whether it looks "
    "credible or fabricated — trained on 38,639 real-world articles, built end to end "
    "with TF-IDF and Logistic Regression."
)

HOME_STATS = [
    {"value": "38.6k+", "label": "Articles in Training Set"},
    {"value": "3", "label": "Models Compared"},
    {"value": "98.64%", "label": "Final Model Accuracy"},
    {"value": "30k", "label": "TF-IDF Features"},
]

# Feature cards shown under "What This App Does" on the Home page
HOME_FEATURES = [
    {
        "kicker": "01 — Analyse News",
        "title": "Instant credibility check",
        "detail": (
            "Paste any headline and article body. The model returns a verdict, "
            "a confidence score, and a full probability breakdown in under a "
            "second."
        ),
    },
    {
        "kicker": "02 — Model Insights",
        "title": "Full evaluation, transparently shown",
        "detail": (
            f"See exactly how {SELECTED_MODEL_NAME} was chosen — accuracy, "
            "precision, recall, F1, ROC-AUC, confusion matrices, and the "
            "actual learned feature importances, compared across all three "
            "models that were trained."
        ),
    },
    {
        "kicker": "03 — About",
        "title": "The full pipeline, explained",
        "detail": (
            "From raw ISOT dataset to deployed model — preprocessing, TF-IDF "
            "feature extraction, model comparison, and selection criteria, "
            "laid out step by step."
        ),
    },
]

# ── About Page Copy ───────────────────────────────────────────────────────────
PIPELINE_STEPS = [
    {
        "step": "01",
        "title": "Data Collection & Cleaning",
        "detail": (
            "The ISOT Fake News Dataset (38,639 articles from Reuters and PolitiFact) "
            "was loaded, deduplicated, and checked for class balance across Credible "
            "and Fake labels."
        ),
    },
    {
        "step": "02",
        "title": "Text Preprocessing",
        "detail": (
            "Lowercasing, URL and HTML stripping, digit normalisation, punctuation "
            "removal, tokenisation, stopword removal (preserving negations like "
            "'not' and 'never'), and lemmatisation — applied identically at train "
            "and inference time."
        ),
    },
    {
        "step": "03",
        "title": "Feature Extraction — TF-IDF",
        "detail": (
            "Text converted into 30,000-dimensional TF-IDF vectors using unigrams "
            "and bigrams, capturing both individual keywords and two-word phrases "
            "that are statistically significant predictors."
        ),
    },
    {
        "step": "04",
        "title": "Model Training & Comparison",
        "detail": (
            "Logistic Regression, Multinomial Naive Bayes, and Random Forest were "
            "trained and evaluated with 5-fold stratified cross-validation on "
            "30,915 training articles."
        ),
    },
    {
        "step": "05",
        "title": "Model Selection",
        "detail": (
            "Logistic Regression was selected using an F1-first, simplicity-second "
            "rule, then retrained on the full 38,639-article dataset before being "
            "saved as the deployed model."
        ),
    },
]

# Raw data files behind the project — shown in the About page workflow section
DATA_SOURCES = [
    {
        "file": "data/Fake.csv",
        "detail": "Fabricated / unreliable articles from the ISOT dataset.",
    },
    {
        "file": "data/True.csv",
        "detail": "Verified Reuters articles from the ISOT dataset.",
    },
    {
        "file": "data/processed/",
        "detail": "Cleaned, preprocessed text saved out of 01_eda_preprocessing.ipynb.",
    },
]

# Notebooks that produced the deployed model — shown in the About page so the
# workflow reads as a real ML project, not just a downloaded model + UI.
NOTEBOOKS = [
    {
        "file": "01_eda_preprocessing.ipynb",
        "title": "Exploratory Data Analysis & Preprocessing",
        "items": [
            "Dataset loading and merging (Fake.csv + True.csv)",
            "Deduplication and class-balance validation",
            "Text cleaning: lowercasing, URL/HTML stripping, punctuation removal",
            "Tokenisation, stopword removal, and lemmatisation",
        ],
    },
    {
        "file": "02_feature_model.ipynb",
        "title": "Feature Engineering & Model Training",
        "items": [
            "TF-IDF vectorisation (unigrams + bigrams, 30,000 features)",
            "Stratified train/test split (30,915 / 7,729 articles)",
            "Training Logistic Regression, Multinomial NB, and Random Forest",
            "5-fold cross-validation and model comparison",
        ],
    },
    {
        "file": "03_evaluation.ipynb",
        "title": "Evaluation & Model Selection",
        "items": [
            "Confusion matrices for all three models",
            "ROC curves and AUC comparison",
            "Feature importance / coefficient analysis",
            "Final model selection and export to models/",
        ],
    },
]

TECH_STACK = [
    "Python", "scikit-learn", "NLTK", "pandas", "NumPy",
    "Streamlit", "TF-IDF", "Logistic Regression", "Joblib",
]

# Reflects the actual repository layout (see NOTEBOOKS / DATA_SOURCES above)
FOLDER_STRUCTURE = """project/
├── app/
│   ├── app.py                  ← Home page
│   ├── config.py                ← Constants, copy, real metrics
│   ├── components.py            ← Reusable UI components
│   ├── styles.py                ← Theme (CSS)
│   ├── text_processing.py       ← Shared clean_text() (used by training notebook too)
│   └── utils.py                 ← Model loading + prediction pipeline
├── data/
│   ├── Fake.csv
│   ├── True.csv
│   └── processed/
├── models/
│   ├── model.pkl                ← Trained Logistic Regression
│   └── vectorizer.pkl           ← Fitted TF-IDF vectorizer
├── notebooks/
│   ├── 01_eda_preprocessing.ipynb
│   ├── 02_feature_model.ipynb
│   └── 03_evaluation.ipynb
├── assets/
│   ├── confusion_matrices.png
│   ├── feature_importance.png
│   └── roc_curves.png
└── requirements.txt"""
