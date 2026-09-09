# Refactoring Rules

## Preserve Public Behavior

- Do not change API routes, request or response models, HTTP status codes, or error messages.
- Do not change the DuckDB schema, column order, timestamp handling, seed records, filters, search behavior, or result sorting.
- Do not change NiceGUI layout, notifications, callback order, or event behavior.

## Keep Persistence Explicit

- Keep SQL values parameterized.
- Keep database column names and result-to-model column ordering explicit.
- Extract SQL construction only when its query text and parameter ordering remain directly testable.

## Extract Purposeful Helpers

- Extract a helper only when it removes repeated knowledge or isolates a behavior that can be tested directly.
- Keep helpers private unless they form part of an existing public contract.
- Prefer immutable module constants for stable schema mappings, seed data, UI options, and static styles.

## Verify Narrowly Then Broadly

- Run focused tests for each changed module before running the full suite.
- Add focused regression tests for extracted helpers and preserved contracts.
- Do not make unrelated formatting, dependency, generated-output, or product-behavior changes.
