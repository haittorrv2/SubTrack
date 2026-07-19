import sqlite3
from pathlib import Path


# ---------------------------------------------------------------------------
# DATABASE LOCATION
# ---------------------------------------------------------------------------

# This stores subscriptions.db in the same folder as database.py.
import os
import sqlite3
from pathlib import Path


def get_database_path() -> Path:
    """
    Store user data in the current Windows user's local AppData folder.
    """

    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:
        app_data_directory = (
            Path(local_app_data)
            / "SubTrack"
        )
    else:
        app_data_directory = (
            Path.home()
            / ".subtrack"
        )

    app_data_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return app_data_directory / "subscriptions.db"


DATABASE_PATH = get_database_path()


# ---------------------------------------------------------------------------
# CONNECTION
# ---------------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """
    Open and return a connection to the SQLite database.

    row_factory allows rows to be accessed using column names, for example:

        subscription["name"]

    rather than only numerical positions.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enforce SQLite foreign-key rules if relationships are added later.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ---------------------------------------------------------------------------
# DATABASE CREATION
# ---------------------------------------------------------------------------

def create_database() -> None:
    """
    Create the subscriptions table if it does not already exist.

    Running this function does not delete or overwrite existing records.
    """

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                price REAL NOT NULL
                    CHECK (price >= 0),

                billing_frequency TEXT NOT NULL,

                next_renewal_date TEXT NOT NULL,

                reminder_days INTEGER NOT NULL DEFAULT 3
                    CHECK (
                        reminder_days >= 0
                        AND reminder_days <= 30
                    ),

                category TEXT NOT NULL DEFAULT 'Other',

                cancellation_url TEXT NOT NULL DEFAULT '',

                cancellation_instructions TEXT NOT NULL DEFAULT '',

                is_cancelled INTEGER NOT NULL DEFAULT 0
                    CHECK (
                        is_cancelled IN (0, 1)
                    )
            )
            """
        )


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def add_subscription(
    name: str,
    price: float,
    billing_frequency: str,
    next_renewal_date: str,
    reminder_days: int,
    category: str,
    cancellation_url: str,
    cancellation_instructions: str,
) -> int:
    """
    Add a new subscription and return its database ID.
    """

    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("Subscription name cannot be empty.")

    if price < 0:
        raise ValueError("Subscription price cannot be negative.")

    if not 0 <= reminder_days <= 30:
        raise ValueError(
            "Reminder days must be between 0 and 30."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO subscriptions (
                name,
                price,
                billing_frequency,
                next_renewal_date,
                reminder_days,
                category,
                cancellation_url,
                cancellation_instructions,
                is_cancelled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                cleaned_name,
                float(price),
                billing_frequency.strip(),
                next_renewal_date.strip(),
                int(reminder_days),
                category.strip() or "Other",
                cancellation_url.strip(),
                cancellation_instructions.strip(),
            ),
        )

        if cursor.lastrowid is None:
            raise RuntimeError(
                "The database did not return a subscription ID."
            )

        return int(cursor.lastrowid)


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_all_subscriptions() -> list[sqlite3.Row]:
    """
    Return all subscriptions.

    Active subscriptions are displayed before cancelled subscriptions.
    Within each group, subscriptions are ordered by renewal date.
    """

    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT
                id,
                name,
                price,
                billing_frequency,
                next_renewal_date,
                reminder_days,
                category,
                cancellation_url,
                cancellation_instructions,
                is_cancelled
            FROM subscriptions
            ORDER BY
                is_cancelled ASC,
                next_renewal_date ASC,
                name COLLATE NOCASE ASC
            """
        )

        return cursor.fetchall()


def get_subscription(
    subscription_id: int,
) -> sqlite3.Row | None:
    """
    Return one subscription using its database ID.

    Returns None if no matching subscription exists.
    """

    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT
                id,
                name,
                price,
                billing_frequency,
                next_renewal_date,
                reminder_days,
                category,
                cancellation_url,
                cancellation_instructions,
                is_cancelled
            FROM subscriptions
            WHERE id = ?
            """,
            (subscription_id,),
        )

        return cursor.fetchone()


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def update_subscription(
    subscription_id: int,
    name: str,
    price: float,
    billing_frequency: str,
    next_renewal_date: str,
    reminder_days: int,
    category: str,
    cancellation_url: str,
    cancellation_instructions: str,
    is_cancelled: bool,
) -> None:
    """
    Replace the saved information for an existing subscription.
    """

    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("Subscription name cannot be empty.")

    if price < 0:
        raise ValueError("Subscription price cannot be negative.")

    if not 0 <= reminder_days <= 30:
        raise ValueError(
            "Reminder days must be between 0 and 30."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE subscriptions
            SET
                name = ?,
                price = ?,
                billing_frequency = ?,
                next_renewal_date = ?,
                reminder_days = ?,
                category = ?,
                cancellation_url = ?,
                cancellation_instructions = ?,
                is_cancelled = ?
            WHERE id = ?
            """,
            (
                cleaned_name,
                float(price),
                billing_frequency.strip(),
                next_renewal_date.strip(),
                int(reminder_days),
                category.strip() or "Other",
                cancellation_url.strip(),
                cancellation_instructions.strip(),
                int(bool(is_cancelled)),
                subscription_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No subscription exists with ID {subscription_id}."
            )


def set_cancelled_status(
    subscription_id: int,
    is_cancelled: bool,
) -> None:
    """
    Mark a subscription as either cancelled or active.
    """

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE subscriptions
            SET is_cancelled = ?
            WHERE id = ?
            """,
            (
                int(bool(is_cancelled)),
                subscription_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No subscription exists with ID {subscription_id}."
            )


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def delete_subscription(subscription_id: int) -> None:
    """
    Permanently delete a subscription.
    """

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM subscriptions
            WHERE id = ?
            """,
            (subscription_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No subscription exists with ID {subscription_id}."
            )


# ---------------------------------------------------------------------------
# OPTIONAL DEVELOPMENT TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    create_database()

    print("Database created successfully.")
    print(f"Database location: {DATABASE_PATH}")

    subscriptions = get_all_subscriptions()
    print(f"Saved subscriptions: {len(subscriptions)}")