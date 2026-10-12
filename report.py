from statistics_calc import daily_totals, weekly_totals, category_totals, describe
from recommendations import get_recommendations


def money(x):
    return f"{x:,.2f}"


def stat_lines(stats):
    keys = ("Mean", "Median", "Mode", "Range")
    return [f"- {k}: {stats[k] if isinstance(stats[k], str) else money(stats[k])}"
            for k in keys]


def build_report(df):
    """Make a plain-text summary report from the expenses in df."""
    daily = daily_totals(df)
    weekly = weekly_totals(df)
    cats = category_totals(df)
    peak = daily.loc[daily["Total"].idxmax()]
    low = daily.loc[daily["Total"].idxmin()]

    lines = [
        "SPENDING PATTERN SUMMARY REPORT",
        "=" * 31,
        f"Period covered: {daily['Date'].min()} to {daily['Date'].max()}",
        f"Number of expenses: {len(df)}",
        f"Total spent: {money(df['amount'].sum())}",
        f"Average per day (days with expenses): {money(daily['Total'].mean())}",
        f"Weekly average: {money(weekly['Total'].mean())}",
        "",
        "STATISTICS OF DAILY TOTALS",
        *stat_lines(describe(daily["Total"])),
        f"- Highest day: {peak['Date']} ({money(peak['Total'])})",
        f"- Lowest day: {low['Date']} ({money(low['Total'])})",
        "",
        "STATISTICS OF INDIVIDUAL EXPENSES",
        *stat_lines(describe(df["amount"])),
        "",
        "SPENDING BY CATEGORY",
        *[f"- {r.Category}: {money(r.Total)} ({r.Percent:.1f}%)"
          for r in cats.itertuples()],
        "",
        "RECOMMENDATIONS",
        *[f"- {text}" for _, text in get_recommendations(df)],
    ]
    return "\n".join(lines)
