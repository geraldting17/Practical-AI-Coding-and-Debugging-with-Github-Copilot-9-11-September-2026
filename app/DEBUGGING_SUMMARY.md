# Debugging Summary

## Startup and Validation

- `TicketPriority.urgent` had an unterminated string literal.
  - Root cause: A missing closing quote prevented Python from importing the package.
- `TicketCreate` accepted empty titles and descriptions and imposed unrealistic limits on descriptions and requester names.
  - Root cause: Its field constraints were inconsistent with the established `TicketUpdate` contract.

## Database and SQL

- Seed initialization queried `SELECT total`, but the table has no `total` column.
  - Root cause: The aggregate query was invalid; it needed `COUNT(*)`.
- The seed guard checked `count < 0`.
  - Root cause: An inverted condition did not prevent reseeding when data already existed.
- The insert statement used `requestor`, while the schema defines `requester`.
  - Root cause: Column-name mismatch caused ticket creation to fail.
- List queries targeted `ticket`, while the schema creates `tickets`.
  - Root cause: Incorrect table identifier.
- Status and priority filters were applied to each other's columns.
  - Root cause: SQL predicate construction swapped status and priority.
- Search generated `%term%` but used `=`.
  - Root cause: Wildcard search patterns require `LIKE`.
- Result mapping labeled database columns as `status, priority` although the schema returns `priority, status`.
  - Root cause: Keys were out of order, producing invalid or swapped Pydantic models.
- Empty updates returned ticket `1`.
  - Root cause: A hardcoded fallback ID was used instead of the requested ticket ID.
- Delete used `WHERE id != ?`.
  - Root cause: An inverted predicate could delete every other ticket instead of the requested record.

## API Behavior

- The list endpoint discarded status and priority filters and could treat a status value as search text.
  - Root cause: `TicketFilters` was built with incorrect arguments.
- The create endpoint fetched `created.id + 1000` after creating a ticket.
  - Root cause: A fabricated offset caused successful creates to become not-found failures.
- Missing-ticket reads returned HTTP 500 with a misleading database error.
  - Root cause: `TicketNotFoundError` was translated to the wrong HTTP status.
- The delete endpoint used `ticket_id + 1`.
  - Root cause: An off-by-one ID error could delete the adjacent ticket.

## UI Behavior and Display

- Filters were sent to the repository only when no filter was selected.
  - Root cause: Reversed conditional logic.
- The new-ticket form swapped requester and description.
  - Root cause: Field values were assigned to the wrong `TicketCreate` parameters.
- The UI always created urgent tickets.
  - Root cause: A hardcoded enum value ignored the selected priority.
- Status updates used `ticket_id + 1`.
  - Root cause: Another off-by-one ID error.
- CSS hid all NiceGUI buttons and rotated all form fields.
  - Root cause: Disruptive global `.q-btn` and `.q-field` rules.
- Filter controls and results were created outside the intended dashboard layout.
  - Root cause: Widgets were instantiated before their containing layout blocks.

## Environment and Tooling

- No automated test files or test configuration were present.
  - Root cause: The training project relies on manual and integration validation.
- The selected virtual environment was missing declared dependencies, including `httpx`, FastAPI, and NiceGUI.
  - Root cause: Incomplete environment setup; validation used the system interpreter after installing missing packages through the supplied proxy.
- GitHub publishing could not be completed.
  - Root cause: The project is not a Git worktree, has no remote, and GitHub CLI authentication is unavailable.

## Validation Performed

- Python compilation passed.
- Application startup import passed.
- In-memory repository checks passed for seed behavior, CRUD, result mapping, filtering, searching, and targeted deletion.
- FastAPI integration checks passed for ticket listing, filters, search, creation, validation, missing records, and deletion.
- NiceGUI registration passed.
- Live checks passed for `/health`, `/api/tickets`, and the dashboard route `/`.
