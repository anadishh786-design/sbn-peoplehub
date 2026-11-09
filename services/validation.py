import re


def validate_employee_id(employee_id):
    if employee_id is None or not str(employee_id).strip():
        raise ValueError("Employee ID is required.")

    normalized_id = str(employee_id).strip().upper()
    if not re.fullmatch(r"SBN\d+", normalized_id):
        raise ValueError("Employee ID must use the format SBN###.")

    return normalized_id


def validate_text(value, field_name):
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")
    return str(value).strip()


def validate_email(email):
    normalized_email = validate_text(email, "Email")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized_email):
        raise ValueError("Email is not valid.")
    return normalized_email.lower()


def validate_manager_relationship(connection, employee_id, manager_id):
    current_employee_id = validate_employee_id(employee_id)
    cleaned_manager_id = (str(manager_id) or "").strip().upper()

    if not cleaned_manager_id:
        return True, "Manager ID is optional."

    if cleaned_manager_id == current_employee_id:
        return False, "Rejected: An employee cannot report to themselves."

    manager_row = connection.execute(
        "SELECT employee_id, status FROM employees WHERE employee_id = ?",
        (cleaned_manager_id,),
    ).fetchone()
    if manager_row is None:
        return False, "Rejected: Manager does not exist."
    if manager_row["status"] != "Active":
        return False, "Rejected: Selected manager is inactive."

    visited_ids = set()
    current_manager_id = cleaned_manager_id

    while current_manager_id is not None:
        if current_manager_id in visited_ids:
            return False, "Rejected: Circular reporting detected."
        visited_ids.add(current_manager_id)

        manager_parent = connection.execute(
            "SELECT manager_id FROM employees WHERE employee_id = ?",
            (current_manager_id,),
        ).fetchone()
        if manager_parent is None:
            return True, "Valid manager relationship."

        parent_id = manager_parent["manager_id"]
        if parent_id == current_employee_id:
            return False, "Rejected: Circular reporting detected."
        current_manager_id = parent_id

    return True, "Valid manager relationship."
