"""Single-file Plotly dashboard (open adoption_dashboard.html in a browser)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def fig_to_div(fig: go.Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def main() -> None:
    funnel = pd.read_csv(OUT / "funnel_activation.csv")
    weekly = pd.read_csv(OUT / "weekly_usage.csv")
    feat = pd.read_csv(OUT / "feature_value_rate.csv")
    shadow = pd.read_csv(OUT / "shadow_it.csv")
    repeat = pd.read_csv(OUT / "repeat_use.csv")
    exp = json.loads((OUT / "enablement_experiment.json").read_text(encoding="utf-8"))

    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "Activation by business unit",
            "WAU vs value events (weekly)",
            "Value-event rate by feature",
            "Shadow IT proxy (% copy-out)",
            "7-day repeat value rate by BU",
            "Enablement A/B: mean time-to-first-value",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    fig.add_trace(
        go.Bar(
            x=funnel["business_unit"],
            y=funnel["activation_pct"],
            marker_color="#5c2d91",
            name="Activation %",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=weekly["week_start"], y=weekly["wau"], name="WAU", line=dict(color="#5c2d91")),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=weekly["week_start"],
            y=weekly["value_events"],
            name="Value events",
            line=dict(color="#00a3e0"),
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Bar(
            y=feat["feature_name"],
            x=feat["value_rate_pct"],
            orientation="h",
            marker_color="#00a3e0",
            name="Value rate",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=shadow["business_unit"],
            y=shadow["pct_sessions_copied_external"],
            marker_color="#c8102e",
            name="Copy-out %",
        ),
        row=2,
        col=2,
    )
    fig.add_trace(
        go.Bar(
            x=repeat["business_unit"],
            y=repeat["repeat_pct"],
            marker_color="#5c2d91",
            name="Repeat %",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=["Webinar", "Huddle"],
            y=[
                exp["webinar"]["mean_ttv_days"],
                exp["huddle"]["mean_ttv_days"],
            ],
            text=[
                f"{exp['webinar']['pct_within_14d']}% ≤14d",
                f"{exp['huddle']['pct_within_14d']}% ≤14d",
            ],
            textposition="outside",
            marker_color=["#888", "#00a3e0"],
            name="Mean TTV (days)",
        ),
        row=3,
        col=2,
    )

    fig.update_layout(
        title_text="Enterprise GenAI adoption — enablement analytics (synthetic)",
        height=950,
        showlegend=False,
        template="plotly_white",
    )
    fig.update_xaxes(tickangle=-35, row=1, col=1)
    fig.update_xaxes(tickangle=-35, row=2, col=2)
    fig.update_xaxes(tickangle=-35, row=3, col=1)

    html_path = OUT / "adoption_dashboard.html"
    body = fig_to_div(fig)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>GenAI adoption dashboard (synthetic)</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 1.5rem; max-width: 1200px; }}
    .note {{ color: #444; font-size: 0.95rem; margin-bottom: 1rem; }}
  </style>
</head>
<body>
  <p class="note"><strong>Synthetic portfolio data.</strong> Enterprise GenAI enablement metrics: adoption, usage vs value, shadow IT proxy, rollout A/B.</p>
  {body}
</body>
</html>"""
    html_path.write_text(html, encoding="utf-8")
    print(f"Wrote {html_path}")


if __name__ == "__main__":
    main()
