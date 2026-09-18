# Enterprise GenAI adoption analytics (synthetic)

**Personal project — Ishan Moudgil, 2026**

Product-analytics sample for **enterprise GenAI enablement**: adoption dashboards, weekly “so what?” readouts, qualitative user-research themes, and a measurement playbook.

**All data is synthetic.** Not based on any employer or production system.

## Why it exists

GenAI programs often report **seats and sessions**. This project models three gaps that matter for enablement teams:

1. Licensed ≠ activated (rollout quality).
2. High-volume features can be toys (**draft** vs **search**).
3. Consumer ChatGPT/Claude/Gemini set expectations; internal tools need grounded metrics.

Planted, checkable findings (seed 42):

- Lagging **activation** in later rollout waves.
- **Draft** with a lower value-event rate than search / code assist.
- Higher copy-to-external (shadow IT proxy) where enablement was webinar-only.
- Public **agent** trend index rising faster than enterprise **prompt** index.

## Stack

Python, pandas, **SQL** (SQLite warehouse), Excel, matplotlib, Plotly.

```
rbc-genai-adoption-analytics/
├── src/                 pipeline: generate → SQL → readout → dashboard
├── docs/                playbook, sample readout, experiment memo
└── outputs/             dashboard HTML, CSV summaries, Excel pack
```

## Quick start

```bash
cd rbc-genai-adoption-analytics
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py
open outputs/adoption_dashboard.html
```

## Documentation

- [`docs/measurement-playbook.md`](docs/measurement-playbook.md) — metric definitions and weekly cadence
- [`docs/weekly-readout.md`](docs/weekly-readout.md) — sample readout for product / enablement stakeholders
- [`docs/enablement-experiment-memo.md`](docs/enablement-experiment-memo.md) — webinar vs huddle A/B on time-to-first-value

Regenerate `data/` and full outputs with `python src/run_all.py` after clone.
