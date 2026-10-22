import os
import tempfile

import pytest

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["EXPENSE_DB"] = _tmp.name

import analysis  # noqa: E402
import db  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    with db.get_conn() as conn:
        conn.execute("DROP TABLE IF EXISTS transactions")
    db.init_db()
    yield


def seed():
    db.add_transaction("2026-09-01", "income", "Salary", 50000)
    db.add_transaction("2026-09-05", "expense", "Food", 1200.5)
    db.add_transaction("2026-10-01", "income", "Salary", 52000)
    db.add_transaction("2026-10-03", "expense", "Rent", 15000)
    db.add_transaction("2026-10-04", "expense", "Food", 800)


def test_empty():
    df = analysis.load_df()
    assert analysis.summary(df) == {"income": 0.0, "expense": 0.0, "balance": 0.0}
    assert analysis.expense_by_category(df).empty
    assert analysis.monthly_totals(df).empty


def test_summary_all_and_month():
    seed()
    s = analysis.summary(analysis.load_df())
    assert s["income"] == 102000
    assert s["expense"] == pytest.approx(17000.5)
    s_oct = analysis.summary(analysis.load_df("2026-10"))
    assert s_oct["balance"] == 52000 - 15800


def test_expense_by_category():
    seed()
    cat = analysis.expense_by_category(analysis.load_df())
    assert cat.index[0] == "Rent"
    assert cat["Food"] == pytest.approx(2000.5)


def test_monthly_totals():
    seed()
    m = analysis.monthly_totals(analysis.load_df())
    assert list(m.index) == ["2026-09", "2026-10"]
    assert m.loc["2026-10", "expense"] == 15800


def test_income_only_month_has_expense_column():
    db.add_transaction("2026-08-01", "income", "Salary", 100)
    m = analysis.monthly_totals(analysis.load_df())
    assert m.loc["2026-08", "expense"] == 0


def test_rejects_bad_amount():
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        db.add_transaction("2026-10-01", "expense", "Food", -5)
