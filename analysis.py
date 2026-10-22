import pandas as pd

from db import get_conn


def load_df(month=None):
    """month format: 'YYYY-MM'. None = all data."""
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM transactions ORDER BY date DESC, id DESC", conn
        )
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")
    if month:
        df = df[df["month"] == month]
    return df


def summary(df):
    if df.empty:
        return {"income": 0.0, "expense": 0.0, "balance": 0.0}
    income = float(df.loc[df["type"] == "income", "amount"].sum())
    expense = float(df.loc[df["type"] == "expense", "amount"].sum())
    return {"income": income, "expense": expense, "balance": income - expense}


def expense_by_category(df):
    if df.empty:
        return pd.Series(dtype=float)
    return (
        df[df["type"] == "expense"]
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )


def monthly_totals(df):
    """Rows = months, columns = income / expense."""
    if df.empty:
        return pd.DataFrame(columns=["income", "expense"])
    pivot = df.pivot_table(
        index="month", columns="type", values="amount", aggfunc="sum", fill_value=0
    )
    return pivot.reindex(columns=["income", "expense"], fill_value=0).sort_index()
