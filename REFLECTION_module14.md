# Reflection — Module 14

## Overview

Module 14 built directly on top of the Module 13 foundation — user
registration, JWT auth, and a working API — by adding a full front-end
BREAD interface for calculations and a real CI/CD pipeline that gates
Docker Hub releases behind a passing Playwright E2E suite. The
functionality itself came together quickly. What took real time was a
multi-day debugging arc where four consecutive CI failures each looked
like they had an obvious cause, and three of those four "obvious causes"
turned out to be wrong.

## The Debugging Arc

### Failure 1: Docker login step failing silently

The `build-and-push` job was failing before it ever reached the Docker
build step. The root cause was a misconfigured secret reference in
`playwright.yml` — the workflow was pointing at the wrong secret name for
the Docker Hub token. Fixing the secret reference and re-verifying both
`DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` under repository settings
resolved this immediately.

**Lesson:** CI secrets fail silently and unhelpfully. Adding explicit
logging around any step that consumes a secret (without printing the
secret itself) turned a guessing game into a two-minute fix.

### Failure 2: Playwright timeouts on all calculation tests

Four tests — add, browse, edit, and delete — all failed with the same
error: `Page.fill: Timeout 30000ms exceeded, waiting for locator("#a")`.
The other 11 tests (pure API tests with no DOM interaction) passed fine.

My first hypothesis was a **DOM race condition**: perhaps
`calculations.js` was trying to attach event listeners or populate the
form before the page had finished loading. I patched the script to be
more defensive, wrapping calculation logic in a `DOMContentLoaded`
listener. This was reasonable, defensive code — but it did not fix the
failure.

### Failure 3: CSS flex layout

Still seeing the identical error, I looked at `style.css` next. The
`body` element had `display: flex` with no `flex-direction` specified,
defaulting to `row`. My hypothesis: the form, table, and header were
being laid out horizontally instead of stacking vertically, pushing form
inputs off-screen where Playwright couldn't interact with them.

I fixed this by adding `flex-direction: column`, which was a genuine
layout bug worth fixing on its own merits — the calculations page did
look wrong before this change. But the test suite still failed with the
exact same error afterward, which was the first real clue I was solving
real problems that weren't *the* problem.

### Failure 4 (the actual root cause): an untracked file

The breakthrough came from re-reading the error message literally
instead of assuming. Playwright's `fill()` command actively scrolls
elements into view as part of its actionability checks — meaning an
off-screen element due to CSS would resolve in milliseconds, not time
out after 30 seconds. A bare, one-line `waiting for locator("#a")` with
no additional detail almost always means the locator matched **zero
elements**, for the entire wait — not that the element was hidden or
obstructed.

Running `git ls-files static/` confirmed it: `calculations.html` was
**never committed to the repository**. It existed on my local disk,
rendered correctly in my own browser, and had for the entire debugging
session — but GitHub Actions' `checkout` step only pulls what Git
actually tracks. The CI runner was serving a 404 for a page that, from
my point of view, obviously existed.

```bash
git add static/calculations.html
git commit -m "Add missing calculations.html to version control"
git push
