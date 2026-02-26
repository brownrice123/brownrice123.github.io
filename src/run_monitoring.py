from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

SQL_PATH = Path('sql/anomalies.sql')
OUTPUT_DIR = Path('outputs')
FLAGGED_PATH = OUTPUT_DIR / 'flagged_days.csv'
REPORT_PATH = OUTPUT_DIR / 'anomaly_report.md'


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def likely_interpretation(flagged: pd.DataFrame) -> str:
    if flagged.empty:
        return "No anomalies were detected at the current 30% threshold."

    spikes = flagged[flagged['deviation'] > 0]
    drops = flagged[flagged['deviation'] < 0]
    parts: list[str] = []

    if not spikes.empty:
        biggest_spike = spikes.loc[spikes['deviation'].idxmax()]
        parts.append(
            f"Detected {len(spikes)} spike anomaly(ies); largest spike was on "
            f"{biggest_spike['date']} at {format_pct(float(biggest_spike['deviation']))} above baseline."
        )

    if not drops.empty:
        biggest_drop = drops.loc[drops['deviation'].idxmin()]
        parts.append(
            f"Detected {len(drops)} drop anomaly(ies); largest drop was on "
            f"{biggest_drop['date']} at {format_pct(abs(float(biggest_drop['deviation'])))} below baseline."
        )

    return " ".join(parts)


def build_report(all_days: pd.DataFrame, flagged: pd.DataFrame) -> str:
    start_date = all_days['date'].min()
    end_date = all_days['date'].max()

    lines: list[str] = [
        "# Metric Anomaly Report",
        "",
        f"- **Time range:** {start_date} to {end_date}",
        f"- **Total days:** {len(all_days)}",
        f"- **Total anomalies:** {len(flagged)}",
        "",
        "## Anomalies",
        "",
    ]

    if flagged.empty:
        lines.append("No anomalies found.")
    else:
        lines.extend([
            "| Date | Value | Baseline (7d) | Deviation |",
            "|---|---:|---:|---:|",
        ])
        for _, row in flagged.iterrows():
            lines.append(
                f"| {row['date']} | {row['metric_value']:.2f} | {row['baseline_7d']:.2f} | {format_pct(float(row['deviation']))} |"
            )

    lines.extend([
        "",
        "## Likely interpretation",
        "",
        likely_interpretation(flagged),
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    query = SQL_PATH.read_text(encoding='utf-8')
    with duckdb.connect() as conn:
        all_days = conn.execute(query).fetchdf()

    all_days['date'] = pd.to_datetime(all_days['date']).dt.date
    flagged = all_days[all_days['is_anomaly']].copy()

    flagged.to_csv(FLAGGED_PATH, index=False)
    report = build_report(all_days, flagged)
    REPORT_PATH.write_text(report, encoding='utf-8')

    print(f"Wrote {FLAGGED_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == '__main__':
    main()
