import statistics
from statistics_calc import daily_totals, weekly_totals, category_totals


def get_recommendations(df):
    """Rule-based suggestions. Returns a list of (type, message)."""
    tips = []
    if df.empty:
        return tips

    daily = daily_totals(df)
    weekly = weekly_totals(df)
    cats = category_totals(df)

    # Rule 1: one category takes a big share of spending
    top = cats.iloc[0]
    if top["Percent"] > 40:
        tips.append(("warning",
            f"{top['Category']} is {top['Percent']:.0f}% of your total spending. "
            "Consider setting a limit for this category."))

    # Rule 2: too much on wants (Entertainment + Shopping)
    wants = cats[cats["Category"].isin(["Entertainment", "Shopping"])]["Percent"].sum()
    if wants > 30:
        tips.append(("warning",
            f"Entertainment and Shopping together are {wants:.0f}% of your spending. "
            "Try to cut back on non-essential purchases."))

    # Rule 3: latest week is higher than the weekly average
    if len(weekly) >= 2:
        latest = weekly["Total"].iloc[-1]
        average = weekly["Total"].mean()
        if latest > average * 1.1:
            tips.append(("warning",
                f"Your most recent week ({latest:,.2f}) is higher than your weekly "
                f"average ({average:,.2f}). Review what you spent on."))

    # Rule 4: spending rising for 3 weeks in a row
    if len(weekly) >= 3:
        a, b, c = weekly["Total"].iloc[-3:]
        if a < b < c:
            tips.append(("warning",
                "Your weekly spending has gone up three weeks in a row. "
                "Setting a weekly budget could help."))

    # Rule 5: very uneven daily spending (high variation)
    if len(daily) >= 2:
        mean = daily["Total"].mean()
        spread = statistics.stdev(daily["Total"])
        if mean > 0 and spread / mean > 0.75:
            tips.append(("info",
                "Your daily spending varies a lot from day to day. "
                "Planning a daily allowance may make spending more consistent."))

    # Always: the most expensive day
    peak = daily.loc[daily["Total"].idxmax()]
    tips.append(("info",
        f"Your highest-spending day was {peak['Date']} ({peak['Total']:,.2f}). "
        "Check what caused it."))

    if not any(kind == "warning" for kind, _ in tips):
        tips.insert(0, ("success",
            "Your spending looks balanced based on the current data. Keep it up!"))
    return tips
