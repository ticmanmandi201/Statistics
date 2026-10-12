# Analysis of Spending Patterns Based on Daily Expenses

A Statistics and Probability school project. The website lets you record daily
expenses and analyzes them with statistics (mean, median, mode, range, weekly
average), charts, budgets, and recommendations.

## Features
- Record expenses by category and payment method; edit, delete, search, and filter
- Dashboard, daily/weekly/monthly totals, and weekly average
- Mean, median, mode, and range
- Charts: spending trends, categories, payment methods
- Compare two days or two weeks
- Monthly budgets with warnings and an end-of-month projection
- Rule-based recommendations
- Downloadable summary report and CSV export

## Tools
Python, Streamlit, SQLite, pandas, Plotly

## How to run (Windows)
1. Install Python from python.org (tick "Add python.exe to PATH").
2. Download this project and open the folder in a terminal.
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
5. Start the website:
   ```
   python -m streamlit run app.py
   ```
   It opens at http://localhost:8501. The database file (`expenses.db`) is created
   automatically the first time.

## Try it with sample data
```
python sample_data.py          # add about 8 weeks of fake expenses
python sample_data.py clear    # remove only the sample expenses
```

## Project structure
- `app.py`: the website (pages and layout)
- `database.py`: saving and reading data (SQLite)
- `statistics_calc.py`, `budgets.py`, `recommendations.py`, `report.py`: the calculations
- `charts.py`, `style.py`, `.streamlit/config.toml`: charts and look
- `sample_data.py`: test data
