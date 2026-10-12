import plotly.express as px

TEAL, AMBER = "#0F766E", "#E5A100"
INK, GRID = "#14202B", "#E3EAE7"

# Each category keeps the same color on every chart
CATEGORY_COLORS = {
    "Food": "#0F766E", "Transportation": "#2563EB", "School": "#7C3AED",
    "Entertainment": "#EA580C", "Shopping": "#DB2777", "Bills and Utilities": "#64748B",
    "Health": "#CA8A04", "Personal Care": "#84CC16", "Internet and Phone": "#0891B2",
    "Gifts and Donations": "#92400E", "Other": "#A8A29E",
}


def _style(fig):
    """Shared look for every chart."""
    fig.update_layout(
        font=dict(family="IBM Plex Sans, Segoe UI, sans-serif", color=INK, size=13),
        title=dict(font=dict(size=16), x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10), legend_title_text="",
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, title_text="")
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title_text="")
    return fig


def daily_trend_chart(daily):
    fig = px.line(daily, x="Date", y="Total", markers=True,
                  title="Daily spending", color_discrete_sequence=[TEAL])
    fig.update_traces(line_width=2.5)
    fig.add_hline(y=daily["Total"].mean(), line_dash="dash", line_color=AMBER,
                  annotation_text="Average", annotation_font_color=AMBER)
    return _style(fig)


def weekly_bar_chart(weekly):
    fig = px.bar(weekly, x="Week Ending (Sunday)", y="Total",
                 title="Weekly spending", color_discrete_sequence=[TEAL])
    fig.update_xaxes(type="category")
    return _style(fig)


def category_pie(cats):
    fig = px.pie(cats, names="Category", values="Total", color="Category",
                 color_discrete_map=CATEGORY_COLORS, hole=0.55,
                 title="Share by category")
    fig.update_traces(textinfo="percent", sort=False)
    return _style(fig)


def category_bar(cats):
    fig = px.bar(cats, x="Category", y="Total", color="Category",
                 color_discrete_map=CATEGORY_COLORS, title="Total by category")
    fig.update_layout(showlegend=False)
    return _style(fig)


def comparison_chart(compare_df):
    """compare_df has a 'category' column plus one column per period."""
    long = compare_df.melt(id_vars="category", var_name="Period", value_name="Total")
    fig = px.bar(long, x="category", y="Total", color="Period", barmode="group",
                 title="Spending by category", color_discrete_sequence=[TEAL, AMBER])
    return _style(fig)


def payment_pie(pay):
    fig = px.pie(pay, names="Payment method", values="Total", hole=0.55,
                 title="Share by payment method",
                 color_discrete_sequence=list(CATEGORY_COLORS.values()))
    fig.update_traces(textinfo="percent")
    return _style(fig)