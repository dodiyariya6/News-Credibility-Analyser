"""
utils.py — Preprocessing, model loading, and prediction logic.
All ML-related operations live here, separate from the UI layer.
"""

import re
import string
import joblib
import streamlit as st

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from config import (
    MODEL_PATH, VECTORIZER_PATH,
    LABEL_MAP,
    TIER_HIGH_THRESHOLD, TIER_MODERATE_THRESHOLD,
    TIER_HIGH, TIER_MODERATE, TIER_UNCERTAIN,
)


def _ensure_nltk_resources() -> None:
    """Downloads required NLTK data only if it isn't already present."""
    resources = [
        ("tokenizers/punkt",     "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords",    "stopwords"),
        ("corpora/wordnet",      "wordnet"),
    ]
    for path, pkg in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)

_ensure_nltk_resources()

_STOP_WORDS = set(stopwords.words("english"))

# Negations carry meaning for this task — keep them during stopword removal.
_NEGATIONS = {"not", "no", "never", "without", "neither", "nor"}
_FILTERED_STOPS = _STOP_WORDS - _NEGATIONS

_lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Replicates the exact preprocessing pipeline used at training time
    (01_eda_preprocessing.ipynb). Step order must stay identical to training
    to avoid a feature mismatch at inference.

    Steps: lowercase -> strip Reuters dateline leak -> strip URLs -> strip HTML ->
    replace digits -> remove punctuation -> tokenise -> remove stopwords
    (keep negations) -> lemmatise.
    """
    text = text.lower()

    # Strip Reuters wire-service dateline leak (e.g. "washington (reuters) -").
    # Nearly all True.csv articles open with this; Fake.csv almost never
    # contains it, so left in, "reuters" becomes a near-perfect label proxy
    # instead of the model learning genuine credibility signals. Must match
    # the identical fix applied in 02_feature_model.ipynb's clean_text(), or
    # inference will diverge from what the model was actually trained on.
    text = re.sub(r"^.*?\(reuters\)\s*-\s*", "", text)
    text = re.sub(r"\breuters\b", "", text)

    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\d+", " NUM ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))

    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in _FILTERED_STOPS]
    tokens = [_lemmatizer.lemmatize(t) for t in tokens]

    return " ".join(tokens)


@st.cache_resource(show_spinner=False)
def load_model():
    """Loads the trained model from disk. Cached for the session lifetime."""
    return joblib.load(MODEL_PATH)


@st.cache_resource(show_spinner=False)
def load_vectorizer():
    """Loads the TF-IDF vectorizer from disk. Cached for the session lifetime."""
    return joblib.load(VECTORIZER_PATH)


def get_confidence_tier(prob: float) -> str:
    """Maps a raw probability (predict_proba for class 1 / Fake) to a tier label."""
    if prob >= TIER_HIGH_THRESHOLD:
        return TIER_HIGH
    elif prob >= TIER_MODERATE_THRESHOLD:
        return TIER_MODERATE
    else:
        return TIER_UNCERTAIN


def predict(title: str, body: str) -> dict:
    """
    Full prediction pipeline: preprocess -> vectorise -> predict.

    Returns:
        dict with keys: label, is_fake, fake_prob, confidence, tier.
    """
    model      = load_model()
    vectorizer = load_vectorizer()

    raw_text       = f"{title} {body}"
    processed_text = clean_text(raw_text)

    X = vectorizer.transform([processed_text])

    pred_label = model.predict(X)[0]
    proba      = model.predict_proba(X)[0]  # [p_credible, p_fake]
    fake_prob  = float(proba[1])
    confidence = float(max(proba))

    return {
        "label"      : LABEL_MAP[pred_label],
        "is_fake"    : bool(pred_label == 1),
        "fake_prob"  : fake_prob,
        "confidence" : confidence,
        "tier"       : get_confidence_tier(confidence),
    }


def get_top_terms(title: str, body: str, top_n: int = 8) -> dict:
    """
    Lightweight explainability without SHAP: intersects the terms present in
    the user's cleaned input with the trained Logistic Regression's learned
    coefficients, returning the strongest fake- and credible-pushing terms
    found in this specific article.

    Returns:
        dict with 'fake_terms' and 'credible_terms', each a list of
        (term, coefficient) tuples sorted by strength.
    """
    model      = load_model()
    vectorizer = load_vectorizer()

    raw_text       = f"{title} {body}"
    processed_text = clean_text(raw_text)

    X = vectorizer.transform([processed_text])
    nonzero_idx = X.nonzero()[1]

    if len(nonzero_idx) == 0 or not hasattr(model, "coef_"):
        return {"fake_terms": [], "credible_terms": []}

    feature_names = vectorizer.get_feature_names_out()
    coefficients  = model.coef_[0]

    present_terms = [(feature_names[i], coefficients[i]) for i in nonzero_idx]

    fake_terms     = sorted((t for t in present_terms if t[1] > 0), key=lambda t: -t[1])[:top_n]
    credible_terms = sorted((t for t in present_terms if t[1] < 0), key=lambda t: t[1])[:top_n]

    return {"fake_terms": fake_terms, "credible_terms": credible_terms}


def highlight_text(text: str, fake_terms: list, credible_terms: list) -> str:
    """
    Returns an HTML-escaped version of the raw article text with words/phrases
    that match the model's top contributing terms wrapped in highlight spans.

    Matching works by lemmatizing each word in the raw text the same way as
    clean_text() and comparing it against the (already-lemmatized) terms
    returned by get_top_terms() — so the *original* text is displayed, only
    the matching words get a background color. Adjacent word pairs are also
    checked so bigram features (e.g. "washington reuters") get highlighted
    as a single phrase.

    This is purely presentational — it does not touch the model or the
    prediction pipeline.
    """
    import html as html_lib

    fake_set = {t.lower() for t, _ in fake_terms}
    credible_set = {t.lower() for t, _ in credible_terms}
    if not fake_set and not credible_set:
        return html_lib.escape(text)

    text = text.replace("\r\n", "\n")
    pieces = re.findall(r"\S+|\s+", text)

    def lemma_of(word: str) -> str:
        w = word.lower().translate(str.maketrans("", "", string.punctuation))
        return _lemmatizer.lemmatize(w) if w else ""

    lemmas = [lemma_of(p) if p.strip() else "" for p in pieces]

    n = len(pieces)
    out = []
    i = 0
    while i < n:
        piece = pieces[i]

        # Whitespace: keep, but strip literal newlines so the caller's
        # render_html() (which joins stripped lines) can't merge words
        # together — visual line breaks are handled by CSS white-space instead.
        if not piece.strip():
            out.append(piece.replace("\n", " "))
            i += 1
            continue

        # Try a two-word (bigram) match first.
        j = i + 1
        while j < n and not pieces[j].strip():
            j += 1
        if j < n and lemmas[i] and lemmas[j]:
            bigram = f"{lemmas[i]} {lemmas[j]}"
            if bigram in fake_set or bigram in credible_set:
                css_class = "highlight-fake" if bigram in fake_set else "highlight-credible"
                segment = "".join(pieces[i:j + 1]).replace("\n", " ")
                out.append(f'<span class="{css_class}">{html_lib.escape(segment)}</span>')
                i = j + 1
                continue

        # Single-word match.
        if lemmas[i] in fake_set:
            out.append(f'<span class="highlight-fake">{html_lib.escape(piece)}</span>')
        elif lemmas[i] in credible_set:
            out.append(f'<span class="highlight-credible">{html_lib.escape(piece)}</span>')
        else:
            out.append(html_lib.escape(piece))
        i += 1

    return "".join(out)


def generate_report(title: str, result: dict, top_terms: dict) -> str:
    """
    Builds a plain-text analysis report for a single prediction, suitable for
    st.download_button. Kept as .txt (not PDF) since it needs no extra
    dependencies and opens reliably anywhere.
    """
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fake_terms = top_terms.get("fake_terms", [])
    credible_terms = top_terms.get("credible_terms", [])

    lines = [
        "NEWS CREDIBILITY ANALYSER — ANALYSIS REPORT",
        "=" * 44,
        f"Generated: {timestamp}",
        "",
        f"Article Title: {title if title else '(untitled article)'}",
        "",
        "VERDICT",
        "-" * 44,
        f"Prediction:            {result['label']}",
        f"Confidence:            {result['confidence'] * 100:.1f}% ({result['tier']})",
        f"Fake Probability:      {result['fake_prob'] * 100:.1f}%",
        f"Credible Probability:  {(1 - result['fake_prob']) * 100:.1f}%",
        "",
        "TOP CONTRIBUTING TERMS",
        "-" * 44,
    ]

    if fake_terms:
        lines.append("Pushed toward Fake:")
        lines.extend(f"  - {term} ({coef:+.3f})" for term, coef in fake_terms)
    else:
        lines.append("Pushed toward Fake: none found")

    lines.append("")

    if credible_terms:
        lines.append("Pushed toward Credible:")
        lines.extend(f"  - {term} ({coef:+.3f})" for term, coef in credible_terms)
    else:
        lines.append("Pushed toward Credible: none found")

    lines += [
        "",
        "-" * 44,
        "Generated by News Credibility Analyser — an educational NLP/ML",
        "portfolio project. Not a substitute for professional fact-checking.",
    ]

    return "\n".join(lines)


# Prediction history is kept in Streamlit session_state — no database needed.
HISTORY_KEY = "prediction_history"


def add_to_history(title: str, result: dict) -> None:
    """Appends a prediction to session-state history (most recent first, capped at 10)."""
    import datetime

    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []

    entry = {
        "title": title if title else "(untitled article)",
        "label": result["label"],
        "is_fake": result["is_fake"],
        "confidence": result["confidence"],
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
    }
    st.session_state[HISTORY_KEY].insert(0, entry)
    st.session_state[HISTORY_KEY] = st.session_state[HISTORY_KEY][:10]


def get_history() -> list:
    return st.session_state.get(HISTORY_KEY, [])


def clear_history() -> None:
    st.session_state[HISTORY_KEY] = []