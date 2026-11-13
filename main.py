from database.database import initialize_database, seed_demo_employees
from services.employee_service import (
    add_employee,
    assign_manager,
    deactivate_employee,
    search_employee,
    update_employee,
    view_all_employees,
)


def print_employee_table(employees):
    if not employees:
        print("No employees found.")
        return

    print("\nEMPLOYEE DIRECTORY")
    print(f"{'ID':<10} {'Name':<20} {'Department':<18} {'Status':<8}")
    print("-" * 60)
    for employee in employees:
        full_name = f"{employee['first_name']} {employee['last_name']}"
        print(f"{employee['employee_id']:<10} {full_name:<20} {employee['department']:<18} {employee['status']:<8}")


def display_menu():
    print("\n====================================")
    print("           SBN PEOPLEHUB")
    print("       EMPLOYEE DIRECTORY")
    print("====================================")
    print("1. Add Employee")
    print("2. View All Employees")
    print("3. Search Employee")
    print("4. Update Employee")
    print("5. Assign Reporting Manager")
    print("6. Deactivate Employee")
    print("7. Exit")


def main():
    initialize_database()
    seed_demo_employees()

    while True:
        display_menu()
        try:
            choice = input("Select an option: ").strip()
        except EOFError:
            print("\nInput interrupted. Exiting.")
            break

        if choice == "1":
            employee_id = input("Employee ID: ").strip()
            first_name = input("First name: ").strip()
            last_name = input("Last name: ").strip()
            email = input("Email: ").strip()
            department = input("Department: ").strip()
            designation = input("Designation: ").strip()
            manager_id = input("Manager ID (optional): ").strip() or None

            success, message = add_employee(
                employee_id,
                first_name,
                last_name,
                email,
                department,
                designation,
                manager_id,
            )
            print(message)

        elif choice == "2":
            employees = view_all_employees()
            print_employee_table(employees)

        elif choice == "3":
            employee_id = input("Enter Employee ID: ").strip()
            try:
                employee = search_employee(employee_id)
            except ValueError as exc:
                print(exc)
            else:
                if employee is None:
                    print("Employee not found.")
                else:
                    print("Employee Details")
                    print(f"Employee ID: {employee['employee_id']}")
                    print(f"Name: {employee['first_name']} {employee['last_name']}")
                    print(f"Department: {employee['department']}")
                    print(f"Designation: {employee['designation']}")
                    print(f"Manager ID: {employee['manager_id'] if employee['manager_id'] else 'None'}")
                    print(f"Status: {employee['status']}")

        elif choice == "4":
            employee_id = input("Enter Employee ID: ").strip()
            first_name = input("First name (leave blank to keep current): ").strip() or None
            last_name = input("Last name (leave blank to keep current): ").strip() or None
            email = input("Email (leave blank to keep current): ").strip() or None
            department = input("Department (leave blank to keep current): ").strip() or None
            designation = input("Designation (leave blank to keep current): ").strip() or None

            success, message = update_employee(
                employee_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                designation=designation,
            )
            print(message)

        elif choice == "5":
            employee_id = input("Employee ID: ").strip()
            manager_id = input("Manager ID: ").strip()
            success, message = assign_manager(employee_id, manager_id)
            print(message)

        elif choice == "6":
            employee_id = input("Employee ID: ").strip()
            success, message = deactivate_employee(employee_id)
            print(message)

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Error: Invalid menu choice. Please try again.")


if __name__ == "__main__":
    main()
