# Ticketing System Debugging and Refactoring Report

## Part 1: Defect Analysis, Root Causes, and Fixes

### Summary

Eighteen intentional defects were identified and corrected across the ticket models, DuckDB repository, FastAPI routes, and NiceGUI dashboard. The defects prevented startup, broke persistence behavior, returned incorrect API responses, and caused UI workflows to operate on the wrong data.

### Startup and Input Validation

| Defect | Root Cause | Fix |
| --- | --- | --- |
| Application could not import. | `TicketPriority.urgent` had an unterminated string literal. | Closed the enum string as `"urgent"`. |
| Ticket creation accepted empty fields and used impractical field limits. | `TicketCreate` constraints were weaker and inconsistent with `TicketUpdate`. | Applied practical minimum and maximum lengths consistent with update validation. |

### Database and SQL

| Defect | Root Cause | Fix |
| --- | --- | --- |
| Seed initialization failed. | The query selected nonexistent column `total`. | Replaced it with `COUNT(*)`. |
| Seed data could be duplicated. | The existing-record guard used an inverted comparison. | Return early when the ticket count is greater than zero. |
| Ticket creation failed at SQL execution. | Insert statement used `requestor`; the schema uses `requester`. | Corrected the insert column name. |
| Ticket listing failed. | Queries used table `ticket`, but the schema defines `tickets`. | Queried the correct table. |
| Status and priority filters returned incorrect records. | SQL predicates applied each filter value to the other column. | Matched status to `status` and priority to `priority`. |
| Text search did not find partial matches. | `%search%` values were used with equality rather than wildcard matching. | Used parameterized `LIKE` predicates. |
| Returned ticket values had swapped priority and status. | Database result keys did not match the schema column order. | Restored the explicit mapping: `priority` before `status`. |
| Empty updates returned an unrelated record. | Update fallback was hardcoded to ticket ID `1`. | Return the requested ticket ID unchanged. |
| Delete could remove unrelated records. | Predicate used `id != ?`, selecting every ticket except the requested one. | Changed the predicate to `id = ?`. |

### API Behavior

| Defect | Root Cause | Fix |
| --- | --- | --- |
| List requests ignored filters. | The API built `TicketFilters` with `None` status/priority values and reused status as search text. | Forwarded status, priority, and search values directly. |
| A successful create returned not found. | The endpoint fetched `created.id + 1000`. | Returned the newly created ticket. |
| Missing records returned HTTP 500. | `TicketNotFoundError` was converted to an internal-server error. | Return HTTP 404 with the existing not-found message. |
| Delete targeted the wrong record. | The endpoint used `ticket_id + 1`. | Delete the exact request ID. |

### NiceGUI Dashboard

| Defect | Root Cause | Fix |
| --- | --- | --- |
| Dashboard filters were not applied. | The filter model was passed only when no filter was selected. | Always construct and pass the current filter model. |
| Requester and description were swapped on create. | Form values were assigned to the wrong `TicketCreate` fields. | Wired each form value to its matching model field. |
| Selected priority was ignored. | Ticket creation was hardcoded to `urgent`. | Convert and use the selected priority value. |
| Status updates affected the adjacent ticket. | Update callback used `ticket_id + 1`. | Use the exact ticket ID. |
| Buttons were invisible and fields were rotated. | Global CSS hid `.q-btn` and transformed `.q-field`. | Removed the disruptive global rules. |
| Filter controls and results were poorly placed. | Controls and ticket container were created outside the intended layout sequence. | Placed them in the dashboard layout after the ticket-creation form. |

### Part 1 Verification

- Python compilation passed.
- Application import and startup passed.
- In-memory repository checks passed for seed idempotence, CRUD, result mapping, filtering, search, and deletion isolation.
- FastAPI integration checks passed for list, combined filters, search, creation, validation, missing records, and deletion.
- NiceGUI registration passed.
- Live server checks passed for `/health`, `/api/tickets`, and `/`.

## Part 2: Behavior-Preserving Refactoring

### Objective

Improve readability, maintainability, and testability without changing the HTTP API, DuckDB persistence contract, seed data, filter/sort behavior, timestamps, or NiceGUI workflow.

### Refactoring Rules Added

`REFACTORING_RULES.md` records the project rules:

- Preserve API routes, models, HTTP statuses, and error messages.
- Preserve database schema, column order, timestamps, seed records, query behavior, and sort order.
- Preserve NiceGUI layout, notifications, event ordering, and callback behavior.
- Keep SQL values parameterized and schema/result mappings explicit.
- Extract helpers only when they remove repeated knowledge and are directly testable.
- Run focused tests before broader validation; avoid unrelated changes.

### Refactored Code

| Area | Refactoring | Behavior Preserved |
| --- | --- | --- |
| Repository result mapping | Extracted explicit `_TICKET_COLUMNS`. | Existing schema column order and Pydantic model mapping. |
| Repository seed data | Extracted immutable `_SEED_TICKETS`. | Exact three seeded records and creation order. |
| Repository filtering | Extracted `_build_list_query`. | Parameterized query text, parameter order, filtering, and `ORDER BY created_at ASC, id ASC`. |
| Dashboard options | Extracted shared status and priority option lists. | Existing option values and order. |
| Dashboard filters | Extracted `_build_ticket_filters`. | Existing conversion of `"all"`, enum values, and search text to `TicketFilters`. |
| Dashboard styles | Extracted static dashboard CSS. | Existing page background and content-width styling. |

### Why Each Helper Exists

- `_TICKET_COLUMNS` keeps database row mapping explicit and prevents accidental changes to the persistence column contract.
- `_SEED_TICKETS` centralizes the stable sample records while preserving exact data and order.
- `_build_list_query` isolates parameterized SQL construction so query and parameter order can be tested directly.
- `_build_ticket_filters` centralizes conversion of UI control values to filter models without changing callbacks or event ordering.
- Shared UI option/style constants remove duplication while retaining exact rendered values and styles.

### Tests Added

`tests/test_refactoring_contracts.py` adds three focused regression tests:

1. Asserts exact repository filter SQL and parameter order.
2. Asserts idempotent seed behavior and stable seed record ordering.
3. Asserts UI options and filter-model construction preserve existing values.

### Part 2 Verification

- Focused tests: `python -m pytest tests/test_refactoring_contracts.py -q` completed with `3 passed`.
- Full available project tests: `python -m pytest tests -q` completed with `3 passed`.
- Compilation: `python -m compileall -q app tests` completed successfully.
- No project formatter, linter, or type-checker command is configured.

## Environment Note

The project virtual environment was incomplete during validation. The system Python interpreter was used after the missing runtime/testing packages were installed through the configured proxy. This is an environment setup limitation, not an application behavior change.
