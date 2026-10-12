"""Fill the database with fake expenses for testing.

    python sample_data.py          adds about 8 weeks of sample expenses
    python sample_data.py clear    removes ONLY the sample expenses
"""
import random
import sys
from datetime import date, timedelta
from database import init_db, add_expense, get_connection

TAG = "[sample]"
PAYMENTS = ["Cash", "Debit/Credit Card", "E-wallet", "Bank Transfer"]
random.seed(42)


def add(day, category, low, high, detail=""):
    amount = random.randrange(low, high + 1, 5)   # multiples of 5 repeat often
    add_expense(day, category, amount, TAG, detail, random.choice(PAYMENTS))


def make_sample(days=56):
    init_db()
    conn = get_connection()
    existing = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE description = ?", (TAG,)).fetchone()[0]
    conn.close()
    if existing:
        print("Sample data is already in the database. Run with 'clear' first.")
        return

    for i in range(days):
        day = date.today() - timedelta(days=i)
        weekend = day.weekday() >= 5
        for _ in range(random.randint(1, 2)):
            add(day, "Food", 30, 200)
        if not weekend and random.random() < 0.9:
            add(day, "Transportation", 20, 120)
        if not weekend and random.random() < 0.25:
            add(day, "School", 50, 500)
        if weekend and random.random() < 0.6:
            add(day, "Entertainment", 100, 450)
        if random.random() < 0.08:
            add(day, "Shopping", 150, 800)
        if random.random() < 0.05:
            add(day, "Health", 50, 300)
        if day.weekday() == 0 and random.random() < 0.5:
            add(day, "Internet and Phone", 50, 150)
        if random.random() < 0.05:
            add(day, "Other", 30, 200, random.choice(["Haircut", "Laundry", "Printing"]))
    print("Sample expenses added.")


def clear_sample():
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE description = ?", (TAG,))
    conn.commit()
    conn.close()
    print("Sample expenses removed. Your own expenses were not touched.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_sample()
    else:
        make_sample()