import pandas as pd
import streamlit as st
from datetime import date, timedelta
from database import (init_db, add_expense, get_expenses, delete_expense,
                      update_expense, delete_all_expenses, set_budget, get_budgets, delete_budget)
from statistics_calc import daily_totals, weekly_totals, category_totals, monthly_totals, describe
from recommendations import get_recommendations
from report import build_report
from budgets import budget_status, budget_alerts, month_projection
import charts
from style import CSS, BRAND, hero_html

CATEGORIES = [
    "Food", "Transportation", "School", "Entertainment", "Shopping",
    "Bills and Utilities", "Health", "Personal Care", "Internet and Phone",
    "Gifts and Donations", "Other",
]
PAYMENTS = ["Cash", "Debit/Credit Card", "E-wallet", "Bank Transfer"]

st.set_page_config(page_title="Spending Tracker", page_icon=":material/payments:", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
init_db()

# Starting values for the Add Expense form (only set the first time)
st.session_state.setdefault("exp_date", date.today())
st.session_state.setdefault("exp_category", CATEGORIES[0])
st.session_state.setdefault("exp_other", "")
st.session_state.setdefault("exp_amount", 0.0)
st.session_state.setdefault("exp_desc", "")
st.session_state.setdefault("exp_payment", PAYMENTS[0])


# ---------- Helper functions ----------
def save_expense():
    """Runs when the Save button is clicked."""
    category = st.session_state.exp_category
    other_detail = st.session_state.exp_other.strip()
    amount = st.session_state.exp_amount

    if amount <= 0:
        st.session_state.flash = ("error", "Please enter an amount greater than 0.")
        return
    if category == "Other" and other_detail == "":
        st.session_state.flash = ("error", "Please specify what the 'Other' expense is.")
        return
    if category != "Other":
        other_detail = ""

    add_expense(st.session_state.exp_date, category, amount,
                st.session_state.exp_desc, other_detail,
                st.session_state.exp_payment)
    st.session_state.flash = ("success", "Expense saved!")
    st.session_state.exp_amount = 0.0
    st.session_state.exp_desc = ""
    st.session_state.exp_other = ""


def delete_all_clicked():
    """Runs when 'Delete all expenses' is clicked. Needs the word DELETE typed."""
    if st.session_state.confirm_delete_all.strip() == "DELETE":
        delete_all_expenses()
        st.session_state.flash = ("success", "All expenses were deleted.")
        st.session_state.confirm_delete_all = ""
    else:
        st.session_state.flash = ("error", "Type DELETE in capital letters to confirm.")


def show_flash():
    """Show the saved/error message once."""
    if "flash" in st.session_state:
        kind, text = st.session_state.pop("flash")
        getattr(st, kind)(text)


def need_data(df):
    if df.empty:
        st.info("No data to show. Add expenses first (or widen the date range).")
        return True
    return False


def format_value(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def show_stats_table(title, values):
    stats = describe(values)
    table = pd.DataFrame({"Measure": list(stats.keys()),
                          "Value": [format_value(v) for v in stats.values()]})
    st.subheader(title)
    st.dataframe(table, hide_index=True, width="stretch")


def rows_between(df, start, end):
    days = pd.to_datetime(df["date"]).dt.date
    return df[(days >= start) & (days <= end)]


# ---------- Page: Dashboard ----------
def dashboard_page(df_all):
    today = date.today()
    st.header(f"Dashboard ({today.strftime('%B %Y')})")
    if df_all.empty:
        st.info("No expenses yet. Record your first one in Add Expense and History to fill this dashboard.")
        return

    month = rows_between(df_all, today.replace(day=1), today)
    budgets = get_budgets()
    spent, projected, days_left = month_projection(df_all, today)

    st.markdown(hero_html(spent, budgets.get("Overall"), days_left), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if "Overall" in budgets:
        c1.metric("Budget left", f"{budgets['Overall'] - spent:,.2f}")
    else:
        c1.metric("Average per day", f"{spent / today.day:,.2f}")
    c2.metric("Projected month total", f"{projected:,.2f}")
    if month.empty:
        c3.metric("Top category", "-")
    else:
        top = category_totals(month).iloc[0]
        c3.metric("Top category", top["Category"], f"{top['Percent']:.0f}% of spending", delta_color="off")

    for kind, text in budget_alerts(budget_status(df_all, budgets, today)):
        getattr(st, kind)(text)

    if month.empty:
        st.info("No expenses recorded this month yet.")
    else:
        left, right = st.columns([3, 2])
        left.plotly_chart(charts.daily_trend_chart(daily_totals(month)), width="stretch")
        right.plotly_chart(charts.category_pie(category_totals(month)), width="stretch")

    st.subheader("Recent Expenses")
    recent = df_all.head(5)[["date", "category", "amount", "description"]]
    recent = recent.rename(columns={"date": "Date", "category": "Category",
                                    "amount": "Amount", "description": "Description"})
    st.dataframe(recent, hide_index=True, width="stretch")


# ---------- Page: Add Expense and History ----------
def add_page(df_all, df):
    st.header("Add an Expense")
    st.date_input("Date", key="exp_date")
    st.selectbox("Category", CATEGORIES, key="exp_category")
    if st.session_state.exp_category == "Other":
        st.text_input("Please specify what this expense is", key="exp_other")
    st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f", key="exp_amount")
    st.selectbox("Payment method", PAYMENTS, key="exp_payment")
    st.text_input("Description (optional)", key="exp_desc")
    st.button("Save expense", on_click=save_expense)
    show_flash()

    st.header("Expense History")
    if df.empty:
        st.info("No expenses yet. Add your first one above.")
    else:
        f1, f2, f3 = st.columns(3)
        search = f1.text_input("Search description")
        cat_filter = f2.multiselect("Filter by category", CATEGORIES)
        pay_filter = f3.multiselect("Filter by payment method", PAYMENTS)
        shown = df
        if search:
            text = shown["description"] + " " + shown["other_detail"]
            shown = shown[text.str.contains(search, case=False, regex=False)]
        if cat_filter:
            shown = shown[shown["category"].isin(cat_filter)]
        if pay_filter:
            shown = shown[shown["payment_method"].isin(pay_filter)]
        st.caption(f"Showing {len(shown)} of {len(df)} expenses (total {shown['amount'].sum():,.2f})")
        history = shown.rename(columns={
            "id": "ID", "date": "Date", "category": "Category", "amount": "Amount",
            "description": "Description", "other_detail": "Other (specified)",
            "payment_method": "Payment method"})
        st.dataframe(history, width="stretch", hide_index=True)
        st.download_button("Download history as CSV",
                           history.to_csv(index=False).encode("utf-8"),
                           "expense_history.csv", "text/csv")

    with st.expander("Edit or delete an expense"):
        if df_all.empty:
            st.write("Nothing to edit yet.")
            return
        labels = {int(r.id): f"#{r.id} | {r.date} | {r.category} | {r.amount:,.2f} | {r.description}"
                  for r in df_all.itertuples()}
        chosen = st.selectbox("Choose an expense", list(labels.keys()),
                              format_func=lambda i: labels[i])
        row = df_all[df_all["id"] == chosen].iloc[0]
        cat_index = CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else len(CATEGORIES) - 1

        e_date = st.date_input("Date", value=pd.to_datetime(row["date"]).date(), key=f"e_date_{chosen}")
        e_cat = st.selectbox("Category", CATEGORIES, index=cat_index, key=f"e_cat_{chosen}")
        e_other = st.text_input("Specify (only if category is Other)", value=row["other_detail"], key=f"e_other_{chosen}")
        e_amount = st.number_input("Amount", min_value=0.0, value=float(row["amount"]), step=1.0, format="%.2f", key=f"e_amount_{chosen}")
        e_desc = st.text_input("Description", value=row["description"], key=f"e_desc_{chosen}")
        pay_index = PAYMENTS.index(row["payment_method"]) if row["payment_method"] in PAYMENTS else 0
        e_pay = st.selectbox("Payment method", PAYMENTS, index=pay_index, key=f"e_pay_{chosen}")

        left, right = st.columns(2)
        if left.button("Update expense"):
            if e_amount <= 0:
                st.error("Amount must be greater than 0.")
            elif e_cat == "Other" and not e_other.strip():
                st.error("Please specify what the 'Other' expense is.")
            else:
                update_expense(chosen, e_date, e_cat, e_amount, e_desc,
                               e_other.strip() if e_cat == "Other" else "", e_pay)
                st.session_state.flash = ("success", "Expense updated!")
                st.rerun()
        sure = right.checkbox("Yes, I want to delete this expense", key=f"sure_{chosen}")
        if right.button("Delete expense"):
            if sure:
                delete_expense(chosen)
                st.session_state.flash = ("success", "Expense deleted.")
                st.rerun()
            else:
                st.warning("Tick the box first to confirm.")

    with st.expander("Delete all expenses"):
        st.warning("This permanently removes every expense. Your budgets are kept. "
                   "Download the CSV from Expense History first if you want a backup.")
        st.text_input("Type DELETE to confirm", key="confirm_delete_all")
        st.button("Delete all expenses", on_click=delete_all_clicked)


# ---------- Page: Statistics ----------
def stats_page(df):
    st.header("Statistics")
    if need_data(df):
        return
    daily, weekly = daily_totals(df), weekly_totals(df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Spent", f"{df['amount'].sum():,.2f}")
    c2.metric("Average per Day", f"{daily['Total'].mean():,.2f}")
    c3.metric("Weekly Average", f"{weekly['Total'].mean():,.2f}")

    left, right = st.columns(2)
    with left:
        st.subheader("Daily Totals")
        st.dataframe(daily.sort_values("Date", ascending=False), hide_index=True, width="stretch")
    with right:
        st.subheader("Weekly Totals")
        st.dataframe(weekly.sort_values("Week Ending (Sunday)", ascending=False), hide_index=True, width="stretch")

    st.subheader("Monthly Totals")
    st.dataframe(monthly_totals(df), hide_index=True, width="stretch")

    left, right = st.columns(2)
    with left:
        show_stats_table("Statistics of Daily Totals", daily["Total"])
    with right:
        show_stats_table("Statistics of Individual Expenses", df["amount"])


# ---------- Page: Charts and Categories ----------
def charts_page(df):
    st.header("Spending Trends")
    if need_data(df):
        return
    daily, weekly, cats = daily_totals(df), weekly_totals(df), category_totals(df)
    st.plotly_chart(charts.daily_trend_chart(daily), width="stretch")
    st.plotly_chart(charts.weekly_bar_chart(weekly), width="stretch")

    st.header("Spending by Category")
    left, right = st.columns(2)
    left.plotly_chart(charts.category_pie(cats), width="stretch")
    right.plotly_chart(charts.category_bar(cats), width="stretch")

    top = cats.iloc[0]
    st.success(f"Top category: {top['Category']} ({top['Percent']:.1f}% of total spending)")
    table = cats.copy()
    table["Total"] = table["Total"].map("{:,.2f}".format)
    table["Percent"] = table["Percent"].map("{:.1f}%".format)
    st.dataframe(table, hide_index=True, width="stretch")

    st.header("Spending by Payment Method")
    pay = df.assign(payment_method=df["payment_method"].replace("", "(not set)"))
    pay = pay.groupby("payment_method")["amount"].sum().reset_index()
    pay.columns = ["Payment method", "Total"]
    st.plotly_chart(charts.payment_pie(pay), width="stretch")

    other = df[df["category"] == "Other"].copy()
    if not other.empty:
        st.subheader("What is inside 'Other'")
        other["other_detail"] = other["other_detail"].replace("", "(not specified)")
        detail = other.groupby("other_detail")["amount"].agg(["count", "sum"]).reset_index()
        detail.columns = ["Detail", "Times", "Total"]
        st.dataframe(detail.sort_values("Total", ascending=False), hide_index=True, width="stretch")


# ---------- Page: Compare ----------
def compare_page(df_all):
    st.header("Compare Days or Weeks")
    if need_data(df_all):
        return
    mode = st.radio("Compare", ["Two days", "Two weeks"], horizontal=True)
    left, right = st.columns(2)
    first = left.date_input("First", value=date.today() - timedelta(days=7), key="cmp_a")
    second = right.date_input("Second", value=date.today(), key="cmp_b")

    def span(d):
        if mode == "Two weeks":      # the Monday-Sunday week containing d
            start = d - timedelta(days=d.weekday())
            return start, start + timedelta(days=6)
        return d, d

    (a_start, a_end), (b_start, b_end) = span(first), span(second)
    label_a = f"First: {a_start}" + (f" to {a_end}" if a_start != a_end else "")
    label_b = f"Second: {b_start}" + (f" to {b_end}" if b_start != b_end else "")
    df_a, df_b = rows_between(df_all, a_start, a_end), rows_between(df_all, b_start, b_end)
    total_a, total_b = df_a["amount"].sum(), df_b["amount"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric(label_a, f"{total_a:,.2f}")
    c2.metric(label_b, f"{total_b:,.2f}")
    change = f"{(total_b - total_a) / total_a * 100:+.1f}%" if total_a > 0 else None
    c3.metric("Difference (Second - First)", f"{total_b - total_a:,.2f}",
              delta=change, delta_color="inverse")

    if df_a.empty and df_b.empty:
        st.info("There are no expenses in either period.")
        return
    by_cat = pd.concat([df_a.groupby("category")["amount"].sum().rename(label_a),
                        df_b.groupby("category")["amount"].sum().rename(label_b)],
                       axis=1).fillna(0).reset_index()
    st.plotly_chart(charts.comparison_chart(by_cat), width="stretch")
    st.dataframe(by_cat.rename(columns={"category": "Category"}), hide_index=True, width="stretch")


# ---------- Page: Budget ----------
def budget_page(df_all):
    today = date.today()
    st.header(f"Monthly Budget ({today.strftime('%B %Y')})")
    budgets = get_budgets()

    c1, c2, c3 = st.columns([2, 2, 1], vertical_alignment="bottom")
    target = c1.selectbox("Budget for", ["Overall"] + CATEGORIES)
    limit = c2.number_input("Monthly limit", min_value=0.0, step=100.0, format="%.2f")
    if c3.button("Save budget"):
        if limit > 0:
            set_budget(target, limit)
            st.rerun()
        else:
            st.error("Enter a limit greater than 0.")

    if budgets:
        status = budget_status(df_all, budgets, today)
        for r in status.itertuples():
            st.write(f"**{r.Category}**: {r.Spent:,.2f} of {r.Budget:,.2f} ({r.Used:.0f}% used)")
            st.progress(min(r.Used / 100, 1.0))
        for kind, text in budget_alerts(status):
            getattr(st, kind)(text)
        r1, r2 = st.columns([2, 1], vertical_alignment="bottom")
        to_remove = r1.selectbox("Remove a budget", list(budgets.keys()))
        if r2.button("Remove"):
            delete_budget(to_remove)
            st.rerun()
    else:
        st.info("No budgets yet. Set one above.")

    st.subheader("End-of-Month Projection")
    spent, projected, days_left = month_projection(df_all, today)
    m1, m2, m3 = st.columns(3)
    m1.metric("Spent this month", f"{spent:,.2f}")
    m2.metric("Projected month total", f"{projected:,.2f}")
    m3.metric("Days left", days_left)
    st.caption("Projection = average spending per day so far x number of days in the month.")
    if "Overall" in budgets and projected > budgets["Overall"]:
        st.warning(f"At this pace you will pass your monthly budget by {projected - budgets['Overall']:,.2f}.")


# ---------- Page: Recommendations ----------
def tips_page(df, df_all):
    st.header("Recommendations")
    if need_data(df):
        return
    for kind, text in get_recommendations(df):
        getattr(st, kind)(text)
    status = budget_status(df_all, get_budgets(), date.today())
    for kind, text in budget_alerts(status):
        getattr(st, kind)(text)


# ---------- Page: Summary Report ----------
def report_page(df):
    st.header("Summary Report")
    if need_data(df):
        return
    report = build_report(df)
    st.code(report, language="text")
    st.download_button("Download report (.txt)", report, "spending_report.txt", "text/plain")


# ---------- Main ----------
st.sidebar.markdown(BRAND, unsafe_allow_html=True)

PAGES = ["Dashboard", "Add Expense and History", "Statistics", "Charts and Categories",
         "Compare", "Budget", "Recommendations", "Summary Report"]
ICONS = {
    "Dashboard": "dashboard", "Add Expense and History": "receipt_long",
    "Statistics": "functions", "Charts and Categories": "bar_chart",
    "Compare": "compare_arrows", "Budget": "savings",
    "Recommendations": "lightbulb", "Summary Report": "description",
}
page = st.sidebar.radio("Go to", PAGES, label_visibility="collapsed",
                        format_func=lambda p: f":material/{ICONS[p]}: {p}")

df_all = get_expenses()
df = df_all

# Period filter (applies to history, statistics, charts, tips and report)
if not df_all.empty:
    today = date.today()
    period = st.sidebar.selectbox(
        "Period", ["All time", "This week", "This month", "Last 30 days", "Custom range"])
    if period == "This week":
        df = rows_between(df_all, today - timedelta(days=today.weekday()), today)
    elif period == "This month":
        df = rows_between(df_all, today.replace(day=1), today)
    elif period == "Last 30 days":
        df = rows_between(df_all, today - timedelta(days=29), today)
    elif period == "Custom range":
        picked = st.sidebar.date_input("Date range", value=(today - timedelta(days=29), today))
        if isinstance(picked, (tuple, list)) and len(picked) == 2:
            df = rows_between(df_all, picked[0], picked[1])

if page == "Dashboard":
    dashboard_page(df_all)
elif page == "Add Expense and History":
    add_page(df_all, df)
elif page == "Statistics":
    stats_page(df)
elif page == "Charts and Categories":
    charts_page(df)
elif page == "Compare":
    compare_page(df_all)
elif page == "Budget":
    budget_page(df_all)
elif page == "Recommendations":
    tips_page(df, df_all)
else:
    report_page(df)