"""Load CSVs into SQLite (stand-in for SQL Server / Postgres)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB = DATA / "genai_adoption.db"


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    for name in ["users", "events", "features", "interviews", "external_trends"]:
        df = pd.read_csv(DATA / f"{name}.csv")
        df.to_sql(name, con, index=False, if_exists="replace")
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_events_user_date ON events(user_id, event_date)"
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_users_bu ON users(business_unit)")
    con.commit()
    con.close()
    print(f"Built {DB}")


if __name__ == "__main__":
    main()
