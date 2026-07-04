"""
app.py — Single-page Streamlit entry point for News Credibility Analyser.

Single page with a brand strip + st.tabs() for navigation, rather than a
native Streamlit multipage app with an auto-generated sidebar. The
prediction pipeline (utils.predict) and evaluation numbers are unchanged —
only presentation changed.

NOTE: if a pages/ directory exists next to this file, delete or rename it —
Streamlit auto-detects it and renders its own sidebar nav regardless of what
this file does.
"""

import os
import streamlit as st
import pandas as pd

# Must be the very first Streamlit call.
st.set_page_config(
    page_title="News Credibility Analyser",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from styles import CSS
from components import (
    render_html,
    render_top_nav,
    render_input_form,
    render_sample_buttons,
    render_tips_card,
    validate_inputs,
    render_results,
    render_explanation,
    render_highlighted_article,
    render_download_report,
    render_history,
    render_about,
    render_data_sources,
    render_notebooks,
    render_footer,
)
from utils import predict, get_top_terms, add_to_history
from config import (
    HERO_HEADLINE_MAIN, HERO_HEADLINE_ITALIC, HERO_SUBTEXT,
    HOME_STATS, HOME_FEATURES, DATASET_STATS, SELECTED_MODEL_NAME,
    SAMPLE_FAKE_ARTICLE, SAMPLE_CREDIBLE_ARTICLE,
    MODEL_METRICS, MODEL_SELECTION_RATIONALE,
    ASSET_CONFUSION_MATRICES, ASSET_FEATURE_IMPORTANCE, ASSET_ROC_CURVES,
    PIPELINE_STEPS, TECH_STACK, FOLDER_STRUCTURE,
    DATASET_CREDIT,
)


# ═════════════════════════════════════════════════════════════════════════
# HOME
# ═════════════════════════════════════════════════════════════════════════
def render_home() -> None:
    render_html(f"""
        <div class="header-block centered fade-in">
            <h1 class="header-title">
                {HERO_HEADLINE_MAIN}
                <span class="accent">{HERO_HEADLINE_ITALIC}</span>
            </h1>
            <p class="header-description" style="max-width:640px;">{HERO_SUBTEXT}</p>
        </div>
    """)

    stat_html = "".join(
        f'<div class="stat-item"><div class="stat-value">{s["value"]}</div>'
        f'<div class="stat-label">{s["label"]}</div></div>'
        for s in HOME_STATS
    )
    render_html(f'<div class="stat-row fade-in fade-in-delay-1">{stat_html}</div>')

    render_html('<div class="section-label">What This App Does</div>')

    for f in HOME_FEATURES:
        render_html(f"""
            <div class="feature-card fade-in">
                <div class="feature-kicker">{f['kicker']}</div>
                <div class="feature-title">{f['title']}</div>
                <div class="feature-detail">{f['detail']}</div>
            </div>
        """)

    render_html(f"""
        <div class="uicard uicard-dark fade-in" style="text-align:center; padding:2.4rem 1.5rem; margin-top:0.5rem;">
            <div class="card-eyebrow">Ready when you are</div>
            <div style="font-size:1.45rem; font-weight:800; margin:0.4rem 0 0.6rem; letter-spacing:-0.02em; color:var(--ink-inverse);">
                Trained on {DATASET_STATS['total_articles']:,} real articles.
            </div>
            <div style="font-size:0.96rem; color:var(--ink-inverse-muted); max-width:480px; margin:0 auto; line-height:1.65;">
                {DATASET_STATS['credible_count']:,} credible and {DATASET_STATS['fake_count']:,} fake
                articles went into training and evaluating this model. Switch to the
                <strong>Analyse News</strong> tab above to see it work on your own text.
            </div>
        </div>
    """)


# ═════════════════════════════════════════════════════════════════════════
# ANALYSE NEWS  (prediction flow — pipeline unchanged, layout tightened)
# ═════════════════════════════════════════════════════════════════════════
def render_analyse() -> None:
    render_html("""
        <div class="header-block fade-in">
            <h1 class="header-title" style="font-size:2.1rem;">Check an article's credibility</h1>
            <p class="header-description">
                Paste a headline and body below, or load a sample to see the model in action.
            </p>
        </div>
    """)

    fake_clicked, credible_clicked = render_sample_buttons()
    if fake_clicked:
        st.session_state["input_title"] = SAMPLE_FAKE_ARTICLE["title"]
        st.session_state["input_body"] = SAMPLE_FAKE_ARTICLE["body"]
        st.rerun()
    if credible_clicked:
        st.session_state["input_title"] = SAMPLE_CREDIBLE_ARTICLE["title"]
        st.session_state["input_body"] = SAMPLE_CREDIBLE_ARTICLE["body"]
        st.rerun()

    render_html("<div style='height:0.5rem'></div>")

    # Two-column layout: form on the left, tips card fills what used to be
    # empty whitespace on the right. No new functionality, just presentation.
    col_form, col_tips = st.columns([2, 1], gap="large")
    with col_form:
        title, body, submitted = render_input_form()
    with col_tips:
        render_tips_card()

    if submitted:
        if validate_inputs(title, body):
            with st.spinner("Analysing article…"):
                try:
                    result = predict(title, body)
                    render_results(result)

                    top_terms = get_top_terms(title, body)
                    render_explanation(top_terms)
                    render_highlighted_article(title, body, top_terms)
                    render_download_report(title, result, top_terms)

                    add_to_history(title, result)
                except FileNotFoundError as e:
                    st.error(
                        f"**Model file not found.**\n\n"
                        f"Ensure `model.pkl` and `vectorizer.pkl` exist at the "
                        f"paths specified in `config.py`.\n\n`{e}`"
                    )
                except Exception as e:
                    st.error(
                        f"**An unexpected error occurred during prediction.**\n\n`{e}`"
                    )

    render_history()
    render_about()


# ═════════════════════════════════════════════════════════════════════════
# MODEL INSIGHTS  (real evaluation results — numbers/logic unchanged)
# ═════════════════════════════════════════════════════════════════════════
def render_dataset_overview() -> None:
    render_html('<div class="section-label">Dataset Overview</div>')
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Articles", f"{DATASET_STATS['total_articles']:,}")
    c2.metric("Credible", f"{DATASET_STATS['credible_count']:,}")
    c3.metric("Fake", f"{DATASET_STATS['fake_count']:,}")

    c4, c5, c6 = st.columns(3)
    c4.metric("Train Set", f"{DATASET_STATS['train_size']:,}")
    c5.metric("Test Set", f"{DATASET_STATS['test_size']:,}")
    c6.metric("TF-IDF Vocabulary", f"{DATASET_STATS['vocab_size']:,}")

    credible_pct = DATASET_STATS["credible_count"] / DATASET_STATS["total_articles"]
    render_html(
        f'<p class="progress-label">Class Balance — {credible_pct*100:.1f}% Credible / '
        f'{(1-credible_pct)*100:.1f}% Fake</p>'
    )
    st.progress(credible_pct)


def render_model_comparison() -> None:
    st.markdown("---")
    render_html('<div class="section-label">Model Comparison — Test Set Results</div>')
    st.caption("Exact figures from 5-fold stratified cross-validation and held-out test evaluation (03_evaluation.ipynb).")

    rows = []
    for name, m in MODEL_METRICS.items():
        rows.append({
            "Model": name + (" ⭐" if m["selected"] else ""),
            "Accuracy": f"{m['accuracy']*100:.2f}%",
            "Precision": f"{m['precision']*100:.2f}%",
            "Recall": f"{m['recall']*100:.2f}%",
            "F1 Score": f"{m['f1']*100:.2f}%",
            "ROC-AUC": f"{m['roc_auc']:.4f}",
            "CV F1 (mean±std)": f"{m['cv_f1_mean']:.4f} ± {m['cv_f1_std']:.4f}",
            "Train Time": f"{m['train_time_s']:.2f}s",
        })
    df = pd.DataFrame(rows).set_index("Model")
    st.dataframe(df, use_container_width=True)

    render_html(f"""
        <div class="uicard fade-in" style="margin-top:1rem;">
            <div class="card-eyebrow">Selected Model — {SELECTED_MODEL_NAME}</div>
            <div style="font-size:0.92rem; color:var(--ink-body); line-height:1.65; margin-top:0.4rem;">
                {MODEL_SELECTION_RATIONALE}
            </div>
        </div>
    """)


def render_charts() -> None:
    st.markdown("---")
    render_html('<div class="section-label">Confusion Matrices — All Models</div>')
    if os.path.exists(ASSET_CONFUSION_MATRICES):
        st.image(ASSET_CONFUSION_MATRICES, use_container_width=True)

    lr_cm = MODEL_METRICS[SELECTED_MODEL_NAME]["confusion_matrix"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("True Negative", lr_cm["tn"])
    c2.metric("False Positive", lr_cm["fp"])
    c3.metric("False Negative", lr_cm["fn"])
    c4.metric("True Positive", lr_cm["tp"])
    st.caption(f"{SELECTED_MODEL_NAME} (deployed model) — rows are actual label, columns are predicted label.")

    st.markdown("---")
    render_html('<div class="section-label">ROC Curve Comparison</div>')
    if os.path.exists(ASSET_ROC_CURVES):
        st.image(ASSET_ROC_CURVES, use_container_width=True)
    st.caption(
        "Logistic Regression AUC = 0.9993 · Multinomial NB AUC = 0.9920 · "
        "Random Forest AUC = 0.9997"
    )

    st.markdown("---")
    render_html('<div class="section-label">Feature Importance — Logistic Regression</div>')
    if os.path.exists(ASSET_FEATURE_IMPORTANCE):
        st.image(ASSET_FEATURE_IMPORTANCE, use_container_width=True)
    st.caption(
        "Top 20 coefficients per class, taken directly from the trained model. "
        "Positive coefficients push toward Fake, negative toward Credible — note how "
        "source-attribution language ('reuters', 'said', 'washington reuters') strongly "
        "signals Credible, while engagement-bait terms ('video', 'via', 'image') signal Fake."
    )


def render_insights() -> None:
    render_html("""
        <div class="header-block fade-in">
            <h1 class="header-title" style="font-size:2.1rem;">How the model was built and evaluated</h1>
            <p class="header-description">
                Every number and chart on this page comes directly from the Phase 3 evaluation notebook — nothing here is a placeholder.
            </p>
        </div>
    """)
    render_dataset_overview()
    render_model_comparison()
    render_charts()


# ═════════════════════════════════════════════════════════════════════════
# ABOUT
# ═════════════════════════════════════════════════════════════════════════
def render_objective() -> None:
    render_html(f"""
        <div class="uicard fade-in">
            <div class="card-eyebrow">Project Objective</div>
            <div style="font-size:0.95rem; color:var(--ink-body); line-height:1.7; margin-top:0.5rem;">
                Build an end-to-end NLP system that classifies news articles as
                 <strong> Credible</strong> or <strong>Fake</strong> using classical machine
                learning — from raw text to a deployed, interactive web application —
                while keeping every step interpretable enough to explain in an interview.
            </div>
        </div>
    """)


def render_pipeline() -> None:
    st.markdown("---")
    render_html('<div class="section-label">The NLP Pipeline</div>')
    for step in PIPELINE_STEPS:
        render_html(f"""
            <div class="pipeline-step fade-in">
                <div class="pipeline-number">{step['step']}</div>
                <div>
                    <div class="pipeline-title">{step['title']}</div>
                    <div class="pipeline-detail">{step['detail']}</div>
                </div>
            </div>
        """)


def render_workflow() -> None:
    """Data sources + notebooks — makes the real ML workflow visible."""
    st.markdown("---")
    render_data_sources()
    render_html("<div style='height:1rem'></div>")
    render_notebooks()


def render_dataset_credit() -> None:
    st.markdown("---")
    render_html('<div class="section-label">Dataset</div>')
    render_html(f"""
        <div class="uicard fade-in">
            <div style="font-size:0.92rem; color:var(--ink-muted); line-height:1.7;">
                {DATASET_CREDIT}<br><br>
                <strong>{DATASET_STATS['total_articles']:,}</strong> total articles ·
                <strong>{DATASET_STATS['credible_count']:,}</strong> credible ·
                <strong>{DATASET_STATS['fake_count']:,}</strong> fake ·
                split into <strong>{DATASET_STATS['train_size']:,}</strong> train /
                <strong>{DATASET_STATS['test_size']:,}</strong> test articles.
            </div>
        </div>
    """)


def render_tech_stack() -> None:
    st.markdown("---")
    render_html('<div class="section-label">Technologies Used</div>')
    pills = "".join(f'<span class="tech-pill">{t}</span>' for t in TECH_STACK)
    render_html(f'<div class="fade-in">{pills}</div>')


def render_folder_structure() -> None:
    st.markdown("---")
    render_html('<div class="section-label">Folder Structure</div>')
    st.code(FOLDER_STRUCTURE, language="text")


def render_about_tab() -> None:
    render_html("""
        <div class="header-block fade-in">
            <h1 class="header-title" style="font-size:2.1rem;">About this project</h1>
            <p class="header-description">
                Objective, dataset, NLP pipeline, model selection, and how the codebase
                is organised.
            </p>
        </div>
    """)
    render_objective()
    render_pipeline()
    render_workflow()
    render_dataset_credit()
    render_tech_stack()
    render_folder_structure()


# ═════════════════════════════════════════════════════════════════════════
# MAIN — brand strip + tabbed navigation
# ═════════════════════════════════════════════════════════════════════════
def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    render_top_nav()

    tab_home, tab_analyse, tab_insights, tab_about = st.tabs(
        ["Home", "Analyse News", "Model Insights", "About"]
    )

    with tab_home:
        render_home()
    with tab_analyse:
        render_analyse()
    with tab_insights:
        render_insights()
    with tab_about:
        render_about_tab()

    render_footer()


if __name__ == "__main__":
    main()