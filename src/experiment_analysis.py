"""Enablement A/B: webinar vs local-champion huddle on time-to-first-value."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "genai_adoption.db"
OUT = ROOT / "outputs"
DOCS = ROOT / "docs"


def load_ttv(con: sqlite3.Connection) -> pd.DataFrame:
    q = """
    SELECT
      u.user_id,
      u.enablement_arm,
      u.business_unit,
      u.licensed_on,
      MIN(e.event_date) AS first_value_date
    FROM users u
    JOIN events e ON e.user_id = u.user_id AND e.is_value_event = 1
    WHERE u.will_activate = 1
    GROUP BY u.user_id
    """
    df = pd.read_sql_query(q, con)
    df["ttv_days"] = (
        pd.to_datetime(df["first_value_date"]) - pd.to_datetime(df["licensed_on"])
    ).dt.days
    df["value_within_14d"] = (df["ttv_days"] <= 14).astype(int)
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    df = load_ttv(con)
    con.close()

    arms = {}
    for arm in ("webinar", "huddle"):
        sub = df[df["enablement_arm"] == arm]
        arms[arm] = {
            "n": int(len(sub)),
            "mean_ttv_days": round(float(sub["ttv_days"].mean()), 2),
            "median_ttv_days": round(float(sub["ttv_days"].median()), 2),
            "pct_within_14d": round(100 * float(sub["value_within_14d"].mean()), 1),
        }

    w = df[df["enablement_arm"] == "webinar"]["ttv_days"]
    h = df[df["enablement_arm"] == "huddle"]["ttv_days"]
    t_stat, p_val = stats.ttest_ind(h, w, equal_var=False)

    lift_14d = arms["huddle"]["pct_within_14d"] - arms["webinar"]["pct_within_14d"]
    summary = {
        "primary_metric": "time_to_first_value_days",
        "secondary_metric": "pct_reaching_value_within_14_days",
        "webinar": arms["webinar"],
        "huddle": arms["huddle"],
        "welch_ttest_ttv": {"t": round(float(t_stat), 3), "p": round(float(p_val), 4)},
        "recommendation": (
            "Default to local-champion huddle at license for lagging BUs"
            if lift_14d > 0 and p_val < 0.05
            else "Continue huddle in pilot BUs; webinar ok where activation already high"
        ),
    }

    OUT.joinpath("enablement_experiment.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    df.groupby("enablement_arm").agg(
        users=("user_id", "count"),
        mean_ttv=("ttv_days", "mean"),
        pct_14d=("value_within_14d", "mean"),
    ).to_csv(OUT / "enablement_experiment.csv")

    memo = f"""# Enablement experiment memo (synthetic)

**Design:** At license, users were assigned **webinar-only** vs **20-minute local-champion huddle** (randomized). Primary outcome: **days to first value event**. Secondary: **% reaching value within 14 days**.

## Results

| Arm | n | Mean TTV (days) | % value within 14d |
|-----|---:|----------------:|-------------------:|
| Webinar | {arms['webinar']['n']} | {arms['webinar']['mean_ttv_days']} | {arms['webinar']['pct_within_14d']}% |
| Huddle | {arms['huddle']['n']} | {arms['huddle']['mean_ttv_days']} | {arms['huddle']['pct_within_14d']}% |

Welch t-test on TTV: t = {summary['welch_ttest_ttv']['t']}, p = {summary['welch_ttest_ttv']['p']}.

## So what?

**{summary['recommendation']}.** Webinar scales; huddle buys **activation and faster first value** where BUs are already skeptical (Retail/Insurance interviews). Pair with a one-page “allowed data” card to cut copy-to-external.

Synthetic data (seed 42).
"""
    (DOCS / "enablement-experiment-memo.md").write_text(memo, encoding="utf-8")
    print("Wrote enablement experiment outputs")


if __name__ == "__main__":
    main()
