# SCOPE.md

## Project Overview

This project is a Splitwise-inspired expense sharing application developed using Django and PostgreSQL. The system allows users to create groups, record shared expenses, split expenses among group members, and track settlements between users.

The primary objective of the project was to implement a robust expense management system with appropriate validation, authorization, and relational database design.

---

# Implemented Features

## User Management

* User registration and authentication.
* Secure password storage using Django's authentication framework.
* Unique usernames and email addresses.

---

## Group Management

* Users can create groups.
* Groups maintain information about their creator and administrator.
* Users can be added as group members.
* Membership information is maintained separately from group metadata.

---

## Expense Management

* Group members can create expenses within their groups.
* Each expense records:

  * Payer information,
  * Expense amount,
  * Currency,
  * Description,
  * Expense date,
  * Split strategy used.

---

## Expense Splitting

The application supports multiple expense splitting strategies:

* Equal Split,
* Exact Split,
* Percentage Split.

During expense creation, appropriate validations ensure that the resulting split allocations remain logically consistent with the original expense amount.

---

## Settlement Tracking

The system allows users to record settlements separately from expenses.

Settlement records capture:

* Who paid,
* Who received the payment,
* Amount settled,
* Currency,
* Settlement date,
* Optional notes.

---

## Authorization and Permissions

The following authorization rules were implemented:

* Only authenticated users can access protected resources.
* Only group members can create expenses within a group.
* Users cannot create expenses involving non-members.
* Group-specific operations are restricted to authorized participants.

---

# Database Schema

The application uses the following relational database structure.

---

## Users

| Column     | Description                |
| ---------- | -------------------------- |
| id         | Primary key                |
| username   | Unique username            |
| email      | User email                 |
| password   | Hashed password            |
| created_at | Account creation timestamp |

---

## Groups

| Column      | Description                |
| ----------- | -------------------------- |
| id          | Primary key                |
| group_name  | Name of the group          |
| group_type  | Type/category of group     |
| created_by  | User who created the group |
| admin       | Group administrator        |
| description | Optional group description |
| created_at  | Group creation timestamp   |

---

## GroupMembers

| Column    | Description                    |
| --------- | ------------------------------ |
| group_id  | Associated group               |
| user_id   | Associated user                |
| joined_at | Membership start date          |
| left_at   | Membership end date (nullable) |

---

## Expenses

| Column       | Description               |
| ------------ | ------------------------- |
| expense_id   | Primary key               |
| group_id     | Associated group          |
| paid_by      | User who paid             |
| amount       | Total expense amount      |
| currency     | Expense currency          |
| description  | Expense description       |
| split_type   | Expense split strategy    |
| expense_date | Date of expense           |
| created_at   | Record creation timestamp |

---

## ExpenseSplits

| Column      | Description                    |
| ----------- | ------------------------------ |
| split_id    | Primary key                    |
| expense_id  | Associated expense             |
| user_id     | User responsible for the share |
| amount_owed | Amount owed by the user        |

---

## Settlements

| Column          | Description                   |
| --------------- | ----------------------------- |
| settlement_id   | Primary key                   |
| group_id        | Associated group              |
| paid_by         | User making the settlement    |
| received_by     | User receiving the settlement |
| amount          | Settlement amount             |
| currency        | Settlement currency           |
| settlement_date | Date of settlement            |
| notes           | Optional remarks              |

---

# CSV Import Feature

## Current Status

The CSV import functionality was analyzed and designed during the development process but was not implemented in the submitted version due to project time constraints.

Although not implemented, the anomaly handling policies and architectural decisions were documented as part of the design exercise.

---

# Proposed CSV Import Assumptions

The following assumptions were identified for a future implementation:

* CSV import operates only within an existing group.
* Usernames appearing in the CSV are expected to correspond to application usernames after normalization.
* Import processing is performed on a per-row basis.
* Partial imports are allowed.
* Rows containing unrecoverable anomalies are excluded from import.

---

# Proposed Anomaly Handling Policies

| Anomaly                                            | Proposed Handling Policy                             |
| -------------------------------------------------- | ---------------------------------------------------- |
| Unknown user                                       | Reject affected row                                  |
| User not belonging to target group                 | Reject affected row                                  |
| Invalid amount (negative or zero)                  | Reject affected row                                  |
| Invalid or unparseable date                        | Reject affected row                                  |
| Split allocations not matching expense total       | Reject affected row                                  |
| Unsupported split representation                   | Convert to exact split representation where possible |
| Missing required fields                            | Reject affected row                                  |
| Data normalization differences (whitespace/casing) | Normalize prior to validation                        |

---

# Future Enhancements

Potential future enhancements identified during the design process include:

* Background processing for large imports,
* Interactive anomaly review workflows,
* Import history and audit logs,
* Downloadable PDF import reports,
* Duplicate expense detection,
* Enhanced import analytics.

---

# Design Philosophy

The project prioritized correctness of financial records, consistency of relational data, and enforcement of group-level permissions.

For features involving external data ingestion, the preferred approach is to reject ambiguous or invalid data rather than silently introducing potentially incorrect financial transactions into the system.
