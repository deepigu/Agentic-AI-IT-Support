
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Locate the existing database
DB_PATH = (
    Path(__file__).resolve().parent
    / "backend"
    / "app"
    / "it_support.db"
)

if not DB_PATH.is_file():
    raise FileNotFoundError(
        f"Database not found: {DB_PATH}"
    )

# Create a backup before changing the database
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = DB_PATH.with_name(
    f"it_support_backup_{timestamp}.db"
)

# Connect and inspect the existing table
with sqlite3.connect(DB_PATH) as connection:
    tables = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name='support_tickets'"
    ).fetchone()

    if tables is None:
        raise RuntimeError(
            "support_tickets table does not exist."
        )

    columns = [
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(support_tickets)"
        ).fetchall()
    ]

    if "priority" in columns:
        print("Priority column already exists.")
    else:
        # SQLite's backup API creates a consistent backup
        with sqlite3.connect(backup_path) as backup:
            connection.backup(backup)

        print(f"Backup created: {backup_path}")

        connection.execute(
            "ALTER TABLE support_tickets "
            "ADD COLUMN priority VARCHAR(20) "
            "NOT NULL DEFAULT 'Medium'"
        )

        connection.commit()
        print("Priority column added successfully!")

    ticket_count = connection.execute(
        "SELECT COUNT(*) FROM support_tickets"
    ).fetchone()[0]

    print(f"Existing tickets preserved: {ticket_count}")

    print("\nCurrent database columns:")
    for row in connection.execute(
        "PRAGMA table_info(support_tickets)"
    ):
        print(f"- {row[1]}")
