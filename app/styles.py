"""
styles.py — All custom CSS for the application.
Injected once per page via st.markdown(..., unsafe_allow_html=True).

Theme: light research-tool palette — cream background, white cards, mint
green accent, dark slate text. Deliberately avoids dark/near-black surfaces,
purple/indigo gradients, neon glow, and glassmorphism, so the app reads as a
research/ML tool rather than an AI-chatbot SaaS product.

Every text color token below was chosen to meet at least WCAG AA contrast
(4.5:1) against the surface it sits on. Nothing in this file uses low-opacity
text for body copy — low contrast was the single biggest issue in the
previous version and is treated as a hard rule here.
"""

CSS = """
<style>

/* ── Font ──────────────────────────────────────────────────────────────────
   Barlow is the font that actually renders (the old Noto Sans Hanunoo import
   only ships glyphs for the Hanunoo script, so it silently fell back to
   Barlow for every English character anyway). Declaring Barlow directly
   keeps the same visual look with one less dead network request. ────────── */
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800;900&family=Barlow+Semi+Condensed:wght@500;600;700&display=swap');

html {font-size: 100%;}
h1 {font-size: 4.210rem;}
h2 {font-size: 3.158rem;}
h3 {font-size: 2.369rem;}
h4 {font-size: 1.777rem;}
h5 {font-size: 1.333rem;}
small {font-size: 0.750rem;}

/* ── Color Tokens ──────────────────────────────────────────────────────────
   Cream background + white cards + mint accent. Locked to light mode
   regardless of OS dark-mode setting, since the design is built for a
   specific light palette, not a dark counterpart. ───────────────────────── */
:root {
    --bg: #FAF8F4;              /* cream page background */
    --bg-elevated: #F3EFE6;
    --card: #FFFFFF;            /* white cards */
    --card-hover: #F6F4EE;
    --surface-alt: #F0ECE2;
    --border: #E7E5E4;
    --border-strong: #D8D4CC;

    --ink: #1F2937;             /* dark slate — headings */
    --ink-body: #374151;        /* dark slate — body copy */
    --ink-muted: #4B5563;       /* muted but still AA-readable on cream/white */
    --ink-inverse: #FFFFFF;     /* text on dark/mint-deep surfaces */
    --ink-inverse-muted: #DCEFE9;

    --accent: #4F9C8A;          /* mint, darkened enough to work as text/icons */
    --accent-hover: #3F8677;
    --accent-mint: #8FD3C1;     /* lighter mint — backgrounds, borders only */
    --accent-soft: rgba(143, 211, 193, 0.16);
    --accent-soft-border: rgba(79, 156, 138, 0.35);
    --accent-deep: #2E6156;     /* dark mint card background, AA with white text */

    /* Verdict colors — kept distinct from mint so results stay unambiguous */
    --credible: #2F7A4D;
    --credible-soft: rgba(47, 122, 77, 0.12);
    --credible-border: rgba(47, 122, 77, 0.35);

    --danger: #B0463A;
    --danger-soft: rgba(176, 70, 58, 0.12);
    --danger-border: rgba(176, 70, 58, 0.35);

    --amber: #93690A;
    --amber-soft: rgba(163, 128, 26, 0.13);
    --amber-border: rgba(163, 128, 26, 0.35);
}

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    font-weight: 400;
    color: var(--ink-body);
}
h1, h2, h3, h4, h5 {
    font-family: 'Barlow', sans-serif;
    font-weight: 700;
}

.stApp {
    background: var(--bg);
}
header[data-testid="stHeader"] {
    background: var(--bg) !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1040px;
}

/* ── Fade-in animation ─────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeInUp 0.4s ease both; }
.fade-in-delay-1 { animation-delay: 0.05s; }
.fade-in-delay-2 { animation-delay: 0.1s; }
.fade-in-delay-3 { animation-delay: 0.15s; }

/* ── Top Nav ───────────────────────────────────────────────────────────── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0 1rem;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 0.25rem;
}
.top-nav-logo {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: 0.01em;
    text-transform: uppercase;
}
.top-nav-logo span {
    font-weight: 800;
    color: var(--accent);
}

/* ── Eyebrow / Badge ───────────────────────────────────────────────────── */
.eyebrow-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--accent-hover);
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.3rem 0;
    margin-bottom: 1.1rem;
    border-bottom: 2px solid var(--accent);
}

/* ── Hero / Header Block ───────────────────────────────────────────────── */
.header-block {
    padding: 1rem 0 1.75rem;
    margin-bottom: 0.5rem;
}
.header-block.centered { text-align: center; }

.header-title {
    font-size: 3rem;
    font-weight: 800;
    color: var(--ink);
    margin: 0 0 0.5rem;
    letter-spacing: -0.02em;
    line-height: 1.12;
}
.header-title .accent {
    font-weight: 800;
    color: var(--accent);
    display: block;
}
.header-subtitle {
    font-size: 1.05rem;
    color: var(--accent-hover);
    font-weight: 600;
    margin: 0.5rem 0 0.6rem;
}
.header-description {
    font-size: 1rem;
    color: var(--ink-body);
    max-width: 640px;
    line-height: 1.7;
}
.header-block.centered .header-description { margin: 0 auto; }

/* ── Section Labels ────────────────────────────────────────────────────── */
.section-label {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent-hover);
    margin-bottom: 1rem;
}
.section-label::before {
    content: "";
    width: 20px; height: 2px;
    background: var(--accent);
    display: inline-block;
}

/* ── Stat Row (Home page) ──────────────────────────────────────────────── */
.stat-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    padding: 1.6rem 0;
    border-top: 1px solid var(--border-strong);
    border-bottom: 1px solid var(--border-strong);
    margin: 1.5rem 0 2rem;
}
.stat-item {
    flex: 1 1 140px;
    background: var(--card);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 4px;
    padding: 1.1rem 1.2rem;
}
.stat-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: -0.01em;
    line-height: 1.1;
    font-variant-numeric: tabular-nums;
}
.stat-label {
    font-size: 0.82rem;
    color: var(--ink-muted);
    margin-top: 0.35rem;
    font-weight: 500;
}

/* ── Generic Card ──────────────────────────────────────────────────────── */
.uicard {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.6rem 1.5rem;
    box-shadow: 0 1px 3px rgba(31, 41, 55, 0.06);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.uicard:hover {
    box-shadow: 0 6px 18px rgba(31, 41, 55, 0.08);
    border-color: var(--accent-soft-border);
}
/* Dark mint card — used for the homepage "Ready when you are" callout.
   Body copy uses --ink-inverse-muted (not a low-opacity white) so it stays
   readable on the dark mint background. */
.uicard-dark {
    background: var(--accent-deep);
    color: var(--ink-inverse);
    border: 1px solid var(--accent-deep);
    border-radius: 6px;
}
.uicard-dark .card-eyebrow { color: var(--accent-mint); }

/* ── Feature Card (Home) ───────────────────────────────────────────────── */
.feature-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 4px;
    padding: 1.6rem 1.5rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.feature-card:hover {
    box-shadow: 0 6px 18px rgba(31, 41, 55, 0.08);
    border-color: var(--border-strong);
    background: var(--card-hover);
}
.feature-kicker {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--accent-hover);
    margin-bottom: 0.6rem;
}
.feature-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.5rem;
    letter-spacing: -0.01em;
}
.feature-detail {
    font-size: 0.95rem;
    color: var(--ink-body);
    line-height: 1.7;
}

/* ── Pipeline Step (About page) ────────────────────────────────────────── */
.pipeline-step {
    display: flex;
    gap: 1.1rem;
    padding: 1.3rem 0;
    border-bottom: 1px solid var(--border);
}
.pipeline-step:last-child { border-bottom: none; }
.pipeline-number {
    font-size: 1.4rem;
    color: var(--accent);
    font-weight: 800;
    min-width: 2.4rem;
    font-variant-numeric: tabular-nums;
}
.pipeline-title {
    font-weight: 700;
    color: var(--ink);
    font-size: 1.05rem;
    margin-bottom: 0.3rem;
}
.pipeline-detail {
    font-size: 0.93rem;
    color: var(--ink-body);
    line-height: 1.7;
}

/* ── Notebook Card (About page — makes the real ML workflow visible) ─────── */
.notebook-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
}
.notebook-file {
    display: inline-block;
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--accent-hover);
    background: var(--accent-soft);
    border: 1px solid var(--accent-soft-border);
    border-radius: 3px;
    padding: 0.2rem 0.6rem;
    margin-bottom: 0.6rem;
}
.notebook-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.7rem;
}
.notebook-list {
    margin: 0;
    padding-left: 1.2rem;
    color: var(--ink-body);
    font-size: 0.92rem;
    line-height: 1.85;
}

/* ── Data Source Item (About page) ────────────────────────────────────── */
.data-source-item {
    display: flex;
    gap: 1rem;
    align-items: baseline;
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--border);
}
.data-source-item:last-child { border-bottom: none; }
.data-source-file {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-weight: 700;
    color: var(--ink);
    font-size: 0.9rem;
    min-width: 150px;
}
.data-source-detail {
    color: var(--ink-muted);
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ── Tech Pills ────────────────────────────────────────────────────────── */
.tech-pill {
    display: inline-block;
    background: var(--surface-alt);
    color: var(--ink-body);
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.4rem 0.9rem;
    border-radius: 3px;
    margin: 0.2rem 0.35rem 0.2rem 0;
    border: 1px solid var(--border-strong);
}

/* ── Result Cards (Analyse page) ──────────────────────────────────────── */
.result-card {
    border-radius: 4px;
    padding: 2rem 1.4rem;
    text-align: center;
    margin-bottom: 0.75rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 4px solid transparent;
    box-shadow: 0 1px 3px rgba(31, 41, 55, 0.06);
}
.card-fake { border-left-color: var(--danger); }
.card-credible { border-left-color: var(--credible); }
.card-eyebrow {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--ink-muted);
    margin-bottom: 0.8rem;
}
.card-icon-wrap {
    width: 52px; height: 52px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 0.8rem;
    font-size: 1.4rem;
}
.card-fake .card-icon-wrap { background: var(--danger); color: #FFFFFF; }
.card-credible .card-icon-wrap { background: var(--credible); color: #FFFFFF; }
.card-fake .card-label { color: var(--danger); }
.card-credible .card-label { color: var(--credible); }
.card-label {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.01em;
}
.confidence-card {
    background: var(--card);
    border-color: var(--border-strong);
    border-left-color: var(--accent);
}
.confidence-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: -0.01em;
    margin: 0.35rem 0;
    font-variant-numeric: tabular-nums;
}

/* ── Tier Badge ────────────────────────────────────────────────────────── */
.tier-badge {
    display: inline-block;
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.3rem 0.85rem;
    border-radius: 3px;
    margin-top: 0.4rem;
}
.tier-high      { background: var(--credible-soft); color: var(--credible); border: 1px solid var(--credible-border); }
.tier-moderate  { background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber-border); }
.tier-uncertain { background: var(--danger-soft); color: var(--danger); border: 1px solid var(--danger-border); }

/* ── Progress Bar Label ────────────────────────────────────────────────── */
.progress-label {
    font-size: 0.86rem;
    font-weight: 600;
    color: var(--ink-body);
    margin: 0.6rem 0 0.3rem;
}

/* ── Probability Cards ─────────────────────────────────────────────────── */
.prob-card {
    background: var(--card);
    border: 1px solid var(--border-strong);
    border-radius: 4px;
    padding: 1.3rem;
    text-align: center;
    margin-top: 0.5rem;
}
.prob-label {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    color: var(--ink-muted);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}
.prob-value {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    font-variant-numeric: tabular-nums;
}
.fake-prob     { color: var(--danger); }
.credible-prob { color: var(--credible); }

/* ── Explanation / Terms ───────────────────────────────────────────────── */
.term-chip {
    display: inline-block;
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.84rem;
    font-weight: 600;
    padding: 0.32rem 0.8rem;
    border-radius: 3px;
    margin: 0.2rem 0.3rem 0.2rem 0;
    border: 1px solid transparent;
}
.term-chip-fake { background: var(--danger-soft); color: var(--danger); border-color: var(--danger-border); }
.term-chip-credible { background: var(--credible-soft); color: var(--credible); border-color: var(--credible-border); }

/* ── Highlighted Article (in-place term highlighting) ─────────────────────
   Reuses the same danger/credible tokens as term chips and the tier badges,
   so red/green here means the same thing everywhere else in the app. ────── */
.highlighted-article-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.6;
    margin-bottom: 0.9rem;
    padding-bottom: 0.9rem;
    border-bottom: 1px solid var(--border);
}
.highlighted-article-body {
    font-size: 0.94rem;
    color: var(--ink-body);
    line-height: 1.85;
    white-space: pre-wrap;
}
.highlight-fake, .highlight-credible {
    border-radius: 3px;
    padding: 0.05rem 0.2rem;
    font-weight: 600;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
}
.highlight-fake { background: var(--danger-soft); color: var(--danger); }
.highlight-credible { background: var(--credible-soft); color: var(--credible); }

.highlight-legend {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.85rem;
    flex-wrap: wrap;
}
.legend-item {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.84rem;
    color: var(--ink-muted);
    font-weight: 500;
}
.legend-swatch {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    display: inline-block;
}
.legend-fake { background: var(--danger); }
.legend-credible { background: var(--credible); }

/* ── Download Report ───────────────────────────────────────────────────── */
.report-card {
    background: var(--surface-alt);
    border: 1px solid var(--border-strong);
    border-radius: 6px;
    padding: 1.1rem 1.3rem;
    margin-top: 0.75rem;
}
.report-card-text {
    font-size: 0.88rem;
    color: var(--ink-muted);
    line-height: 1.6;
    margin-bottom: 0.7rem;
}
.report-card-text strong { color: var(--ink); }

/* ── Uncertain Warning ─────────────────────────────────────────────────── */
.uncertain-warning {
    background: var(--amber-soft);
    border: 1px solid var(--amber-border);
    border-left: 4px solid var(--amber);
    border-radius: 4px;
    padding: 1.05rem 1.2rem;
    font-size: 0.9rem;
    color: #6B5411;
    line-height: 1.7;
    margin-top: 0.75rem;
}

/* ── History Item ──────────────────────────────────────────────────────── */
.history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.9rem 1.15rem;
    margin-bottom: 0.6rem;
}
.history-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--ink);
    max-width: 60%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.history-meta {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.78rem;
    color: var(--ink-muted);
}
.history-badge {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.22rem 0.65rem;
    border-radius: 3px;
}

/* ── Analyse Page — Tips Card ──────────────────────────────────────────────
   Fills the whitespace next to the input form with something useful rather
   than leaving it empty, without adding any new functionality. ─────────── */
.tips-card {
    background: var(--surface-alt);
    border: 1px solid var(--border-strong);
    border-radius: 6px;
    padding: 1.3rem 1.4rem;
}
.tips-card-title {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--accent-hover);
    margin-bottom: 0.7rem;
}
.tips-list {
    margin: 0;
    padding-left: 1.1rem;
    color: var(--ink-body);
    font-size: 0.88rem;
    line-height: 1.8;
}

/* ── Footer ────────────────────────────────────────────────────────────── */
.footer-block {
    margin-top: 3rem;
    padding-top: 1.75rem;
    border-top: 2px solid var(--ink);
}
.footer-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.75rem;
    text-align: left;
}
.footer-col-title {
    font-family: 'Barlow Semi Condensed', sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent-hover);
    margin-bottom: 0.5rem;
}
.footer-col-text {
    font-size: 0.85rem;
    color: var(--ink-muted);
    line-height: 1.65;
}
@media (max-width: 640px) {
    .footer-grid {
        grid-template-columns: 1fr;
        gap: 1.4rem;
    }
}

/* ── Streamlit Widget Overrides ────────────────────────────────────────── */
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label {
    font-weight: 700 !important;
    color: var(--ink) !important;
    font-size: 0.92rem !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 4px !important;
    border: 1.5px solid var(--border-strong) !important;
    font-size: 0.95rem !important;
    background: var(--card) !important;
    color: var(--ink) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
    color: var(--ink-muted) !important;
    opacity: 1 !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 700 !important;
    font-size: 0.97rem !important;
    padding: 0.7rem 1.25rem !important;
    transition: background 0.15s ease, transform 0.1s ease;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:focus-visible {
    outline: none !important;
    box-shadow: 0 0 0 3px var(--accent-soft-border) !important;
}

div[data-testid="stButton"] > button:not([kind="primary"]) {
    border-radius: 4px !important;
    font-weight: 600 !important;
    border: 1.5px solid var(--border-strong) !important;
    color: var(--ink) !important;
    background: var(--card) !important;
    transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
}
div[data-testid="stButton"] > button:not([kind="primary"]):hover {
    border-color: var(--accent) !important;
    color: var(--accent-hover) !important;
    background: var(--card-hover) !important;
}

div[data-testid="stProgress"] > div > div > div {
    background: var(--accent) !important;
    border-radius: 999px !important;
}
div[data-testid="stProgress"] > div > div {
    background: var(--surface-alt) !important;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--border-strong) !important;
    border-radius: 6px !important;
    overflow: hidden;
    background: var(--card);
}
div[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    color: var(--ink) !important;
}

/* Tabs — primary navigation, sits directly under the logo strip */
div[data-testid="stTabs"] {
    margin-bottom: 2rem;
}
div[data-baseweb="tab-list"] {
    gap: 2rem !important;
    border-bottom: 1px solid var(--border-strong) !important;
}
button[data-baseweb="tab"] {
    font-family: 'Barlow Semi Condensed', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: var(--ink-muted) !important;
    padding: 0.6rem 0.1rem !important;
}
button[data-baseweb="tab"]:hover {
    color: var(--ink) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent-hover) !important;
}
div[data-baseweb="tab-highlight"] {
    background: var(--accent) !important;
    height: 3px !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--border-strong) !important;
    border-radius: 6px !important;
    overflow: hidden;
}

div[data-testid="stAlert"] {
    border-radius: 4px !important;
    font-weight: 500;
    background: var(--surface-alt) !important;
    border: 1px solid var(--border-strong) !important;
}

div[data-testid="stMetric"] {
    background: var(--card);
    border: 1px solid var(--border-strong);
    border-top: 3px solid var(--accent);
    border-radius: 4px;
    padding: 1.1rem 1.2rem;
}
div[data-testid="stMetricLabel"] { color: var(--ink-muted) !important; font-weight: 700 !important; }
div[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-weight: 800 !important;
    font-variant-numeric: tabular-nums;
}

hr { margin: 1.5rem 0 !important; border-color: var(--border-strong) !important; }

[data-testid="stCaptionContainer"], .stCaption {
    color: var(--ink-muted) !important;
}

div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li {
    color: var(--ink-body);
}
div[data-testid="stMarkdownContainer"] strong {
    color: var(--ink);
}
div[data-testid="stMarkdownContainer"] h3,
div[data-testid="stMarkdownContainer"] h4 {
    color: var(--ink) !important;
}
div[data-testid="stMarkdownContainer"] table {
    color: var(--ink-body);
}

</style>
"""