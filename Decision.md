# DECISIONS.md

## Overview

This document records the significant architectural and implementation decisions made during the development of the Expense Splitter application. For each decision, the alternatives considered and the reasoning behind the final choice are documented.

---

# 1. Backend Framework

## Decision

Use **Django REST Framework (DRF)**.

## Alternatives Considered

* Express.js
* FastAPI
* Flask

## Rationale

Although I had prior experience with the MERN stack, I chose Django REST Framework because:

* It provides a mature authentication and permission system.
* Its ORM simplifies relational database interactions.
* Serializers offer built-in validation capabilities.
* The admin interface accelerates debugging.
* The project requirements were highly relational in nature.

---

# 2. Frontend Framework

## Decision

Use **React with Vite**.

## Alternatives Considered

* Plain HTML/CSS/JavaScript
* Next.js

## Rationale

React enabled component-based development and efficient state updates. Vite provided a lightweight development experience with fast builds.

Next.js was considered unnecessary because server-side rendering was not required.

---

# 3. Database Selection

## Decision

Use **PostgreSQL**.

## Alternatives Considered

* SQLite
* MySQL

## Rationale

The application required:

* Complex relational queries,
* Strong consistency,
* Production deployment readiness.

SQLite was unsuitable for production workloads, while PostgreSQL provided excellent support for relational data and Django integration.

---

# 4. Authentication Strategy

## Decision

Use **JWT Authentication** with refresh tokens.

## Alternatives Considered

* Django Session Authentication
* Token Authentication

## Rationale

JWT authentication supports decoupled frontend-backend architectures more naturally.

Advantages:

* Stateless authentication,
* Suitable for SPA applications,
* Easy frontend integration.

Refresh token blacklisting was implemented to support secure logout.

---

# 5. Group Membership Design

## Decision

Model memberships using a dedicated **GroupMember** table.

## Alternatives Considered

* Direct ManyToMany relationship.

## Rationale

The intermediary model allows storing metadata such as:

* Roles,
* Join dates,
* Leave dates.

This design supports future extensibility.

---

# 6. Invitation System

## Decision

Use a separate **Invitation** model.

## Alternatives Considered

* Immediately adding users to groups.

## Rationale

Invitations provide an explicit approval workflow and prevent users from being added without consent.

This approach improves usability and security.

---

# 7. Direct Expenses

## Decision

Represent direct expenses as **special groups of type DIRECT**.

## Alternatives Considered

* Separate DirectExpense models,
* Separate APIs.

## Rationale

Treating direct expenses as groups allows reusing:

* Expense logic,
* Settlement logic,
* Balance calculations.

This reduced duplication significantly.

---

# 8. Balance Computation Strategy

## Decision

Compute balances dynamically.

## Alternatives Considered

* Maintain a dedicated GroupBalance table.

## Rationale

Dynamic computation avoids:

* Synchronization problems,
* Complex update logic.

The application's scale does not justify denormalized balance storage.

---

# 9. Expense Editing Policy

## Decision

Expenses cannot be edited after creation.

## Alternatives Considered

* Allow unrestricted edits,
* Maintain edit history.

## Rationale

Financial records should remain immutable to preserve consistency.

Incorrect entries should instead be corrected through settlements or new expenses.

---

# 10. Split Types Supported

## Decision

Support:

* Equal splits,
* Exact splits,
* Percentage splits.

Share-based splitting was deferred.

## Alternatives Considered

* Implement all split methods immediately.

## Rationale

The selected split methods covered the majority of real-world scenarios.

Share-based splitting introduced additional complexity and was postponed to prioritise delivering a stable MVP.

---

# 11. Payer Participation Rule

## Decision

The expense creator automatically participates in the expense.

## Alternatives Considered

* Require explicit payer inclusion.

## Rationale

This reduces user input requirements and reflects typical expense-sharing behaviour.

For exact and percentage splits, the payer's share is automatically calculated.

---

# 12. Settlement Rules

## Decision

Allow partial settlements.

## Alternatives Considered

* Only allow full settlements.

## Rationale

Partial settlements mirror real-world usage patterns more accurately.

Users often repay debts incrementally.

---

# 13. Settlement Validation

## Decision

Reject overpayments.

## Alternatives Considered

* Permit negative balances.

## Rationale

Preventing overpayment simplifies balance calculations and maintains data integrity.

---

# 14. Currency Support

## Decision

Support INR and USD.

## Alternatives Considered

* Restrict to a single currency,
* Support all currencies.

## Rationale

Supporting two currencies addressed the immediate use cases without introducing exchange-rate complexities.

---

# 15. Search Functionality

## Decision

Provide only global user search.

## Alternatives Considered

* Group-level search,
* Extensive filtering systems.

## Rationale

The immediate requirement was enabling user invitations.

Additional search capabilities were deferred to keep the MVP focused.

---

# 16. Frontend State Management

## Decision

Use React's built-in state management.

## Alternatives Considered

* Redux,
* Zustand,
* Context-heavy architectures.

## Rationale

The project's complexity did not justify introducing external state management libraries.

Local component state remained manageable.

---

# 17. Backend Structure

## Decision

Separate Django apps by domain.

## Applications

* accounts,
* groups,
* expenses.

## Alternatives Considered

* Monolithic application structure.

## Rationale

Domain separation improves maintainability and aligns with Django best practices.

---

# 18. Deployment Strategy

## Decision

Deploy using:

* Railway (backend and PostgreSQL),
* Vercel (frontend).

## Alternatives Considered

* AWS,
* Render,
* Self-hosted VPS.

## Rationale

Railway and Vercel provided:

* Simple deployment workflows,
* Free developer tiers,
* GitHub integration,
* Rapid iteration capability.

---

# 19. Environment Configuration

## Decision

Use environment variables via python-decouple.

## Alternatives Considered

* Hardcoded settings.

## Rationale

Environment variables improve security and simplify deployment across environments.

---

# 20. Migration Strategy

## Decision

Run migrations automatically during deployment.

## Alternatives Considered

* Manual migration execution.

## Rationale

Automating migrations reduces operational overhead and deployment errors.

---

# 21. Repository Structure

## Decision

Use a monorepo structure.

## Structure

```text
repository/
├── backend/
├── frontend/
└── docker-compose.yml
```

## Alternatives Considered

* Separate repositories.

## Rationale

A monorepo simplifies:

* Version management,
* Feature coordination,
* Deployment workflows.

---

# Lessons Learned

Key lessons from this project include:

* Designing schemas carefully reduces future complexity.
* Financial systems benefit from immutable transaction records.
* Dynamic balance computation is often preferable to denormalization for small-to-medium workloads.
* Deployment introduces a distinct class of problems unrelated to feature development.
* CORS configuration and environment management are critical aspects of production readiness.

---

# Future Reconsiderations

The following decisions may be revisited as the application scales:

* Introduce balance caching mechanisms.
* Implement share-based splits.
* Add comprehensive automated tests.
* Adopt dedicated state management.
* Introduce asynchronous task processing.
* Support multi-currency exchange rates.
* Add audit logs for administrative actions.
