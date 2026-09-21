"""End-to-end: generate → warehouse → SQL → readout → Excel."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import build_dashboard
import build_powerbi_dashboard
import build_database
import experiment_analysis
import generate_data
import generate_workbook
import insights
import sql_analysis


def main() -> None:
    generate_data.main()
    build_database.main()
    sql_analysis.main()
    experiment_analysis.main()
    insights.main()
    generate_workbook.main()
    build_dashboard.main()
    build_powerbi_dashboard.main()
    print("Done. Open outputs/adoption_dashboard.html for demo.")


if __name__ == "__main__":
    main()
