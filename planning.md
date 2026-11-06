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

## 5. Reporting changes and inactive managers

### If a manager becomes inactive

An employee should never lose their reporting relationship merely because the reporting manager is deactivated. Making a manager inactive must run a controlled reporting-change workflow:

1. Identify all active employees reporting directly to that manager.
2. Temporarily mark the inactive-manager change as pending and warn the authorised HR or Operations user.
3. Require a new active manager for each affected employee, following normal approval rules.
4. Apply all reassignment changes together so the directory does not retain broken reporting links.
5. If SBN permits a short exception, record the exception, approver, reason, and expiry date. A permanent managerless record should not be an accidental default.

Inactive managers and reports remain available in historical organisation views. They must not appear as available managers for a new assignment.

### Preventing invalid reporting relationships

The reporting change service must enforce all of the following before saving:

* The proposed manager is an existing employee.
* The proposed manager is active.
* The proposed manager is not the employee being changed.
* Walking the proposed manager's ancestors does not reach the employee being changed.

The indirect-cycle check also handles changes several levels away. For example, if A proposes to report to B, and C reports to A, the application must follow B -> C -> A only if such a relationship already exists. A change that produces a path back to A must be rejected even when it is not a direct cycle.

At database level, enforce employee existence with a foreign key. Application validation must additionally enforce manager activity and acyclic relationships. If the database may receive direct writes, a transaction or database trigger should prevent partial reporting updates.

## 6. Employee changes and historical information

When department, designation, process, manager, or active status changes, update the employee's current record in place and create an effective-dated change entry. This preserves the stable employee identity while providing an audit trail.

A proposed history record should contain:

| Field | Purpose |
|---|---|
| Employee ID | Stable identity of the employee. |
| Change type | Department, designation, process, manager, status, or personal detail change. |
| Previous value | Value before the change. |
| New value | Value after the change. |
| Effective date | Date the change became operational. |
| Recorded date | Date the change was entered into the directory. |
| Changed by | User or administrator who recorded the change. |
| Reason / reference | Optional approved reason, ticket, transfer, or promotion reference. |

The employee ID, original joining date, and original employment identity remain unchanged by normal organisational changes. The current department, designation, process, manager, work email, active status, and other mutable current-directory fields change in place. Historical entries retain the values that were correct on their effective dates.

Sensitive identity or work-history details should only be displayed or exported according to SBN's role policy. Correcting an incorrect history entry must be auditable rather than silently overwriting past facts.

## 7. Basic security and access controls

The directory should start with authenticated access and least-privilege roles:

| Role | Proposed permissions |
|---|---|
| Employee | View permitted directory profiles, search the organisation, and manage only their own permitted profile fields. |
| Manager | View their reporting organisation and the profiles their role is authorised to see. |
| HR / directory administrator | Create, update, deactivate, and reassign employees; review rejected cycles and approve recorded exceptions. |
| Organisation administrator | Maintain configuration such as departments, processes, ID policies, and role assignments. |

Additional controls are:

* Use individual authenticated accounts; do not share passwords or use a shared administrator account.
* Authorise actions server-side on every request, not only by hiding buttons in the interface.
* Log employee creation, profile changes, manager reassignment, deactivation, history corrections, exports, and permission changes.
* Protect work email and other personal information in transit and restrict exports by role.
* Apply session timeouts, strong password or organisation identity-provider policies, and protection against common web vulnerabilities.
* Prevent inactive employee accounts from signing in to edit data, unless SBN separately requires another authorised system account.
* Require confirmation and an audit trail for bulk changes and employee deactivation.
* Keep production data separate from training and test data, and use fictional records in non-production environments.

The first release should not expose unrestricted personal contact details or employee history to every account. SBN should confirm the privacy, retention, and approval policies before the directory stores data beyond the minimum operational fields.

## 8. Explanations of key decisions

1. **Why Employee ID instead of employee name is the unique identifier:** Employee ID is the stable organisational identity for a person. Names can be repeated, misspelled, or changed, so name matching can merge two employees or create an incorrect reporting link. The ID should remain unchanged even when a name, role, department, or manager changes.

2. **What should happen if an employee's manager becomes inactive:** The manager should not be removed silently and leave reports disconnected. The system should identify the affected active reports, require reassignment to another active manager, and apply the reassignment transactionally. If SBN allows a documented exception, it must include an approver and expiry rather than becoming an untracked permanent state.

3. **How an indirect circular reporting relationship is detected:** Before saving a proposed manager change, the application follows the proposed manager's chain upward through each manager link. If that chain reaches the employee being edited, saving the relationship would create a cycle and must be rejected. This check works for direct and indirect cycles.

4. **Which information remains unchanged when an employee changes department:** The employee ID remains unchanged, as does the original joining date and the link to their immutable person record. The current department changes to the new department, while a dated history entry keeps both the old and new department values. Name and employment identity should only change through their own authorised changes, not because the department changed.

5. **Why leave management is excluded from the first stage:** It introduces policy, approval, entitlement, balance, holiday-calendar, and payroll-style rules that are separate from building a trustworthy employee directory. Defining the employee identity and reporting model first gives the later leave system stable data to reference. Leaving it out also keeps this stage testable and reduces privacy and compliance risk.

## 9. Review notes

This is a proposal for review, not a final SBN policy. The sample records are fictional and intended only to demonstrate duplicate names, manager links, a managerless top-level role, two direct reports, and an inactive employee.

**Assistance used:** Prepared with AI assistance (OpenAI Codex) from the task brief. No real employee information was used.
