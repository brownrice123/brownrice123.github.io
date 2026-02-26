from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    db_path = Path(__file__).resolve().parent / "sample.db"
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE companies (
                company_id INTEGER,
                company_name TEXT NOT NULL,
                segment TEXT NOT NULL
            );

            CREATE TABLE leads (
                lead_id INTEGER,
                company_id INTEGER,
                email TEXT,
                segment TEXT
            );
            """
        )

        conn.executemany(
            "INSERT INTO companies (company_id, company_name, segment) VALUES (?, ?, ?)",
            [
                (1, "Acme Inc", "SMB"),
                (2, "Globex Corp", "Enterprise"),
                (3, "Initech", "Mid-Market"),
            ],
        )

        conn.executemany(
            "INSERT INTO leads (lead_id, company_id, email, segment) VALUES (?, ?, ?, ?)",
            [
                (1001, 1, "owner@acme.com", "SMB"),
                (1002, 2, None, "Enterprise"),  # not_null fail
                (1002, 2, "sales@globex.com", "Enterprise"),  # unique fail
                (1004, 99, "unknown@orphan.com", "SMB"),  # relationship fail
                (1005, 3, "contact@initech.com", "Startup"),  # accepted_values fail
            ],
        )

    print(f"Created sample database at {db_path}")


if __name__ == "__main__":
    main()
