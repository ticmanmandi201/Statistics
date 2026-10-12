"""Look and feel. Two main colors: deep teal (#0F766E / #0A3F3B) and gold (#F2B01E)."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, .stApp, h1, h2, h3, h4, p, label, li, td, th, button, input, textarea {
    font-family: 'IBM Plex Sans', 'Segoe UI', sans-serif;
}
.stApp { font-variant-numeric: tabular-nums; }
.block-container { padding-top: 2.2rem; max-width: 1200px; }
.stApp h1, .stApp h2, .stApp h3 { color: #0A3F3B; font-weight: 600; letter-spacing: -0.01em; }

/* ---------- Sidebar ---------- */
.brand { padding: 4px 0 16px 0; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.18); }
.brand-name { font-size: 1.45rem; font-weight: 600; color: #FFFFFF; }
.brand-name::before {
    content: ""; display: inline-block; width: 11px; height: 11px; border-radius: 50%;
    background: #F2B01E; margin-right: 9px;
}
.brand-sub { font-size: 0.85rem; color: #A7D3CC; margin-top: 2px; }

[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%; padding: 13px 16px; border-radius: 10px; cursor: pointer;
    border-left: 4px solid transparent; align-items: center;
}
/* hide the round radio circle, keep the label */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child:not(:has([data-testid="stMarkdownContainer"])) {
    display: none;
}
[data-testid="stSidebar"] [role="radiogroup"] label p { font-size: 1.12rem; }
[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stIconMaterial"] {
    font-size: 1.5rem; color: #9FD8CE;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,0.08); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: rgba(255,255,255,0.15); border-left-color: #F2B01E; font-weight: 600;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) [data-testid="stIconMaterial"] {
    color: #F2B01E;
}

/* ---------- Main area ---------- */
[data-testid="stMetric"] {
    background: #FFFFFF; border: 1px solid #D5DEDA; border-left: 4px solid #F2B01E;
    border-radius: 6px; padding: 12px 16px;
}
[data-testid="stMetricLabel"] { color: #3F5560; }
[data-testid="stMetricValue"] { font-weight: 600; font-size: 1.6rem; color: #0A3F3B; }

.stButton > button, .stDownloadButton > button {
    background: #0F766E; color: #FFFFFF; border: 0; border-radius: 6px; font-weight: 500;
}
.stButton > button p, .stDownloadButton > button p { color: #FFFFFF; }
.stButton > button:hover, .stDownloadButton > button:hover { background: #0A5C55; }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
    outline: 2px solid #F2B01E; outline-offset: 2px;
}
[data-testid="stDataFrame"] { border: 1px solid #D5DEDA; border-radius: 6px; }

.hero {
    background: #0F766E; border-left: 8px solid #F2B01E; border-radius: 8px;
    padding: 22px 28px; margin-bottom: 16px;
}
.hero-label { color: rgba(255,255,255,0.85); font-size: 1rem; }
.hero-value { font-size: 3.4rem; font-weight: 600; line-height: 1.1; color: #FFFFFF; }
.hero-bar { height: 8px; background: rgba(255,255,255,0.25); border-radius: 4px; margin: 14px 0 8px 0; }
.hero-bar div { height: 100%; border-radius: 4px; }
.hero-note { color: rgba(255,255,255,0.85); font-size: 0.95rem; }
</style>
"""

BRAND = """
<div class="brand">
  <div class="brand-name">Spending Patterns</div>
  <div class="brand-sub">Analysis based on daily expenses</div>
</div>
"""


def hero_html(spent, budget, days_left):
    """Big panel for this month's spending, with a budget bar if a budget is set."""
    if budget:
        used = spent / budget * 100
        color = "#FFFFFF" if used < 80 else "#F6C453" if used < 100 else "#FF8A80"
        bar = (f'<div class="hero-bar"><div style="width:{min(used, 100):.0f}%;'
               f'background:{color}"></div></div>')
        note = f"{used:.0f}% of your {budget:,.2f} monthly budget used, {days_left} days left"
    else:
        bar = ""
        note = f"{days_left} days left this month. Set a monthly budget to track your limit."
    return (f'<div class="hero"><div class="hero-label">Spent this month</div>'
            f'<div class="hero-value">{spent:,.2f}</div>{bar}'
            f'<div class="hero-note">{note}</div></div>')