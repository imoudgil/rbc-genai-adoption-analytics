"""Export Power BI-ready CSVs and a static dashboard preview PNG."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
PBI = OUT / "powerbi"
DOCS_IMG = ROOT / "docs" / "images"


def _weekly_ttv(events: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    first_value = (
        events.loc[events["is_value_event"] == 1]
        .groupby("user_id")["event_date"]
        .min()
        .rename("first_value_date")
    )
    u = users.merge(first_value.reset_index(), on="user_id")
    u = u.dropna(subset=["first_value_date"])
    u["licensed_on"] = pd.to_datetime(u["licensed_on"])
    u["first_value_date"] = pd.to_datetime(u["first_value_date"])
    u["ttv_days"] = (u["first_value_date"] - u["licensed_on"]).dt.days
    u["cohort_week"] = u["licensed_on"].dt.to_period("W").astype(str)
    weekly = (
        u.groupby("cohort_week", as_index=False)["ttv_days"]
        .agg(median_ttv_days="median", mean_ttv_days="mean", n_users="count")
        .sort_values("cohort_week")
    )
    return weekly


def _weekly_tokens(events: pd.DataFrame) -> pd.DataFrame:
    e = events.copy()
    e["event_date"] = pd.to_datetime(e["event_date"])
    e["year_week"] = e["event_date"].dt.strftime("%Y-%W")
    e["est_tokens"] = (e["session_minutes"].clip(lower=1) * 850).astype(int)
    e["est_cost_usd"] = e["est_tokens"] * 0.000002
    return (
        e.groupby("year_week", as_index=False)
        .agg(
            week_start=("event_date", "min"),
            sessions=("event_id", "count"),
            est_tokens=("est_tokens", "sum"),
            est_cost_usd=("est_cost_usd", "sum"),
        )
        .sort_values("week_start")
    )


def _feature_miss_rate() -> pd.DataFrame:
    feat = pd.read_csv(OUT / "feature_value_rate.csv")
    feat["miss_rate_pct"] = (100 - feat["value_rate_pct"]).round(1)
    return feat


def _render_preview(
    weekly_ttv: pd.DataFrame,
    weekly_tokens: pd.DataFrame,
    feat: pd.DataFrame,
    exp: pd.DataFrame,
) -> Path:
    DOCS_IMG.mkdir(parents=True, exist_ok=True)
    plt.style.use("ggplot")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    fig.patch.set_facecolor("#F3F2F1")
    fig.suptitle(
        "Enterprise GenAI adoption — Power BI sample",
        fontsize=13,
        fontweight="bold",
        color="#252423",
        y=1.02,
    )

    ax0 = axes[0]
    x = range(len(weekly_ttv))
    ax0.plot(x, weekly_ttv["median_ttv_days"], color="#118DFF", linewidth=2.5, marker="o", markersize=4)
    ax0.set_title("Time-to-first-value (median days)", fontsize=10, fontweight="bold")
    ax0.set_ylabel("Days")
    ax0.set_xlabel("License cohort week")
    ax0.grid(True, alpha=0.35)

    ax1 = axes[1]
    ax1.bar(
        range(len(weekly_tokens)),
        weekly_tokens["est_tokens"] / 1000,
        color="#F2C811",
        edgecolor="#252423",
        linewidth=0.3,
    )
    ax1.set_title("Estimated token volume (000s)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Tokens (thousands)")
    ax1.set_xlabel("Usage week")
    ax1.grid(True, axis="y", alpha=0.35)

    ax2 = axes[2]
    labels = [n.replace(" ", "\n") for n in feat["feature_name"]]
    ax2.barh(labels, feat["miss_rate_pct"], color="#E74856")
    ax2.set_title("Non-value session rate by feature", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Miss rate (%)")
    ax2.invert_yaxis()
    ax2.grid(True, axis="x", alpha=0.35)

    fig.text(
        0.5,
        -0.02,
        f"Enablement A/B: webinar mean TTV {exp.loc[exp['arm']=='webinar','mean_ttv_days'].iloc[0]:.1f}d "
        f"vs huddle {exp.loc[exp['arm']=='huddle','mean_ttv_days'].iloc[0]:.1f}d (Welch p={exp['p_value'].iloc[0]:.3f})",
        ha="center",
        fontsize=9,
        color="#605E5C",
    )
    plt.tight_layout()
    path = DOCS_IMG / "adoption_powerbi_dashboard.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def main() -> None:
    PBI.mkdir(parents=True, exist_ok=True)
    events = pd.read_csv(DATA / "events.csv")
    users = pd.read_csv(DATA / "users.csv")

    weekly_ttv = _weekly_ttv(events, users)
    weekly_tokens = _weekly_tokens(events)
    feat = _feature_miss_rate()

    weekly_ttv.to_csv(PBI / "time_to_first_value_by_cohort.csv", index=False)
    weekly_tokens.to_csv(PBI / "weekly_token_usage.csv", index=False)
    feat.to_csv(PBI / "feature_quality_miss_rate.csv", index=False)
    pd.read_csv(OUT / "weekly_usage.csv").to_csv(PBI / "weekly_adoption_usage.csv", index=False)

    with open(OUT / "enablement_experiment.json") as f:
        import json

        j = json.load(f)
    exp = pd.DataFrame(
        [
            {"arm": "webinar", "mean_ttv_days": j["webinar"]["mean_ttv_days"], "n": j["webinar"]["n"]},
            {"arm": "huddle", "mean_ttv_days": j["huddle"]["mean_ttv_days"], "n": j["huddle"]["n"]},
        ]
    )
    exp["p_value"] = j["welch_ttest_ttv"]["p"]
    exp.to_csv(PBI / "enablement_ab_summary.csv", index=False)

    png = _render_preview(weekly_ttv, weekly_tokens, feat, exp)
    print(f"Wrote Power BI CSVs under {PBI}")
    print(f"Wrote preview {png}")


if __name__ == "__main__":
    main()
