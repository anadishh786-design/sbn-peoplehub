import os
import sqlite3
import tempfile
import unittest

from database.database import get_connection, initialize_database, seed_demo_employees
from services.employee_service import (
    add_employee,
    assign_manager,
    deactivate_employee,
    search_employee,
    update_employee,
)


class EmployeeServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "peoplehub_test.db")
        initialize_database(self.db_path)
        seed_demo_employees(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def database_snapshot(self):
        connection = get_connection(self.db_path)
        try:
            rows = connection.execute("SELECT * FROM employees ORDER BY employee_id").fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def test_add_valid_employee(self):
        success, message = add_employee(
            "SBN007",
            "Ishita",
            "Khan",
            "ishita.khan@example.com",
            "Operations",
            "Operations Analyst",
            "SBN001",
            db_path=self.db_path,
        )
        self.assertTrue(success)
        self.assertIn("Employee added successfully", message)
        self.assertEqual(search_employee("SBN007", self.db_path)["first_name"], "Ishita")

    def test_add_duplicate_employee_id_rejected(self):
        success, message = add_employee(
            "SBN001",
            "New",
            "Employee",
            "new.employee@example.com",
            "Operations",
            "Analyst",
            "SBN002",
            db_path=self.db_path,
        )
        self.assertFalse(success)
        self.assertIn("Employee ID already exists", message)

    def test_add_duplicate_email_rejected(self):
        success, message = add_employee(
            "SBN099",
            "Rita",
            "Patel",
            "asha.sharma@example.com",
            "Operations",
            "Analyst",
            "SBN001",
            db_path=self.db_path,
        )
        self.assertFalse(success)
        self.assertIn("Email already exists", message)

    def test_search_existing_employee(self):
        employee = search_employee("SBN003", self.db_path)
        self.assertIsNotNone(employee)
        self.assertEqual(employee["first_name"], "Asha")
        self.assertEqual(employee["last_name"], "Verma")

    def test_search_missing_employee_returns_none(self):
        employee = search_employee("SBN999", self.db_path)
        self.assertIsNone(employee)

    def test_update_employee(self):
        success, message = update_employee(
            "SBN002",
            department="Finance Operations",
            designation="Senior Analyst",
            db_path=self.db_path,
        )
        self.assertTrue(success)
        self.assertIn("updated successfully", message)

        updated_employee = search_employee("SBN002", self.db_path)
        self.assertEqual(updated_employee["department"], "Finance Operations")
        self.assertEqual(updated_employee["designation"], "Senior Analyst")

    def test_update_invalid_email_is_rejected_without_changes(self):
        before = self.database_snapshot()

        success, message = update_employee("SBN002", email="not-an-email", db_path=self.db_path)

        self.assertFalse(success)
        self.assertIn("Email is not valid", message)
        self.assertEqual(self.database_snapshot(), before)

    def test_update_empty_name_is_rejected_without_changes(self):
        before = self.database_snapshot()

        success, message = update_employee("SBN002", first_name=" ", db_path=self.db_path)

        self.assertFalse(success)
        self.assertIn("First name is required", message)
        self.assertEqual(self.database_snapshot(), before)

    def test_update_empty_department_is_rejected_without_changes(self):
        before = self.database_snapshot()

        success, message = update_employee("SBN002", department="", db_path=self.db_path)

        self.assertFalse(success)
        self.assertIn("Department is required", message)
        self.assertEqual(self.database_snapshot(), before)

    def test_update_duplicate_email_is_rejected_without_changes(self):
        before = self.database_snapshot()

        success, message = update_employee(
            "SBN002",
            email="ASHA.VERMA@example.com",
            db_path=self.db_path,
        )

        self.assertFalse(success)
        self.assertIn("Email already exists", message)
        self.assertEqual(self.database_snapshot(), before)

    def test_employee_operations_reject_invalid_id_format(self):
        self.assertIsNone(search_employee("employee-1", self.db_path))

        success, message = update_employee("employee-1", first_name="New", db_path=self.db_path)

        self.assertFalse(success)
        self.assertIn("Employee ID must use the format", message)

    def test_assign_valid_manager(self):
        success, message = assign_manager("SBN004", "SBN003", db_path=self.db_path)
        self.assertTrue(success)
        self.assertIn("Manager assigned successfully", message)
        self.assertEqual(search_employee("SBN004", self.db_path)["manager_id"], "SBN003")

    def test_assign_nonexistent_manager_rejected(self):
        success, message = assign_manager("SBN005", "SBN999", db_path=self.db_path)
        self.assertFalse(success)
        self.assertIn("Manager does not exist", message)

    def test_assign_inactive_manager_rejected(self):
        success, message = deactivate_employee("SBN004", db_path=self.db_path)
        self.assertTrue(success)

        success, message = assign_manager("SBN005", "SBN004", db_path=self.db_path)
        self.assertFalse(success)
        self.assertIn("inactive", message.lower())

    def test_add_employee_with_inactive_manager_is_rejected_without_changes(self):
        success, _ = deactivate_employee("SBN004", db_path=self.db_path)
        self.assertTrue(success)
        before = self.database_snapshot()

        success, message = add_employee(
            "SBN007",
            "Ishita",
            "Khan",
            "ishita.khan@example.com",
            "Operations",
            "Analyst",
            "SBN004",
            db_path=self.db_path,
        )

        self.assertFalse(success)
        self.assertIn("inactive", message.lower())
        self.assertEqual(self.database_snapshot(), before)

    def test_add_employee_with_invalid_reporting_relationship_is_rejected(self):
        before = self.database_snapshot()

        success, message = add_employee(
            "SBN007",
            "Ishita",
            "Khan",
            "ishita.khan@example.com",
            "Operations",
            "Analyst",
            "SBN007",
            db_path=self.db_path,
        )

        self.assertFalse(success)
        self.assertIn("cannot report to themselves", message.lower())
        self.assertEqual(self.database_snapshot(), before)

    def test_employee_reports_to_self_rejected(self):
        success, message = assign_manager("SBN003", "SBN003", db_path=self.db_path)
        self.assertFalse(success)
        self.assertIn("cannot report to themselves", message.lower())

    def test_circular_reporting_rejected(self):
        success, message = assign_manager("SBN001", "SBN003", db_path=self.db_path)
        self.assertFalse(success)
        self.assertIn("circular", message.lower())

    def test_deactivate_employee_with_active_reports_rejected(self):
        success, message = deactivate_employee("SBN001", db_path=self.db_path)
        self.assertFalse(success)
        self.assertIn("active direct reports", message)

    def test_deactivate_employee_without_active_reports_passes(self):
        success, message = deactivate_employee("SBN004", db_path=self.db_path)
        self.assertTrue(success)
        self.assertEqual(search_employee("SBN004", self.db_path)["status"], "Inactive")

    def test_repeated_startup_does_not_duplicate_sample_employees(self):
        initialize_database(self.db_path)

        inserted_count = seed_demo_employees(self.db_path)

        self.assertEqual(inserted_count, 0)
        self.assertEqual(len(self.database_snapshot()), 6)

    def test_seed_recovers_missing_sample_rows(self):
        connection = get_connection(self.db_path)
        try:
            for employee_id in ("SBN006", "SBN005", "SBN004", "SBN003", "SBN002"):
                connection.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
            connection.commit()
        finally:
            connection.close()

        inserted_count = seed_demo_employees(self.db_path)

        self.assertEqual(inserted_count, 5)
        self.assertEqual(len(self.database_snapshot()), 6)

    def test_failed_seed_rolls_back_all_inserted_rows(self):
        partial_seed_path = os.path.join(self.temp_dir.name, "partial_seed.db")
        initialize_database(partial_seed_path)
        connection = get_connection(partial_seed_path)
        try:
            connection.execute(
                """
                CREATE TRIGGER fail_sample_insert
                BEFORE INSERT ON employees
                WHEN NEW.employee_id = 'SBN003'
                BEGIN
                    SELECT RAISE(ABORT, 'simulated seed failure');
                END
                """
            )
            connection.commit()
        finally:
            connection.close()

        with self.assertRaises(sqlite3.IntegrityError):
            seed_demo_employees(partial_seed_path)

        connection = get_connection(partial_seed_path)
        try:
            employee_count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
            connection.execute("DROP TRIGGER fail_sample_insert")
            connection.commit()
        finally:
            connection.close()
        self.assertEqual(employee_count, 0)
        self.assertEqual(seed_demo_employees(partial_seed_path), 6)


if __name__ == "__main__":
    unittest.main()
