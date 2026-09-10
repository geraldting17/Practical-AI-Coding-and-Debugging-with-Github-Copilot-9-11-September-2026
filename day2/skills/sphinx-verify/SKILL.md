---
name: sphinx-verify
description: "Verify a completed Sphinx documentation run: strict build evidence, phase order, local HTML links, anchors, assets, and navigation reachability. Use after generation or when checking a saved site."
user-invocable: true
---

# Sphinx Verify

## Purpose and Parameter

Check generated documentation without rebuilding it. The required `--run` parameter
is the completed pipeline run directory returned by `sphinx-build`, not its `html/`
subdirectory. No other parameters are required.

## Procedure and Example

1. Locate the exact successful run from the build result. Do not choose an arbitrary
   partial output or treat an old run as evidence for changed source.
2. Invoke the shared
   [skill implementation](./../../../Debugging%20Task/documentation_agent/sphinx_skills.py)
   from the repository root, substituting the actual run path:

```powershell
.\.venv\Scripts\python.exe "Debugging Task/documentation_agent/sphinx_skills.py" verify --run "<run-directory-returned-by-build>"
```

3. Inspect `site-verification.json`. Open the site for human navigation and visual
   review; use the application's link only when its server is running.
4. Fix broken local links, anchors, missing assets, or unreachable content in source
   guides/generation logic and rebuild. Do not patch only generated HTML.

## Expected Output

Exit 0 and JSON with page/link counts, reachable pages, an empty `errors` list,
external links not checked, and `human_review_required: true`. Results are also
written to the run's `site-verification.json`.

Exit 1 and a JSON error indicate missing/failed build evidence, invalid phase order,
Sphinx warnings/errors, or HTML navigation failures. HTML failures retain their
diagnostics in `site-verification.json`.

## Limitations

The check validates local HTML `href`/`src` targets, fragment IDs, and guide/reference
reachability from home. It does not execute JavaScript, inspect CSS resource URLs,
contact external URLs, check server health, or prove visual/factual correctness.
It verifies a saved build, not source freshness or evidence authenticity. Regenerate
after changes. Do not claim human approval or production readiness from this result.