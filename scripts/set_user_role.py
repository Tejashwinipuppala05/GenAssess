from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone

from dotenv import load_dotenv

from src.auth.database import connect_database, initialize_database
from src.auth.models import UserRole

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign a GenAssess account role.")
    parser.add_argument("email", help="Email address of an existing account")
    parser.add_argument("role", choices=[role.value for role in UserRole])
    arguments = parser.parse_args()

    initialize_database()
    connection = connect_database()
    try:
        with connection:
            cursor = connection.execute(
                "UPDATE users SET role = ?, updated_at = ? WHERE email = ?",
                (
                    arguments.role,
                    datetime.now(timezone.utc).isoformat(),
                    arguments.email.strip().lower(),
                ),
            )
            if cursor.rowcount == 0:
                parser.error("No account found for that email.")
    except sqlite3.Error as exc:
        parser.error(f"Could not update the account role: {exc}")
    finally:
        connection.close()

    print(f"Updated {arguments.email} to {arguments.role}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
