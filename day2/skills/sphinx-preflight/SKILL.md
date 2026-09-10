---
name: sphinx-preflight
description: "Check Sphinx dependencies, Python documentation scope, docstring plans, and guide inputs before generating a documentation site. Use before sphinx-build."
user-invocable: true
---

# Sphinx Preflight

## Purpose

Validate documentation inputs without modifying application files, running tests,
or invoking Sphinx. Reuse the existing pipeline's AST and docstring-plan checks.

## Parameters

| Parameter | Required | Meaning |
| --- | --- | --- |
| `--source` | Yes | Directory containing source-relative Python files named in the plan. |
| `--plan` | Yes | JSON `files` mapping from relative paths to qualified symbol/docstring mappings. |
| `--tests` | Yes | Trusted directory containing applicable `test*.py` tests. |
| `--guides` | No | Trusted directory of `guide-*.rst` narrative pages. |
| `--timeout` | No | Positive timeout for subsequent subprocesses; default 120 seconds. |

## Procedure

1. Read the source and tests, confirm scope, and author factual docstrings in the
   plan. For this workspace the sample targets `Debugging Task/app/models.py`.
2. Use the application virtual environment with the documentation requirements
   installed. Missing packages cause a nonzero exit; do not silently change the
   application's dependency constraints.
3. Run the `preflight` command in the shared
   [skill implementation](./../../../Debugging%20Task/documentation_agent/sphinx_skills.py)
   from the repository root:

```powershell
.\.venv\Scripts\python.exe "Debugging Task/documentation_agent/sphinx_skills.py" preflight --source "Debugging Task/app" --plan "Debugging Task/documentation_agent/sample-plan.json" --tests "Debugging Task/documentation_agent/sample_tests" --guides "Debugging Task/documentation_agent/guides"
```

4. Inspect the JSON result. Correct missing targets, invalid paths, dependencies,
   or guide inputs before calling `sphinx-build`. Preflight success does not mean
   tests or Sphinx have passed.

## Expected Output

Exit 0 and JSON with `status: passed`, dependency versions, scoped files, guide
pages, and docstring count. The sample expects 8 docstring targets and 5 guide
pages. Failures exit 1 with a JSON error on stderr. Temporary analysis files are
removed automatically. Source files remain unchanged.

## Boundaries

Read only trusted sources and plans. Python syntax and AST equivalence do not prove
documentation accuracy. Additional project dependencies are checked when regression
tests actually run. Do not suppress an error or claim the build has run.