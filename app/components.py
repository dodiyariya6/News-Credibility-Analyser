"""
components.py — Reusable Streamlit UI components.
Each function renders one visual section. Pages in app.py call these in order.
"""

import html

import streamlit as st
from config import (
    DISCLAIMER, DATASET_CREDIT,
    TIER_HIGH, TIER_MODERATE, TIER_UNCERTAIN,
    MIN_BODY_WORDS,
    DATA_SOURCES, NOTEBOOKS,
)
from utils import get_history, clear_history, highlight_text, generate_report


def render_html(html: str) -> None:
    """
    Render an HTML fragment via st.markdown.

    Streamlit's markdown parser treats any line indented 4+ spaces as a code
    block. Every HTML fragment here is naturally indented (it lives inside a
    Python function), so each line is stripped before rendering to avoid
    Streamlit printing literal "<div class=...>" text instead of parsing it.
    """
    st.markdown(
        "".join(line.strip() for line in html.strip().splitlines()),
        unsafe_allow_html=True,
    )


def render_top_nav() -> None:
    render_html("""
        <div class="top-nav fade-in">
            <div class="top-nav-logo">news<span>credible</span></div>
        </div>
    """)


def render_sample_buttons() -> tuple[bool, bool]:
    """Renders the 'Try fake sample' / 'Try credible sample' buttons."""
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        fake_clicked = st.button("Try a Fake-style Sample", use_container_width=True)
    with col2:
        credible_clicked = st.button("Try a Credible-style Sample", use_container_width=True)
    return fake_clicked, credible_clicked


def render_input_form() -> tuple[str, str, bool]:
    """
    Renders the title + body inputs and the Analyse button.

    Returns:
        (title, body, submitted)
    """

    render_html('<div class="section-label">Article Input</div>')

    title = st.text_input(
        label="Article Title",
        placeholder="Paste the article headline here…",
        help="Enter the full headline or title of the article.",
        key="input_title",
    )

    body = st.text_area(
        label="Article Body",
        placeholder="Paste the full article text here…",
        height=220,
        help=f"Enter at least {MIN_BODY_WORDS} words for a reliable prediction.",
        key="input_body",
    )

    col_btn, col_clear = st.columns([3, 1])

    with col_btn:
        submitted = st.button(
            "Analyse Article",
            use_container_width=True,
            type="primary"
        )

    with col_clear:
        cleared = st.button(
            "Clear",
            use_container_width=True
        )

    # Clear inputs safely
    if cleared:
        st.session_state.pop("input_title", None)
        st.session_state.pop("input_body", None)
        st.rerun()

    return title.strip(), body.strip(), submitted

def render_tips_card() -> None:
    """Fills the space beside the input form with guidance — presentation only."""
    render_html("""
        <div class="tips-card fade-in">
            <div class="tips-card-title">Tips for a reliable result</div>
            <ul class="tips-list">
                <li>Paste the real headline, not a paraphrase</li>
                <li>Include the full article body — at least a few paragraphs</li>
                <li>English-language political / news-style text works best</li>
                <li>Very short snippets often land in "Uncertain"</li>
            </ul>
        </div>
    """)


def validate_inputs(title: str, body: str) -> bool:
    """Checks for empty fields and minimum body length; shows inline messages."""
    if not title and not body:
        st.error("Please enter both a title and the article body.")
        return False

    if not title:
        st.error("Article title is required.")
        return False

    if not body:
        st.error("Article body is required.")
        return False

    word_count = len(body.split())
    if word_count < MIN_BODY_WORDS:
        st.warning(
            f"The article body is very short ({word_count} words). "
            f"For reliable results, please enter at least {MIN_BODY_WORDS} words."
        )
        # Not a hard block — allow submission with a warning.

    return True


