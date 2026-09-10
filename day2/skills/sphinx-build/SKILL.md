---
name: sphinx-build
description: "Generate a navigable Sphinx HTML documentation site from validated docstrings and optional guides. Run the docstring-first pipeline, regression tests, strict build, and link verification."
user-invocable: true
---

# Sphinx Build

## Purpose

Run the full five-phase workflow and build HTML without importing application
modules into Sphinx. This command also performs preflight and HTML verification;
it cannot bypass the staged docstring and regression gates.

## Parameters

| Parameter | Required | Meaning |
| --- | --- | --- |
| `--source` | Yes | Directory containing Python files explicitly listed in the plan. |
| `--plan` | Yes | JSON mapping source paths and qualified symbols to authored RST docstrings. |
| `--tests` | Yes | Trusted regression test directory. Tests run with staged source on `PYTHONPATH`. |
| `--output` | Yes | Parent directory for a fresh `run-*` artifact directory. |
| `--guides` | No | Directory of trusted `guide-*.rst` pages added to the site's navigation. |
| `--timeout` | No | Positive per-subprocess time limit in seconds; default 120. |

## Procedure and Example

1. Confirm documentation scope and inspect `sphinx-preflight` results. Review plan
   prose against source/tests; the script does not infer prose itself.
2. From the repository root, invoke the shared
   [skill implementation](./../../../Debugging%20Task/documentation_agent/sphinx_skills.py):

```powershell
.\.venv\Scripts\python.exe "Debugging Task/documentation_agent/sphinx_skills.py" build --source "Debugging Task/app" --plan "Debugging Task/documentation_agent/sample-plan.json" --tests "Debugging Task/documentation_agent/sample_tests" --guides "Debugging Task/documentation_agent/guides" --output "Debugging Task/documentation_agent/runs"
```

3. Inspect the final JSON `run` and `html` paths. Open the generated `html/index.html`
   and navigate between guide and model-reference pages. Check the sidebar and search.
4. Report results and request human review. Use `sphinx-verify` to recheck an existing
   artifact. Rebuild after source, guide, or dependency changes.

## Expected Output

Exit 0, phase progress, and a final JSON result with `status: passed`, run directory,
HTML index, and verification counts. Files include staged `source/`, generated
`sphinx/`, `html/`, `events.jsonl`, `regression.log`, `sphinx.log`, `review.json`,
`invocation.json`, and `site-verification.json`. Original source is not overwritten.

The build uses `-W --keep-going -E -a`: warnings and errors are failures, not ignored.
Failures return exit 1 and JSON on stderr. Pipeline-stage failures also record
`failure.json`; post-build HTML failures record `site-verification.json`. Partial
HTML from a failed run must not be presented as a successful deliverable.

## Safety and Review

Use only trusted code, tests, guides, and plans. Tests execute Python and Sphinx
processes directives; the runner is not a security sandbox. Review logs for secrets
before sharing. Never import `app.main` to generate documentation: it opens a database.
Do not weaken checks, publish, commit, or replace application files automatically.
The sample documents model symbols plus narrative UI/API/storage guides, not every
application function. Human approval remains separate from a successful build.