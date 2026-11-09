import os
import tempfile
import unittest

from database.database import initialize_database, seed_demo_employees
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


if __name__ == "__main__":
    unittest.main()