def render_results(result: dict) -> None:
    """Renders the verdict card, confidence card, progress bar, and probabilities."""
    is_fake    = result["is_fake"]
    label      = result["label"]
    confidence = result["confidence"]
    fake_prob  = result["fake_prob"]
    tier       = result["tier"]

    st.markdown("---")
    render_html('<div class="section-label">Analysis Results</div>')

    col_verdict, col_confidence = st.columns(2, gap="medium")

    with col_verdict:
        verdict_class = "card-fake" if is_fake else "card-credible"
        verdict_icon  = "!" if is_fake else "✓"
        render_html(f"""
            <div class="result-card {verdict_class} fade-in">
                <div class="card-eyebrow">Verdict</div>
                <div class="card-icon-wrap"><strong>{verdict_icon}</strong></div>
                <div class="card-label">{label}</div>
            </div>
        """)

    with col_confidence:
        tier_class = {
            TIER_HIGH     : "tier-high",
            TIER_MODERATE : "tier-moderate",
            TIER_UNCERTAIN: "tier-uncertain",
        }.get(tier, "tier-uncertain")

        render_html(f"""
            <div class="result-card confidence-card fade-in fade-in-delay-1">
                <div class="card-eyebrow">Model Confidence</div>
                <div class="confidence-value">{confidence * 100:.1f}%</div>
                <div class="tier-badge {tier_class}">{tier}</div>
            </div>
        """)

    render_html(f'<p class="progress-label">Confidence Level — {confidence * 100:.1f}%</p>')
    st.progress(confidence)

    prob_col1, prob_col2 = st.columns(2, gap="medium")

    with prob_col1:
        render_html(f"""
            <div class="prob-card fade-in fade-in-delay-2">
                <div class="prob-label">Fake Probability</div>
                <div class="prob-value fake-prob">{fake_prob * 100:.1f}%</div>
            </div>
        """)

    with prob_col2:
        credible_prob = 1 - fake_prob
        render_html(f"""
            <div class="prob-card fade-in fade-in-delay-2">
                <div class="prob-label">Credible Probability</div>
                <div class="prob-value credible-prob">{credible_prob * 100:.1f}%</div>
            </div>
        """)

    if tier == TIER_UNCERTAIN:
        render_html("""
            <div class="uncertain-warning fade-in">
                <strong>Low Confidence Prediction</strong><br>
                The model is uncertain about this article. This can happen with
                short texts, mixed signals, or topics underrepresented in training data.
                Please cross-check this article using trusted, independent fact-checking
                sources before drawing conclusions.
            </div>
        """)


def render_explanation(top_terms: dict) -> None:
    """Shows the terms from this article that most influenced the prediction."""
    fake_terms     = top_terms.get("fake_terms", [])
    credible_terms = top_terms.get("credible_terms", [])

    if not fake_terms and not credible_terms:
        return

    st.markdown("---")
    render_html('<div class="section-label">Why This Prediction</div>')
    st.caption(
        "Terms found in this article that most influenced the model — drawn "
        "directly from the trained Logistic Regression coefficients."
    )

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("**Pushed toward Fake**")
        if fake_terms:
            chips = "".join(
                f'<span class="term-chip term-chip-fake">{term}</span>'
                for term, _ in fake_terms
            )
            render_html(f'<div class="fade-in">{chips}</div>')
        else:
            st.caption("No strong fake-associated terms found.")

    with col2:
        st.markdown("**Pushed toward Credible**")
        if credible_terms:
            chips = "".join(
                f'<span class="term-chip term-chip-credible">{term}</span>'
                for term, _ in credible_terms
            )
            render_html(f'<div class="fade-in">{chips}</div>')
        else:
            st.caption("No strong credible-associated terms found.")


def render_highlighted_article(title: str, body: str, top_terms: dict) -> None:
    """Shows the pasted article with fake/credible-pushing terms highlighted in place."""
    fake_terms     = top_terms.get("fake_terms", [])
    credible_terms = top_terms.get("credible_terms", [])

    if not fake_terms and not credible_terms:
        return

    st.markdown("---")
    render_html('<div class="section-label">Highlighted Article</div>')
    st.caption(
        "The same terms shown as chips above, highlighted directly in your "
        "article — so you can see exactly where each signal came from."
    )

    highlighted_title = highlight_text(title, fake_terms, credible_terms) if title else ""
    highlighted_body  = highlight_text(body, fake_terms, credible_terms)

    title_html = (
        f'<div class="highlighted-article-title">{highlighted_title}</div>'
        if highlighted_title else ""
    )

    render_html(f"""
        <div class="uicard fade-in">
            {title_html}
            <div class="highlighted-article-body">{highlighted_body}</div>
        </div>
    """)

    render_html("""
        <div class="highlight-legend fade-in">
            <span class="legend-item"><span class="legend-swatch legend-fake"></span>Pushed toward Fake</span>
            <span class="legend-item"><span class="legend-swatch legend-credible"></span>Pushed toward Credible</span>
        </div>
    """)


def render_download_report(title: str, result: dict, top_terms: dict) -> None:
    """Lets the user download a plain-text summary of this prediction."""
    st.markdown("---")
    render_html('<div class="section-label">Download Report</div>')

    render_html("""
        <div class="report-card fade-in">
            <div class="report-card-text">
                Save this verdict, confidence score, and contributing terms as a
                text file — useful for attaching to an assignment or portfolio write-up.
            </div>
        </div>
    """)

    report_text = generate_report(title, result, top_terms)
    safe_title  = "".join(c if c.isalnum() else "_" for c in (title or "article"))[:40]

    st.download_button(
        label="Download Analysis Report (.txt)",
        data=report_text,
        file_name=f"credibility_report_{safe_title}.txt",
        mime="text/plain",
        use_container_width=True,
    )


