# Expense Tracker

Flask + SQLite + Pandas + Matplotlib. Add income/expenses, see monthly summaries,
pie/bar charts, and export CSV or Excel reports.

## Run

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Test

```bash
pytest -q
```

## Layout

- `db.py` SQLite access
- `analysis.py` Pandas summaries
- `charts.py` Matplotlib PNG charts (in memory)
- `app.py` Flask routes, CSV/Excel export
- `templates/index.html` UI

Set `SECRET_KEY` and `EXPENSE_DB` environment variables to override defaults.
