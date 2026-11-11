import os
import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database",
    "peoplehub.db",
)


def get_database_path():
    configured_path = os.getenv("SBN_PEOPLEHUB_DB_PATH")
    if configured_path:
        return configured_path
    return DEFAULT_DB_PATH


def get_connection(db_path=None):
    target_path = db_path or get_database_path()
    directory = os.path.dirname(target_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    connection = sqlite3.connect(target_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def initialize_database(db_path=None):
    target_path = db_path or get_database_path()
    connection = get_connection(target_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                department TEXT NOT NULL,
                designation TEXT NOT NULL,
                manager_id TEXT,
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (manager_id)
                    REFERENCES employees(employee_id),
                CHECK (status IN ('Active', 'Inactive')),
                CHECK (
                    manager_id IS NULL
                    OR manager_id != employee_id
                )
            )
            """
        )
        connection.commit()
    finally:
        connection.close()
    return target_path


def seed_demo_employees(db_path=None):
    target_path = db_path or get_database_path()
    connection = get_connection(target_path)
    try:
        timestamp = get_current_timestamp()
        sample_employees = [
            ("SBN001", "Arjun", "Mehta", "arjun.mehta@example.com", "Management", "Department Head", None, "Active", timestamp, timestamp),
            ("SBN002", "Asha", "Sharma", "asha.sharma@example.com", "Finance", "Finance Analyst", "SBN001", "Active", timestamp, timestamp),
            ("SBN003", "Asha", "Verma", "asha.verma@example.com", "Technology", "Senior Analyst", "SBN001", "Active", timestamp, timestamp),
            ("SBN004", "Rahul", "Singh", "rahul.singh@example.com", "Finance", "Finance Lead", "SBN002", "Active", timestamp, timestamp),
            ("SBN005", "Neha", "Patel", "neha.patel@example.com", "Technology", "Support Engineer", "SBN003", "Active", timestamp, timestamp),
            ("SBN006", "Aman", "Khan", "aman.khan@example.com", "Operations", "Operations Analyst", "SBN001", "Active", timestamp, timestamp),
        ]

        connection.execute("BEGIN IMMEDIATE")
        existing_count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        expected_by_id = {employee[0]: employee for employee in sample_employees}
        existing_samples = connection.execute(
            "SELECT * FROM employees WHERE employee_id IN (?, ?, ?, ?, ?, ?)",
            tuple(expected_by_id),
        ).fetchall()

        if existing_count > 0 and not existing_samples:
            connection.rollback()
            return 0

        for existing in existing_samples:
            expected = expected_by_id[existing["employee_id"]]
            if tuple(existing[key] for key in (
                "employee_id", "first_name", "last_name", "email", "department",
                "designation", "manager_id", "status",
            )) != expected[:8]:
                connection.rollback()
                return 0

        existing_ids = {row["employee_id"] for row in existing_samples}
        missing_employees = [employee for employee in sample_employees if employee[0] not in existing_ids]
        connection.executemany(
            """
            INSERT INTO employees (
                employee_id,
                first_name,
                last_name,
                email,
                department,
                designation,
                manager_id,
                status,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            missing_employees,
        )
        connection.commit()
        return len(missing_employees)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
