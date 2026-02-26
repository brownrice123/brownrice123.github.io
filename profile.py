#!/usr/bin/env python3
"""Profile GroceryTrackerData.xlsx and write summary to report.md."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def format_percent(value: float) -> str:
    return f"{value:.2f}%"


def build_report(df: pd.DataFrame, source_name: str) -> str:
    row_count = len(df)
    col_count = len(df.columns)

    lines: list[str] = []
    lines.append("# Data Profile Report")
    lines.append("")
    lines.append(f"**Source file:** `{source_name}`")
    lines.append(f"**Row count:** {row_count}")
    lines.append(f"**Column count:** {col_count}")
    lines.append("")

    lines.append("## Column Summary")
    lines.append("")
    lines.append("| Column | Data Type | Percent Nulls |")
    lines.append("|---|---|---:|")

    null_percentages = (df.isnull().mean() * 100).to_dict()
    for column in df.columns:
        dtype = str(df[column].dtype)
        pct_nulls = format_percent(float(null_percentages[column]))
        lines.append(f"| {column} | {dtype} | {pct_nulls} |")

    lines.append("")
    lines.append("## Top 5 Distinct Values by Column")
    lines.append("")

    for column in df.columns:
        lines.append(f"### {column}")
        non_null_series = df[column].dropna()

        if non_null_series.empty:
            lines.append("")
            lines.append("No non-null values found.")
            lines.append("")
            continue

        value_counts = non_null_series.astype(str).value_counts().head(5)

        lines.append("")
        lines.append("| Value | Count |")
        lines.append("|---|---:|")
        for value, count in value_counts.items():
            safe_value = value.replace("|", r"\|")
            lines.append(f"| {safe_value} | {int(count)} |")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Profile an Excel file and write Markdown report."
    )
    parser.add_argument(
        "--input",
        default="GroceryTrackerData.xlsx",
        help="Input Excel file path (default: GroceryTrackerData.xlsx)",
    )
    parser.add_argument(
        "--output",
        default="report.md",
        help="Output Markdown report path (default: report.md)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_excel(input_path)
    report_content = build_report(df, input_path.name)
    output_path.write_text(report_content, encoding="utf-8")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
