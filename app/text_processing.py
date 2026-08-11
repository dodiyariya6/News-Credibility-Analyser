"""
text_processing.py — Single source of truth for the text-cleaning pipeline
used both to train the model (notebooks/02_feature_model.ipynb) and to run
inference (app/utils.py).

Previously clean_text() was hand-copied into both places, and the copies
had quietly drifted (the app stripped only ASCII punctuation via
string.punctuation, while the notebook stripped all non-word Unicode
punctuation via regex; the app also padded the NUM digit-placeholder with
spaces while the notebook did not) — so articles containing smart
quotes/em-dashes or digits glued to letters were vectorised differently at
inference time than the vocabulary the model was actually trained on.

Importing clean_text() from this one module in both places — instead of
maintaining two copies by hand — is what guarantees inference always sees
the exact same feature space the model was trained on.
"""

import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def ensure_nltk_resources() -> None:
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


ensure_nltk_resources()

# Negations carry meaning for this task — keep them during stopword removal.
NEGATIONS = {"not", "no", "never", "without", "neither", "nor"}

# Build custom stopword list: standard English list minus the negations above.
STOP_WORDS = set(stopwords.words("english")) - NEGATIONS

# Single shared lemmatizer instance (creating one per call is expensive).
lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Full preprocessing pipeline applied to a single string. Step order must
    stay identical to training to avoid a feature mismatch at inference.

    Steps (in order):
        1. Lowercase
        2. Strip Reuters wire-service dateline / source-name leak
        3. Remove URLs
        4. Remove HTML tags
        5. Replace digit sequences with a NUM token
        6. Remove punctuation
        7. Collapse multiple spaces
        8. Tokenize
        9. Remove stopwords (keeping negations)
        10. Lemmatize
        11. Rejoin into a single string
    """
    # 1. Lowercase
    text = text.lower()

    # 2. Strip Reuters wire-service dateline leak.
    #    Nearly every True.csv article opens with a dateline like
    #    "washington (reuters) -" / "london (reuters) -" and Fake.csv
    #    articles almost never contain this. Left in, the literal word
    #    "reuters" becomes a near-perfect proxy for the label instead of
    #    the model learning genuine credibility signals. Strip the dateline
    #    phrase, then remove any remaining standalone "reuters" mentions.
    text = re.sub(r"^.*?\(reuters\)\s*-\s*", "", text)
    text = re.sub(r"\breuters\b", "", text)

    # 3. Remove URLs (http/https and bare www addresses)
    text = re.sub(r"http\S+|www\S+", "", text)

    # 4. Remove HTML tags
    text = re.sub(r"<.*?>", "", text)

    # 5. Replace digit sequences with a placeholder token.
    #    Preserves the information that a number appeared without
    #    memorising values.
    text = re.sub(r"\d+", "NUM", text)

    # 6. Remove punctuation — keep only word characters and whitespace.
    #    Unicode-aware (\w), so smart quotes/em-dashes are stripped too,
    #    not just ASCII punctuation.
    text = re.sub(r"[^\w\s]", "", text)

    # 7. Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    # 8. Tokenize
    tokens = word_tokenize(text)

    # 9. Remove stopwords; preserve negation words defined in NEGATIONS
    tokens = [t for t in tokens if t not in STOP_WORDS]

    # 10. Lemmatize each token
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    # 11. Rejoin
    return " ".join(tokens)
