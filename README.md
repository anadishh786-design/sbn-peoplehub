# SBN PeopleHub

SBN PeopleHub is a simple command-line employee directory built with Python and SQLite. This module focuses on the employee data model, reporting relationships, validation, and inactive employee handling.

## Current implementation and future plans

The current application is a command-line program written in Python. It uses Python's standard library and SQLite for local data storage; it does not currently use a web framework, a web interface, or an authentication platform.

The separate planning document describes possible future capabilities, including a browser-based directory, organisation views, authentication, role-based access, and audit history. These are proposals only. No future web framework, database server, or identity technology has been selected or implemented.

## Features

- Create and persist employee records in SQLite.
- Add employees with validation for IDs, names, emails, departments, and managers.
- Search, view, and update employee records.
- Assign and validate reporting managers.
- Prevent invalid manager relationships including self-reporting and cycles.
- Prevent deactivation when active direct reports still exist.
- Provide automated tests with the Python `unittest` module.

## Project structure

- `database/database.py` — SQLite connection setup, schema creation, and sample seed data.
- `services/employee_service.py` — business logic for employee operations.
- `services/validation.py` — validation rules for IDs, emails, and manager relationships.
- `tests/test_employee_service.py` — automated verification for valid and invalid scenarios.
- `main.py` — command-line menu application.

## Running the application

```bash
python main.py
```

## Running tests

```bash
python -m unittest discover -s tests -v
```

## Database notes

The schema uses SQLite foreign keys and enforces a `CHECK` constraint for valid employee statuses. The `employees` table stores `employee_id` as the primary key and keeps `manager_id` as a reference to another employee record. The database is created automatically when the application starts.

## Sample data

The application seeds six fictional employee records on first run so the directory can be explored immediately. The seed data includes repeated first names, multiple departments, and a reporting hierarchy that demonstrates manager validation and inactive employee safeguards.

Seeding is transactional: a failed insert rolls back the batch, and a later startup can try again. If only some unchanged sample rows exist, seeding adds the missing rows. If any existing sample ID has been edited, the seeder does not overwrite it or add the remaining samples; it leaves the database unchanged so user data is not silently replaced. Review or repair that sample data explicitly before reseeding.
