"""Weekly 'so what' readout + charts from SQL outputs and interviews."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DOCS = ROOT / "docs"
CHARTS = OUT / "charts"


def write_readout() -> None:
    funnel = pd.read_csv(OUT / "funnel_activation.csv")
    ttv = pd.read_csv(OUT / "ttv_by_bu.csv")
    feat = pd.read_csv(OUT / "feature_value_rate.csv")
    shadow = pd.read_csv(OUT / "shadow_it.csv")
    weekly = pd.read_csv(OUT / "weekly_usage.csv")
    interviews = pd.read_csv(ROOT / "data" / "interviews.csv")
    trends = pd.read_csv(ROOT / "data" / "external_trends.csv")
    exp_path = OUT / "enablement_experiment.json"
    exp_line = ""
    if exp_path.exists():
        import json

        exp = json.loads(exp_path.read_text(encoding="utf-8"))
        exp_line = (
            f"- Enablement A/B: **huddle** mean TTV **{exp['huddle']['mean_ttv_days']}** days vs "
            f"**webinar {exp['webinar']['mean_ttv_days']}** "
            f"({exp['huddle']['pct_within_14d']}% vs {exp['webinar']['pct_within_14d']}% reach value within 14d, p={exp['welch_ttest_ttv']['p']})\n"
        )

    worst_act = funnel.sort_values("activation_pct").iloc[0]
    slow_ttv = ttv.sort_values("mean_ttv_days").iloc[-1]
    low_value_feat = feat.sort_values("value_rate_pct").iloc[0]
    high_value_feat = feat.sort_values("value_rate_pct").iloc[-1]
    worst_shadow = shadow.sort_values("pct_sessions_copied_external").iloc[-1]
    last_wau = weekly.iloc[-1]
    last_trend = trends.iloc[-1]
    barriers = interviews[interviews["theme_type"] == "barrier"]["note"].head(3).tolist()

    lines = f"""# Weekly GenAI adoption readout (synthetic)

**To:** AI Business Enablement / Product  
**From:** Data Analyst (portfolio simulation)  
**Re:** Usage vs value, rollout gaps, external context  
**Data:** Synthetic enterprise GenAI assistant — {int(funnel['licensed_users'].sum())} licensed seats.

---

## Three decisions

| Question | Recommendation | Why |
|----------|----------------|-----|
| Where is adoption stalling? | Put a **local champion + 20-min huddle** in **{worst_act['business_unit']}** (activation **{worst_act['activation_pct']}%**) | License is not use. Same pattern in interviews: webinar-only go-live. |
| Are we measuring the right thing? | Stop celebrating **{low_value_feat['feature_name']}** session volume. Report **value-event rate** (now **{low_value_feat['value_rate_pct']}%** vs **{high_value_feat['feature_name']}** at **{high_value_feat['value_rate_pct']}%**) | High usage, low completed work. |
| What is the external so-what? | Consumer **agent** index is **{last_trend['consumer_agent_index']}** vs enterprise prompt index **{last_trend['enterprise_prompt_index']}**. Brief product on **grounded search + citations** before 'agents.' | Users already compare us to ChatGPT/Claude. |

---

## This week's numbers

- Last complete week WAU: **{int(last_wau['wau'])}**; value events: **{int(last_wau['value_events'])}**
- Slowest time-to-first-value: **{slow_ttv['business_unit']}** (**{slow_ttv['mean_ttv_days']}** days from license)
- Highest copy-to-external (shadow IT proxy): **{worst_shadow['business_unit']}** (**{worst_shadow['pct_sessions_copied_external']}%** of sessions)
{exp_line}
## Qualitative (user research)

"""
    for b in barriers:
        lines += f"- Barrier: {b}\n"
    lines += """
## Implications for enablement

1. **Measurement playbook:** WAU is a hygiene metric. Primary KPI = % licensed who reach a value event in 14 days; secondary = 7-day repeat value.
2. **Rollout:** Pair license date with a floor huddle in lagging BUs; webinar-only waves under-activate.
3. **Product:** Draft is a funnel top. Search/summarize create the stories leadership can take to BUs.
4. **Risk:** Copy-to-external is an enablement + policy problem, not only a model problem.

All figures are **synthetic** (seed=42) so methods can be checked.
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "weekly-readout.md").write_text(lines, encoding="utf-8")
    (OUT / "weekly-readout.md").write_text(lines, encoding="utf-8")
    print("Wrote weekly readout")


def charts() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    weekly = pd.read_csv(OUT / "weekly_usage.csv")
    feat = pd.read_csv(OUT / "feature_value_rate.csv")
    funnel = pd.read_csv(OUT / "funnel_activation.csv")

    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(weekly["week_start"], weekly["wau"], label="WAU")
    ax.plot(weekly["week_start"], weekly["value_events"], label="Value events")
    ax.set_title("Adoption curve: WAU vs value events (synthetic)")
    ax.legend()
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(CHARTS / "adoption_curve.png", dpi=140)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(feat["feature_name"], feat["value_rate_pct"])
    ax.set_xlabel("Value-event rate (%)")
    ax.set_title("Feature quality: sessions that complete work")
    fig.tight_layout()
    fig.savefig(CHARTS / "feature_value_rate.png", dpi=140)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(funnel["business_unit"], funnel["activation_pct"])
    ax.set_xlabel("Activated / licensed (%)")
    ax.set_title("Phased rollout: activation by business unit")
    fig.tight_layout()
    fig.savefig(CHARTS / "activation_by_bu.png", dpi=140)
    plt.close()
    print(f"Wrote charts to {CHARTS}")


def main() -> None:
    write_readout()
    charts()


if __name__ == "__main__":
    main()
