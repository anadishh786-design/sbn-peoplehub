from database.database import get_connection, get_current_timestamp
from services import validation


def add_employee(employee_id, first_name, last_name, email, department, designation, manager_id=None, status="Active", db_path=None):
    try:
        cleaned_employee_id = validation.validate_employee_id(employee_id)
        cleaned_first_name = validation.validate_text(first_name, "First name")
        cleaned_last_name = validation.validate_text(last_name, "Last name")
        cleaned_email = validation.validate_email(email)
        cleaned_department = validation.validate_text(department, "Department")
        cleaned_designation = validation.validate_text(designation, "Designation")
        cleaned_manager_id = None
        if manager_id is not None and str(manager_id).strip():
            cleaned_manager_id = validation.validate_employee_id(manager_id)
        cleaned_status = validation.validate_text(status, "Status").title()
        if cleaned_status not in {"Active", "Inactive"}:
            raise ValueError("Status must be either Active or Inactive.")
    except ValueError as exc:
        return False, str(exc)

    connection = get_connection(db_path)
    try:
        existing_employee = connection.execute(
            "SELECT 1 FROM employees WHERE employee_id = ?",
            (cleaned_employee_id,),
        ).fetchone()
        if existing_employee is not None:
            return False, "Error: Employee ID already exists."

        duplicate_email = connection.execute(
            "SELECT 1 FROM employees WHERE LOWER(email) = LOWER(?)",
            (cleaned_email,),
        ).fetchone()
        if duplicate_email is not None:
            return False, "Error: Email already exists."

        if cleaned_manager_id is not None:
            is_valid, message = validation.validate_manager_relationship(connection, cleaned_employee_id, cleaned_manager_id)
            if not is_valid:
                return False, message

        timestamp = get_current_timestamp()
        connection.execute(
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
            (
                cleaned_employee_id,
                cleaned_first_name,
                cleaned_last_name,
                cleaned_email,
                cleaned_department,
                cleaned_designation,
                cleaned_manager_id,
                cleaned_status,
                timestamp,
                timestamp,
            ),
        )
        connection.commit()
        return True, f"Employee added successfully.\nEmployee ID: {cleaned_employee_id}"
    finally:
        connection.close()


def search_employee(employee_id, db_path=None):
    try:
        normalized_employee_id = validation.validate_employee_id(employee_id)
    except ValueError:
        return None

    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            (normalized_employee_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        connection.close()


def view_all_employees(db_path=None):
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            "SELECT employee_id, first_name, last_name, department, designation, status FROM employees ORDER BY employee_id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def update_employee(employee_id, first_name=None, last_name=None, email=None, department=None, designation=None, db_path=None):
    try:
        normalized_employee_id = validation.validate_employee_id(employee_id)
    except ValueError as exc:
        return False, str(exc)

    connection = get_connection(db_path)
    try:
        existing_employee = connection.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            (normalized_employee_id,),
        ).fetchone()
        if existing_employee is None:
            return False, "Error: Employee not found."

        update_values = {}
        try:
            if first_name is not None:
                update_values["first_name"] = validation.validate_text(first_name, "First name")
            if last_name is not None:
                update_values["last_name"] = validation.validate_text(last_name, "Last name")
            if email is not None:
                cleaned_email = validation.validate_email(email)
                if cleaned_email.lower() != existing_employee["email"].lower():
                    duplicate_email = connection.execute(
                        "SELECT 1 FROM employees WHERE LOWER(email) = LOWER(?) AND employee_id != ?",
                        (cleaned_email, normalized_employee_id),
                    ).fetchone()
                    if duplicate_email is not None:
                        return False, "Error: Email already exists."
                update_values["email"] = cleaned_email
            if department is not None:
                update_values["department"] = validation.validate_text(department, "Department")
            if designation is not None:
                update_values["designation"] = validation.validate_text(designation, "Designation")
        except ValueError as exc:
            return False, str(exc)

        if not update_values:
            return False, "Error: No changes supplied."

        update_values["updated_at"] = get_current_timestamp()
        assignments = ", ".join(f"{field} = ?" for field in update_values)
        values = list(update_values.values())

        connection.execute(
            f"UPDATE employees SET {assignments} WHERE employee_id = ?",
            (*values, normalized_employee_id),
        )
        connection.commit()
        return True, "Employee updated successfully."
    finally:
        connection.close()


def assign_manager(employee_id, manager_id, db_path=None):
    try:
        normalized_employee_id = validation.validate_employee_id(employee_id)
        normalized_manager_id = validation.validate_employee_id(manager_id)
    except ValueError as exc:
        return False, str(exc)

    connection = get_connection(db_path)
    try:
        employee_row = connection.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            (normalized_employee_id,),
        ).fetchone()
        if employee_row is None:
            return False, "Error: Employee not found."

        is_valid, message = validation.validate_manager_relationship(connection, normalized_employee_id, normalized_manager_id)
        if not is_valid:
            return False, message

        connection.execute(
            "UPDATE employees SET manager_id = ?, updated_at = ? WHERE employee_id = ?",
            (normalized_manager_id, get_current_timestamp(), normalized_employee_id),
        )
        connection.commit()
        return True, "Manager assigned successfully."
    finally:
        connection.close()


def deactivate_employee(employee_id, db_path=None):
    try:
        normalized_employee_id = validation.validate_employee_id(employee_id)
    except ValueError as exc:
        return False, str(exc)

    connection = get_connection(db_path)
    try:
        employee_row = connection.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            (normalized_employee_id,),
        ).fetchone()
        if employee_row is None:
            return False, "Error: Employee not found."

        if employee_row["status"] == "Inactive":
            return False, "Error: Employee is already inactive."

        active_reports = connection.execute(
            "SELECT COUNT(*) AS report_count FROM employees WHERE manager_id = ? AND status = 'Active'",
            (normalized_employee_id,),
        ).fetchone()["report_count"]

        if active_reports > 0:
            return (
                False,
                f"Cannot deactivate {normalized_employee_id}. This employee has {active_reports} active direct reports. Please reassign the reporting relationships first.",
            )

        connection.execute(
            "UPDATE employees SET status = 'Inactive', updated_at = ? WHERE employee_id = ?",
            (get_current_timestamp(), normalized_employee_id),
        )
        connection.commit()
        return True, f"Employee {normalized_employee_id} deactivated successfully."
    finally:
        connection.close()
