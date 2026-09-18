# Measurement playbook — enterprise GenAI adoption (synthetic)

Use this as the **repeatable** pack AI Business Enablement would run after each BU wave. Figures in this repo are synthetic.

## Metrics (definitions)

| Metric | Definition | Cadence | Owner |
|--------|------------|---------|--------|
| Licensed | Seat provisioned | Daily | Product |
| Activated | ≥1 session | Daily | Enablement |
| WAU | Distinct users with a session in ISO week | Weekly | Analyst |
| Value event | Session tagged `is_value_event=1` (completed task: cited search, shipped draft, merged assist, etc.) | Weekly | Product + analyst |
| Time-to-first-value (TTV) | Days from `licensed_on` to first value event | After each wave | Analyst |
| 7-day repeat | Second value event ≥7 days after first | Monthly | Analyst |
| Shadow IT proxy | Share of sessions flagged copy-to-external | Weekly | Risk + enablement |

**Do not** use session count as the executive KPI. Draft features inflate it.

## Weekly cadence

1. Refresh warehouse (SQL Server / Postgres in production; SQLite here).
2. Run the six SQL questions in `src/queries.sql`.
3. Write a **one-page readout**: three decisions, three numbers, two interview quotes.
4. Send to enablement + product **before** Thursday standup.
5. Log one experiment: huddle vs webinar, or citation-required search vs baseline.

## Qualitative

- 4–6 user conversations per lagging BU per month.
- Tag **barrier** vs **success**. Barriers that repeat twice become a rollout change, not a dashboard footnote.

## External scan (30 minutes)

- Note one consumer GenAI change (ChatGPT / Claude / Gemini) that users will compare us to.
- Ask: does it change our **measurement** (agents vs prompts) or only the **comms**?

## Post go-live (14 days)

- Activation % vs prior wave.
- TTV vs 14-day target.
- Copy-to-external spike → policy card, not a model swap.
