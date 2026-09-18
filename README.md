# Enterprise GenAI adoption analytics (synthetic)

**Personal project — Ishan Moudgil, 2026**

Product-analytics pack for an **AI Business Enablement** intern desk: adoption dashboards, weekly “so what?” readouts, qualitative barriers, and a measurement playbook.

Built to match work like **RBC Borealis / AI enablement data analyst** (usage vs value, phased rollout, GenAI tools). **All data is synthetic.** Not RBC, not production.

## Why it exists

GenAI programs report **seats and sessions**. That hides three things this desk actually cares about:

1. Licensed ≠ activated (rollout quality).
2. High-volume features can be toys (**draft** vs **search**).
3. Consumer ChatGPT/Claude/Gemini set the bar; internal prompt-only products look late.

Planted, checkable findings (seed 42):

- Lagging **activation** in later waves (Retail / Insurance style BUs).
- **Draft** has a worse value-event rate than search / code assist.
- Copy-to-external (shadow IT) is higher where enablement was webinar-only.
- Public **agent** trend index rises faster than enterprise **prompt** index.

## Stack

Python, pandas, **SQL (SQLite as SQL Server/Postgres stand-in)**, Excel charts (Power BI-style storytelling), matplotlib.

```
rbc-genai-adoption-analytics/
├── src/generate_data.py      users, events, interviews, external trends
├── src/build_database.py
├── src/queries.sql           6 enablement questions
├── src/sql_analysis.py
├── src/insights.py           weekly readout + PNG charts
├── src/generate_workbook.py  Excel pack
├── src/run_all.py
├── docs/measurement-playbook.md
├── docs/weekly-readout.md    generated
└── outputs/                  CSV + xlsx + charts
```

```bash
cd rbc-genai-adoption-analytics
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py
open outputs/adoption_dashboard.html
```

Interview prep: `docs/interview-talk-track.md`, `docs/enablement-experiment-memo.md`.

After clone, run `python src/run_all.py` to regenerate `data/` and full `outputs/` (not all artifacts are in git).

## Resume one-liner

Built a synthetic enterprise GenAI adoption warehouse (SQL) tracking license→activate→WAU→time-to-value, wrote a weekly enablement readout that separates session vanity from value events, and documented a repeatable measurement playbook including qualitative barriers and consumer-tool context.
