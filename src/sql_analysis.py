"""Run SQL business questions and save result tables."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "genai_adoption.db"
OUT = ROOT / "outputs"
SQL = (ROOT / "src" / "queries.sql").read_text(encoding="utf-8")


def split_queries(sql: str) -> list[str]:
    parts = []
    buf: list[str] = []
    for line in sql.splitlines():
        if line.strip().startswith("--") and buf:
            parts.append("\n".join(buf).strip())
            buf = []
        buf.append(line)
    if buf:
        parts.append("\n".join(buf).strip())
    return [p for p in parts if "SELECT" in p.upper()]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    names = [
        "funnel_activation",
        "weekly_usage",
        "feature_value_rate",
        "ttv_by_bu",
        "shadow_it",
        "repeat_use",
    ]
    queries = split_queries(SQL)
    for name, q in zip(names, queries):
        df = pd.read_sql_query(q, con)
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows")
    con.close()


if __name__ == "__main__":
    main()
