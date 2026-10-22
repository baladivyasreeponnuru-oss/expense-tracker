import io

from matplotlib.figure import Figure


def _to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf


def pie_chart(category_series):
    fig = Figure(figsize=(5, 4))
    ax = fig.subplots()
    if category_series.empty:
        ax.text(0.5, 0.5, "No expenses yet", ha="center", va="center")
        ax.axis("off")
    else:
        ax.pie(
            category_series.values,
            labels=category_series.index,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.set_title("Expenses by category")
    return _to_png(fig)


def bar_chart(monthly_df):
    fig = Figure(figsize=(6, 4))
    ax = fig.subplots()
    if monthly_df.empty:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
        ax.axis("off")
    else:
        monthly_df.plot(kind="bar", ax=ax, color=["#2e9e5b", "#d9534f"])
        ax.set_title("Income vs expense per month")
        ax.set_xlabel("")
        ax.set_ylabel("Amount")
        ax.tick_params(axis="x", rotation=45)
    return _to_png(fig)
