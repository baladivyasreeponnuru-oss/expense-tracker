import io
import os
from datetime import date, datetime

import pandas as pd
from flask import (Flask, flash, redirect, render_template, request,
                   send_file, url_for)

import analysis
import charts
import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

db.init_db()

CATEGORIES = ["Food", "Rent", "Transport", "Bills", "Shopping",
              "Health", "Entertainment", "Salary", "Other"]


@app.route("/")
def index():
    month = request.args.get("month") or None  # e.g. 2026-10
    full = analysis.load_df()
    df = full[full["month"] == month] if (month and not full.empty) else full
    all_months = sorted(full["month"].unique(), reverse=True) if not full.empty else []
    return render_template(
        "index.html",
        rows=df.to_dict("records"),
        totals=analysis.summary(df),
        months=all_months,
        selected=month,
        categories=CATEGORIES,
        today=date.today().isoformat(),
    )


@app.route("/add", methods=["POST"])
def add():
    try:
        amount = float(request.form["amount"])
        if amount <= 0:
            raise ValueError
    except (ValueError, KeyError):
        flash("Amount must be a positive number.")
        return redirect(url_for("index"))

    tx_date = request.form.get("date", "")
    try:
        datetime.strptime(tx_date, "%Y-%m-%d")
    except ValueError:
        flash("Date must be in YYYY-MM-DD format.")
        return redirect(url_for("index"))

    type_ = request.form.get("type")
    if type_ not in ("income", "expense"):
        flash("Type must be income or expense.")
        return redirect(url_for("index"))

    db.add_transaction(
        tx_date, type_, request.form.get("category", "Other"),
        amount, request.form.get("note", ""),
    )
    return redirect(url_for("index"))


@app.route("/delete/<int:tx_id>", methods=["POST"])
def delete(tx_id):
    db.delete_transaction(tx_id)
    return redirect(url_for("index"))


# ---------- charts ----------
@app.route("/chart/pie.png")
def pie():
    df = analysis.load_df(request.args.get("month") or None)
    return send_file(charts.pie_chart(analysis.expense_by_category(df)),
                     mimetype="image/png")


@app.route("/chart/bar.png")
def bar():
    df = analysis.load_df()  # bar chart always shows all months
    return send_file(charts.bar_chart(analysis.monthly_totals(df)),
                     mimetype="image/png")


# ---------- exports ----------
@app.route("/export/csv")
def export_csv():
    df = analysis.load_df(request.args.get("month") or None)
    buf = io.BytesIO(
        df.drop(columns=["month"], errors="ignore").to_csv(index=False).encode()
    )
    return send_file(buf, mimetype="text/csv", as_attachment=True,
                     download_name="expenses.csv")


@app.route("/export/xlsx")
def export_xlsx():
    df = analysis.load_df(request.args.get("month") or None)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        out = df.drop(columns=["month"], errors="ignore")
        out.to_excel(xw, sheet_name="Transactions", index=False)
        analysis.monthly_totals(analysis.load_df()).to_excel(xw, sheet_name="Monthly summary")
        analysis.expense_by_category(df).to_frame("amount").to_excel(xw, sheet_name="By category")
    buf.seek(0)
    return send_file(
        buf, as_attachment=True, download_name="expense_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(debug=True)
