# SBN PeopleHub: Employee Directory Plan

**Status:** Planning only. Leave management is out of scope for this step.

## 1. Employee record

Use one employee row per person. In SQLite, the proposed fields are:

| Field | Proposed storage | Notes |
|---|---|---|
| Employee ID | `employee_id TEXT PRIMARY KEY` | Stable organisation-assigned identifier, for example `SBN-1001`. |
| Full name | `full_name TEXT NOT NULL` | Display name; not a unique key. |
| Designation | `designation TEXT NOT NULL` | Job title or level, such as Senior Analyst. |
| Department | `department TEXT NOT NULL` | Organisational unit, such as Operations. |
| Process / work assignment | `process TEXT` | Team, service, or work area within a department. |
| Reporting manager | `manager_employee_id TEXT NULL` | Foreign key to `employees.employee_id`; NULL for the top-level role or an approved exception. |
| Work email | `work_email TEXT NOT NULL` | Work contact; uniqueness policy needs SBN confirmation. |
| Joining date | `joining_date TEXT NOT NULL` | ISO date `YYYY-MM-DD`. |
| Active status | `is_active INTEGER NOT NULL` | Boolean stored as 1 (active) or 0 (inactive). |

Department, designation, and process describe different things. For example, **Neha** can be an **Operations Manager** (designation) in **Operations** (department), assigned to the **Customer Operations** process (work assignment).

Employee ID identifies the person and should remain stable if their name, job, department, or assignment changes. A manager reference uses that ID, so reporting links do not depend on names or titles.

## 2. Fictional employee examples

All people and details below are invented. Addresses use `example.com`.

| Employee ID | Full name | Designation | Department | Process / assignment | Reporting manager | Work email | Joining date | Status |
|---|---|---|---|---|---|---|---|---|
| SBN-1001 | Amit Yadav | Department Head | Technology | Technology Leadership | — (no manager recorded) | amit.yadav@example.com | 2020-04-06 | Active |
| SBN-1002 | Darshit Pandey | Team Manager | Technology | Platform Support | SBN-1001 — Amit Yadav | darshit.pandey@example.com | 2021-08-16 | Active |
| SBN-1003 | Asha | Support Analyst | Technology | Platform Support | SBN-1002 — Darshit Pandey | asha@example.com | 2023-02-13 | Active |
| SBN-1004 | Asha | Systems Analyst | Technology | Access Operations | SBN-1002 — Darshit Pandey | asha2@example.com | 2024-06-03 | Active |
| SBN-2001 | Neha | Operations Manager | Operations | Customer Operations | SBN-1001 — Amit Yadav | neha@example.com | 2020-11-09 | Active |
| SBN-2002 | Prakash Singh | Operations Associate | Operations | Customer Onboarding | SBN-2001 — Neha | prakash.singh@example.com | 2022-05-23 | Inactive |

SBN-1002 has two direct reports (SBN-1003 and SBN-1004). SBN-1001 has no reporting manager recorded. Asha appears twice with different employee IDs and different work emails. SBN-2002 is inactive.

## 3. Screen sketches

### Employee directory

```text
+---------------------------------------------------------------------+
| SBN PeopleHub                         Employee Directory   [Profile] |
+---------------------------------------------------------------------+
| Search by ID or name [________________________] Department [All v]  |
|                                                                     |
| ID        Name          Designation       Department   Status        |
| SBN-1001  Amit Yadav     Department Head   Technology   Active        |
| SBN-1002  Darshit Pandey     Team Manager      Technology   Active        |
| SBN-1003  Asha   Support Analyst   Technology   Active        |
| ...                                                                 |
| [Select a row to open the employee profile]                         |
+---------------------------------------------------------------------+
```

### Employee profile

```text
+----------------------------------------------------------+
| SBN PeopleHub                         Directory | Org    |
+----------------------------------------------------------+
| Asha                              [Active]        |
| Employee ID: SBN-1003                                    |
| Designation: Support Analyst                             |
| Department: Technology                                   |
| Process: Platform Support                               |
| Work email: asha@example.com                      |
| Joining date: 2023-02-13                                 |
|                                                          |
| Reporting manager                                        |
| Darshit Pandey — SBN-1002 — Team Manager                      |
| [Open manager profile]                                   |
+----------------------------------------------------------+
```

### Organisation view

```text
+----------------------------------------------------------+
| SBN PeopleHub                    Directory | Organisation|
+----------------------------------------------------------+
| Amit Yadav (SBN-1001) — Department Head                   |
|   +-- Darshit Pandey (SBN-1002) — Team Manager                |
|   |     +-- Asha (SBN-1003) — Support Analyst     |
|   |     +-- Asha (SBN-1004) — Systems Analyst     |
|   +-- Neha (SBN-2001) — Operations Manager          |
|         +-- Prakash Singh (SBN-2002) — Operations Associate  |
+----------------------------------------------------------+
```

## 4. Decisions and open business questions

1. **What remains unchanged after a designation or department change?** The employee ID remains the stable identity. The employee's joining date also remains their original joining date. Name, work email, designation, department, process, manager, and active status are separate fields and are updated only when those facts change. SBN should decide whether to retain a dated history of previous titles, departments, and assignments; the initial directory proposal stores current values only.
2. **How to prevent duplicate employee IDs?** Make `employee_id` the SQLite primary key and reject duplicate IDs on insert/update with a clear validation message. Never generate IDs from names, because names can repeat or change. SBN must decide the official ID format and who assigns IDs.
3. **What if a manager becomes inactive?** Do not silently delete or reassign their reports. Flag or block the change until each active direct report has a valid active manager, or an authorised exception is recorded. SBN must decide who can approve exceptions and whether inactive employees remain visible in historical organisation views.
4. **How to prevent self-reporting and cycles?** Reject a manager ID equal to the employee's own ID. Before saving a manager change, walk upward from the proposed manager; reject the change if that path reaches the employee being edited. Also require any non-null manager ID to reference an existing employee. SQLite foreign keys should be enabled. SBN should decide whether top-level employees may have no manager and whether multiple organisational roots are allowed.

## 5. Review notes

This is a proposal for review, not a final SBN policy. The sample records are fictional and intended only to demonstrate duplicate names, manager links, a managerless top-level role, two direct reports, and an inactive employee.

**Assistance used:** Prepared with AI assistance (OpenAI Codex) from the task brief. No real employee information was used.
