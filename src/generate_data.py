"""Synthetic enterprise GenAI adoption events, interviews, and external trend notes.

Personal portfolio — not RBC data. Seeded so metrics are reproducible.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

random.seed(42)

BUSINESS_UNITS = [
    "Retail Banking",
    "Capital Markets",
    "Insurance",
    "Technology & Operations",
    "Human Resources",
    "Finance",
]

FEATURES = [
    ("summarize", "Document summarize"),
    ("draft", "Email / memo draft"),
    ("search", "Policy / knowledge search"),
    ("code_assist", "Internal code assist"),
    ("meeting_notes", "Meeting notes"),
]

# Wave start offsets (days from 2026-01-06) — phased rollout
WAVE_START = {
    "Technology & Operations": 0,
    "Finance": 21,
    "Human Resources": 35,
    "Retail Banking": 49,
    "Capital Markets": 63,
    "Insurance": 77,
}

N_USERS = 420
START = date(2026, 1, 6)
END = date(2026, 9, 7)  # ~35 weeks of history for a winter-2027 interview story


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def build_users() -> list[dict]:
    rows = []
    uid = 1
    for bu in BUSINESS_UNITS:
        n = {
            "Technology & Operations": 110,
            "Finance": 70,
            "Human Resources": 50,
            "Retail Banking": 80,
            "Capital Markets": 60,
            "Insurance": 50,
        }[bu]
        for _ in range(n):
            wave = WAVE_START[bu]
            licensed = START + timedelta(days=wave + random.randint(0, 14))
            # 18% never activate after license (adoption barrier)
            # Webinar-only vs local-champion huddle (A/B on rollout motion)
            enablement_arm = random.choice(["webinar", "huddle"])
            activate_p = 0.82 if enablement_arm == "huddle" else 0.72
            will_activate = random.random() < activate_p
            rows.append(
                {
                    "user_id": f"U{uid:04d}",
                    "business_unit": bu,
                    "licensed_on": licensed.isoformat(),
                    "will_activate": int(will_activate),
                    "enablement_arm": enablement_arm,
                    "sticky": int(random.random() > 0.35),
                    "role": random.choice(
                        ["analyst", "manager", "ops", "engineer", "advisor"]
                    ),
                }
            )
            uid += 1
    return rows[:N_USERS]


def first_value_event_day(
    licensed: date, feature: str, bu: str, enablement_arm: str
) -> date | None:
    """Time-to-value: first session that is not a throwaway draft."""
    base = {
        "search": 3,
        "summarize": 5,
        "meeting_notes": 7,
        "code_assist": 4,
        "draft": 12,  # high volume, slower "value" — planted finding
    }[feature]
    if bu in ("Retail Banking", "Insurance"):
        base += 6  # training lag
    if bu == "Technology & Operations":
        base = max(1, base - 2)
    if enablement_arm == "huddle":
        base = max(1, base - 5)
    lag = max(1, int(random.gauss(base, 3)))
    return licensed + timedelta(days=lag)


def build_events(users: list[dict]) -> list[dict]:
    events = []
    eid = 1
    for u in users:
        if not u["will_activate"]:
            continue
        licensed = date.fromisoformat(u["licensed_on"])
        bu = u["business_unit"]
        sticky = bool(u.get("sticky", 1))
        arm = u.get("enablement_arm", "webinar")
        first_value_seen: date | None = None
        # Feature mix by BU
        weights = {
            "Technology & Operations": [0.15, 0.2, 0.15, 0.4, 0.1],
            "Finance": [0.25, 0.35, 0.25, 0.05, 0.1],
            "Human Resources": [0.2, 0.4, 0.2, 0.0, 0.2],
            "Retail Banking": [0.2, 0.45, 0.2, 0.0, 0.15],
            "Capital Markets": [0.3, 0.25, 0.3, 0.05, 0.1],
            "Insurance": [0.25, 0.35, 0.25, 0.0, 0.15],
        }[bu]
        # Prefer 2–3 features per user
        feats = [f[0] for f in FEATURES]
        chosen = random.sample(feats, k=random.choice([2, 3]))
        ttv_dates = {}
        for feat in chosen:
            ttv_dates[feat] = first_value_event_day(licensed, feat, bu, arm)

        for day in daterange(licensed, END):
            if day.weekday() >= 5:
                continue
            weeks_in = (day - licensed).days / 7
            # Adoption curve: ramp then plateau; draft stays noisy
            p_session = min(0.55, 0.08 + weeks_in * 0.06)
            if bu in ("Retail Banking", "Insurance"):
                p_session *= 0.72
            if arm == "huddle" and weeks_in < 4:
                p_session = min(0.62, p_session * 1.15)
            if random.random() > p_session:
                continue
            if first_value_seen and not sticky:
                if (day - first_value_seen).days > 14:
                    continue
            feat = random.choices(chosen, weights=[weights[feats.index(f)] + 0.05 for f in chosen])[0]
            # Value event: search/summarize more often "completed task"
            is_value = False
            if feat in ("search", "code_assist", "summarize"):
                is_value = True
            elif feat == "meeting_notes":
                is_value = random.random() < 0.48
            elif feat == "draft":
                is_value = random.random() < 0.22
            if day < ttv_dates[feat]:
                is_value = False
            if is_value and first_value_seen is None:
                first_value_seen = day
            duration = max(1, int(random.gauss(8 if is_value else 3, 2)))
            events.append(
                {
                    "event_id": eid,
                    "user_id": u["user_id"],
                    "event_date": day.isoformat(),
                    "feature": feat,
                    "is_value_event": int(is_value),
                    "session_minutes": duration,
                    "copied_to_external": int(
                        random.random() < (0.11 if bu in ("Retail Banking", "Insurance") else 0.04)
                    ),
                }
            )
            eid += 1
    return events


def build_interviews() -> list[dict]:
    notes = [
        (
            "Retail Banking",
            "barrier",
            "Advisors paste client emails into consumer ChatGPT because internal search feels slower and they are unsure what is classified.",
        ),
        (
            "Retail Banking",
            "success",
            "One branch ops lead cut weekly policy lookup from ~40 minutes to under 10 using knowledge search after a 20-minute huddle.",
        ),
        (
            "Insurance",
            "barrier",
            "Fear of putting claim narrative into any model. Training did not cover 'what is in-policy vs out.'",
        ),
        (
            "Technology & Operations",
            "success",
            "Code assist is the default for boilerplate tests. Time-to-first-value under a week for most engineers in the wave.",
        ),
        (
            "Technology & Operations",
            "barrier",
            "Draft is used as a toy. High session counts, low 'I shipped the email' follow-through.",
        ),
        (
            "Finance",
            "success",
            "Summarize on long vendor PDFs is the story leadership wants: measurable hours back in close week.",
        ),
        (
            "Finance",
            "barrier",
            "Managers want a PowerPoint-ready weekly pack. Raw usage counts do not answer so-what.",
        ),
        (
            "Human Resources",
            "success",
            "Meeting notes on skip-levels; repeat use after the second week.",
        ),
        (
            "Capital Markets",
            "barrier",
            "Policy search must cite source. Hallucinated clause = they abandon the tool for a week.",
        ),
        (
            "Capital Markets",
            "success",
            "Research associates use summarize on public filings only; clear boundary increased trust.",
        ),
        (
            "Insurance",
            "success",
            "A small cohort who got a 1-page 'allowed data' card started using search within 5 days.",
        ),
        (
            "Retail Banking",
            "barrier",
            "Go-live event was a webinar. No local champion. Activation lagged 3 weeks behind license date.",
        ),
    ]
    rows = []
    for i, (bu, kind, text) in enumerate(notes, start=1):
        rows.append(
            {
                "interview_id": f"INT-{i:02d}",
                "business_unit": bu,
                "theme_type": kind,
                "week_ending": (START + timedelta(days=7 * (8 + i))).isoformat(),
                "note": text,
            }
        )
    return rows


def build_external_trends() -> list[dict]:
    """Weekly public-tool narrative vs internal (synthetic indices)."""
    rows = []
    week = START
    t = 0
    while week < END:
        # Consumer 'agent' buzz rises faster than enterprise prompt-only
        consumer_agent = min(100, 20 + t * 2.1)
        consumer_chat = min(100, 55 + t * 0.8)
        enterprise_prompt = min(100, 30 + t * 1.1)
        rows.append(
            {
                "week_ending": week.isoformat(),
                "consumer_chat_index": round(consumer_chat, 1),
                "consumer_agent_index": round(consumer_agent, 1),
                "enterprise_prompt_index": round(enterprise_prompt, 1),
                "note": (
                    "Public tools shipping agent workflows; internal product still prompt-and-paste."
                    if t > 12
                    else "Consumer ChatGPT/Claude usage stable; enterprise still in prompt era."
                ),
            }
        )
        week += timedelta(days=7)
        t += 1
    return rows


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    users = build_users()
    events = build_events(users)
    write_csv(
        DATA / "users.csv",
        users,
        [
            "user_id",
            "business_unit",
            "licensed_on",
            "will_activate",
            "enablement_arm",
            "sticky",
            "role",
        ],
    )
    write_csv(
        DATA / "events.csv",
        events,
        [
            "event_id",
            "user_id",
            "event_date",
            "feature",
            "is_value_event",
            "session_minutes",
            "copied_to_external",
        ],
    )
    write_csv(
        DATA / "features.csv",
        [{"feature_id": a, "feature_name": b} for a, b in FEATURES],
        ["feature_id", "feature_name"],
    )
    write_csv(
        DATA / "interviews.csv",
        build_interviews(),
        ["interview_id", "business_unit", "theme_type", "week_ending", "note"],
    )
    write_csv(
        DATA / "external_trends.csv",
        build_external_trends(),
        [
            "week_ending",
            "consumer_chat_index",
            "consumer_agent_index",
            "enterprise_prompt_index",
            "note",
        ],
    )
    print(f"Wrote {len(users)} users, {len(events)} events to {DATA}")


if __name__ == "__main__":
    main()
