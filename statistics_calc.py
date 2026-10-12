import statistics
import pandas as pd


def _prepare(df):
    """Make a copy and turn the date column into real dates."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df


def daily_totals(df):
    """Total spending for each day that has at least one expense."""
    df = _prepare(df)
    daily = df.groupby("date")["amount"].sum().reset_index()
    daily.columns = ["Date", "Total"]
    daily["Date"] = daily["Date"].dt.date
    return daily


def weekly_totals(df):
    """Total spending per week (weeks run Monday to Sunday)."""
    df = _prepare(df)
    weekly = df.set_index("date")["amount"].resample("W-SUN").sum().reset_index()
    weekly.columns = ["Week Ending (Sunday)", "Total"]
    weekly["Week Ending (Sunday)"] = weekly["Week Ending (Sunday)"].dt.date
    return weekly


def describe(values):
    """Mean, median, mode, and range of a list of numbers."""
    values = list(values)
    modes = statistics.multimode(values)

    # If every value appears equally often (for example, all different),
    # there is no mode.
    if len(modes) == len(set(values)):
        mode_text = "No mode"
    else:
        mode_text = ", ".join(f"{m:,.2f}" for m in sorted(modes))

    return {
        "Count": len(values),
        "Mean": statistics.mean(values),
        "Median": statistics.median(values),
        "Mode": mode_text,
        "Minimum": min(values),
        "Maximum": max(values),
        "Range": max(values) - min(values),
    }


def category_totals(df):
    """Total and percentage of spending for each category (largest first)."""
    cats = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    cats = cats.reset_index()
    cats.columns = ["Category", "Total"]
    cats["Percent"] = cats["Total"] / cats["Total"].sum() * 100
    return cats


def monthly_totals(df):
    """Total spending for each month."""
    df = _prepare(df)
    monthly = df.groupby(df["date"].dt.strftime("%Y-%m"))["amount"].sum().reset_index()
    monthly.columns = ["Month", "Total"]
    return monthly