import calendar
import pandas as pd


def _this_month(df, today):
    days = pd.to_datetime(df["date"])
    return df[(days.dt.year == today.year) & (days.dt.month == today.month)]


def budget_status(df, budgets, today):
    """One row per budget: how much of this month's limit is used."""
    month = _this_month(df, today)
    rows = []
    for category, limit in budgets.items():
        if category == "Overall":
            spent = month["amount"].sum()
        else:
            spent = month.loc[month["category"] == category, "amount"].sum()
        rows.append({"Category": category, "Budget": limit, "Spent": spent,
                     "Remaining": limit - spent, "Used": spent / limit * 100})
    return pd.DataFrame(rows, columns=["Category", "Budget", "Spent", "Remaining", "Used"])


def budget_alerts(status):
    """Warnings for budgets that are used up or almost used up."""
    alerts = []
    for r in status.itertuples():
        name = "monthly" if r.Category == "Overall" else r.Category
        if r.Used >= 100:
            alerts.append(("warning", f"You are over your {name} budget by {-r.Remaining:,.2f} this month."))
        elif r.Used >= 80:
            alerts.append(("info", f"You have used {r.Used:.0f}% of your {name} budget this month."))
    return alerts


def month_projection(df, today):
    """Spent so far, projected month total (daily average x days in month), days left."""
    spent = _this_month(df, today)["amount"].sum()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    projected = spent / today.day * days_in_month
    return spent, projected, days_in_month - today.day
