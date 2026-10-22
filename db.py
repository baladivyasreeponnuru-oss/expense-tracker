import os
import sqlite3

DB_PATH = os.environ.get("EXPENSE_DB", "expenses.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                date     TEXT NOT NULL,
                type     TEXT NOT NULL CHECK(type IN ('income','expense')),
                category TEXT NOT NULL,
                amount   REAL NOT NULL CHECK(amount > 0),
                note     TEXT
            )
            """
        )


def add_transaction(date, type_, category, amount, note=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO transactions (date, type, category, amount, note) VALUES (?,?,?,?,?)",
            (date, type_, category, amount, note),
        )


def delete_transaction(tx_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
