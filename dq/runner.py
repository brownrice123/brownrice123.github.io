from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

VALID_RULES = {"not_null", "unique", "accepted_values", "relationships"}
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class Check:
    name: str
    table: str
    rule: str
    column: str
    values: list[str] | None = None
    ref_table: str | None = None
    ref_column: str | None = None


def quote_ident(name: str) -> str:
    if not IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name}")
    return f'"{name}"'


def load_checks(checks_path: Path) -> list[Check]:
    with checks_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("checks.yaml must contain a top-level object")
    if data.get("database") != "sqlite":
        raise ValueError("Only database: sqlite is supported")

    raw_checks = data.get("checks")
    if not isinstance(raw_checks, list):
        raise ValueError("checks must be a list")

    checks: list[Check] = []
    for idx, raw in enumerate(raw_checks, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"check #{idx} must be an object")

        for field in ("name", "table", "rule", "column"):
            if field not in raw or not isinstance(raw[field], str) or not raw[field].strip():
                raise ValueError(f"check #{idx} missing/invalid '{field}'")

        rule = raw["rule"]
        if rule not in VALID_RULES:
            raise ValueError(f"check #{idx} has invalid rule '{rule}'")

        values = raw.get("values")
        ref_table = raw.get("ref_table")
        ref_column = raw.get("ref_column")

        if rule == "accepted_values":
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                raise ValueError(f"check #{idx} accepted_values requires 'values' as list[str]")
        else:
            values = None

        if rule == "relationships":
            if not isinstance(ref_table, str) or not isinstance(ref_column, str):
                raise ValueError(f"check #{idx} relationships requires ref_table and ref_column")
        else:
            ref_table = None
            ref_column = None

        checks.append(
            Check(
                name=raw["name"],
                table=raw["table"],
                rule=rule,
                column=raw["column"],
                values=values,
                ref_table=ref_table,
                ref_column=ref_column,
            )
        )

    return checks


def build_assertion_query(check: Check) -> tuple[str, list[Any]]:
    t = quote_ident(check.table)
    c = quote_ident(check.column)

    if check.rule == "not_null":
        return f"SELECT * FROM {t} WHERE {c} IS NULL", []

    if check.rule == "unique":
        return (
            f"SELECT * FROM {t} "
            f"WHERE {c} IN ("
            f"SELECT {c} FROM {t} GROUP BY {c} HAVING COUNT(*) > 1"
            f")",
            [],
        )

    if check.rule == "accepted_values":
        values = check.values or []
        placeholders = ", ".join(["?"] * len(values))
        return (
            f"SELECT * FROM {t} WHERE {c} IS NULL OR {c} NOT IN ({placeholders})",
            values,
        )

    if check.rule == "relationships":
        rt = quote_ident(check.ref_table or "")
        rc = quote_ident(check.ref_column or "")
        return (
            f"SELECT * FROM {t} AS child "
            f"WHERE child.{c} IS NOT NULL "
            f"AND NOT EXISTS ("
            f"SELECT 1 FROM {rt} AS parent "
            f"WHERE parent.{rc} = child.{c}"
            f")",
            [],
        )

    raise ValueError(f"Unsupported rule: {check.rule}")


def run_checks(db_path: Path, checks: list[Check]) -> int:
    any_fail = False
    with sqlite3.connect(db_path) as conn:
        for check in checks:
            query, params = build_assertion_query(check)
            rows = conn.execute(query, params).fetchall()
            count = len(rows)
            passed = count == 0
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {check.name} - offending rows: {count}")
            if not passed:
                any_fail = True

    return 1 if any_fail else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SQLite SQL checks as code")
    parser.add_argument("--db", required=True, help="Path to SQLite database")
    parser.add_argument("--checks", required=True, help="Path to checks.yaml")
    args = parser.parse_args()

    db_path = Path(args.db)
    checks_path = Path(args.checks)

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    if not checks_path.exists():
        raise FileNotFoundError(f"Checks file not found: {checks_path}")

    checks = load_checks(checks_path)
    exit_code = run_checks(db_path, checks)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