def render_history() -> None:
    history = get_history()

    st.markdown("---")
    render_html('<div class="section-label">Prediction History (this session)</div>')

    if not history:
        st.caption("No predictions yet. Analyse an article to see it appear here.")
        return

    for entry in history:
        badge_color = "var(--danger)" if entry["is_fake"] else "var(--credible)"
        badge_bg    = "var(--danger-soft)" if entry["is_fake"] else "var(--credible-soft)"
        # entry["title"] is raw user input (the article title the visitor
        # typed) — it must be HTML-escaped before going into unsafe_allow_html
        # markup, or a pasted title like "<img src=x onerror=...>" would
        # execute as live HTML/JS instead of rendering as text.
        safe_title = html.escape(entry["title"])
        render_html(f"""
            <div class="history-item fade-in">
                <div>
                    <div class="history-title">{safe_title}</div>
                    <div class="history-meta">{entry['timestamp']}</div>
                </div>
                <div class="history-badge" style="background:{badge_bg}; color:{badge_color};">
                    {entry['label']} · {entry['confidence']*100:.0f}%
                </div>
            </div>
        """)

    if st.button("Clear History", use_container_width=False):
        clear_history()
        st.rerun()


def render_about() -> None:
    """Collapsed model explainer shown at the bottom of the Analyse page."""
    st.markdown("---")
    with st.expander("About This Model", expanded=False):
        st.markdown(
            """
            ### How It Works

            **Dataset**
            Trained on the [ISOT Fake News Dataset](https://onlineacademiccommunity.uvic.ca/isot/)
            (38,639 articles). Credible articles come from Reuters; Fake articles come
            from PolitiFact and other flagged sources.

            **Feature Extraction — TF-IDF**
            Each article is converted into a numerical vector using
            **TF-IDF (Term Frequency–Inverse Document Frequency)** with unigrams and bigrams
            (30,000 features). This captures both individual keywords and
            two-word phrases that are statistically significant predictors.

            **Model — Logistic Regression**
            Selected after comparing Logistic Regression, Multinomial Naive Bayes, and
            Random Forest. Logistic Regression was chosen for its combination of high F1
            score, fast inference, and interpretability — its learned coefficients directly
            reveal which words most strongly push toward Fake or Credible.

            **Confidence Tiers**

            | Probability | Tier                   | Meaning                              |
            |-------------|------------------------|---------------------------------------|
            | ≥ 85%       | High Confidence        | Result is reliable                   |
            | 60–85%      | Moderate Confidence    | Likely correct, treat with caution   |
            | < 60%       | Uncertain              | Verify manually                      |

            **Limitations**
            This model is trained on English-language political news. It may not generalise
            well to other domains (science, sports, entertainment) or non-English text.
            """
        )


def render_data_sources() -> None:
    """About page — the raw data files behind the project."""
    render_html('<div class="section-label">Data Sources</div>')
    items_html = "".join(
        f"""
        <div class="data-source-item fade-in">
            <div class="data-source-file">{d['file']}</div>
            <div class="data-source-detail">{d['detail']}</div>
        </div>
        """
        for d in DATA_SOURCES
    )
    render_html(f'<div class="uicard">{items_html}</div>')


def render_notebooks() -> None:
    """About page — the notebooks that produced the deployed model."""
    render_html('<div class="section-label">Notebooks</div>')
    for nb in NOTEBOOKS:
        list_items = "".join(f"<li>{item}</li>" for item in nb["items"])
        render_html(f"""
            <div class="notebook-card fade-in">
                <div class="notebook-file">{nb['file']}</div>
                <div class="notebook-title">{nb['title']}</div>
                <ul class="notebook-list">{list_items}</ul>
            </div>
        """)


def render_footer() -> None:
    render_html(f"""
        <div class="footer-block">
            <div class="footer-grid">
                <div class="footer-col">
                    <div class="footer-col-title">Dataset</div>
                    <div class="footer-col-text">{DATASET_CREDIT}</div>
                </div>
                <div class="footer-col">
                    <div class="footer-col-title">Technology</div>
                    <div class="footer-col-text">Python · Scikit-Learn · NLTK · TF-IDF · Streamlit</div>
                </div>
                <div class="footer-col">
                    <div class="footer-col-title">Disclaimer</div>
                    <div class="footer-col-text">{DISCLAIMER}</div>
                </div>
            </div>
        </div>
    """)