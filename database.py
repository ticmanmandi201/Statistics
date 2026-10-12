import sqlite3
import pandas as pd

# The database is a single file saved in your project folder
DB_NAME = "expenses.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Create the expenses table if it doesn't exist yet."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            other_detail TEXT,
            payment_method TEXT
        )
    """)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(expenses)")]
    for name in ("other_detail", "payment_method"):
        if name not in columns:
            conn.execute(f"ALTER TABLE expenses ADD COLUMN {name} TEXT")
    conn.execute("CREATE TABLE IF NOT EXISTS budgets "
                 "(category TEXT PRIMARY KEY, amount REAL NOT NULL)")
    conn.commit()
    conn.close()


def add_expense(expense_date, category, amount, description, other_detail="", payment_method="Cash"):
    """Save one expense into the table."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (date, category, amount, description, other_detail, payment_method) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (str(expense_date), category, float(amount), description, other_detail, payment_method),
    )
    conn.commit()
    conn.close()


def update_expense(expense_id, expense_date, category, amount, description, other_detail="", payment_method="Cash"):
    """Change an existing expense."""
    conn = get_connection()
    conn.execute(
        "UPDATE expenses SET date = ?, category = ?, amount = ?, "
        "description = ?, other_detail = ?, payment_method = ? WHERE id = ?",
        (str(expense_date), category, float(amount), description,
         other_detail, payment_method, int(expense_id)),
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    """Remove one expense."""
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (int(expense_id),))
    conn.commit()
    conn.close()


def get_expenses():
    """Return all expenses as a pandas DataFrame (newest first)."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM expenses ORDER BY date DESC, id DESC", conn
    )
    conn.close()
    df["description"] = df["description"].fillna("")
    df["other_detail"] = df["other_detail"].fillna("")
    df["payment_method"] = df["payment_method"].fillna("")
    return df


def set_budget(category, amount):
    """Save a monthly budget ('Overall' or a category name)."""
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)",
                 (category, float(amount)))
    conn.commit()
    conn.close()


def delete_budget(category):
    conn = get_connection()
    conn.execute("DELETE FROM budgets WHERE category = ?", (category,))
    conn.commit()
    conn.close()


def get_budgets():
    """Return {category: monthly limit}."""
    conn = get_connection()
    rows = conn.execute("SELECT category, amount FROM budgets").fetchall()
    conn.close()
    return dict(rows)


def delete_all_expenses():
    """Remove every expense (budgets are kept) and restart the ID numbers."""
    conn = get_connection()
    conn.execute("DELETE FROM expenses")
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'expenses'")
    conn.commit()
    conn.close()