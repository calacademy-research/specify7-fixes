# Specify 7 Backlog — CAS Fix Candidates

Tracking file for CAS attempts at upstream Specify 7 bugs and regressions.
Source: [specify/specify7 GitHub Issues](https://github.com/specify/specify7/issues)

## Workflow

1. **Triage** — categorize issue as fixable / maybe / skip
2. **Test** — write a failing test that reproduces the bug
3. **Fix** — implement the fix on a `fix/issue-NNNN` branch
4. **Verify** — run test suite + eyetest if UI-facing
5. **Never PR upstream** — all work stays local in `calacademy-research/specify7-fixes`

## Status Key

| Status | Meaning |
|--------|---------|
| `triage` | Under evaluation |
| `ready` | Triaged as fixable, not yet started |
| `test` | Writing failing test |
| `fix` | Fix in progress |
| `done` | Fix + test complete |
| `skip` | Not feasible for AI fix |

---

## Tier 1 — Likely Fixable (clear bug, reproducible, code path identifiable)

| # | Title | Labels | Status | Branch | Notes |
|---|-------|--------|--------|--------|-------|
| [#7898](https://github.com/specify/specify7/issues/7898) | `Download All` button enabled when no attachments | regression, good-first-issue | `done` | `fix/issue-7898` | Fixed: added `disabled` prop when attachment count is 0 |
| [#7900](https://github.com/specify/specify7/issues/7900) | Create Interactions dialog duplicates "no records found" | regression | `ready` | | Duplicate render in dialog — likely React state or double-append |
| [#7870](https://github.com/specify/specify7/issues/7870) | Saving record without COT set causes infinite hang | regression | `done` | `fix/issue-7870` | Fixed: null guard on `collectionObjectType` in businessRuleDefs.ts |
| [#7664](https://github.com/specify/specify7/issues/7664) | GEOLocate fails with `"` or `'` in Locality name | bug | `done` | `fix/issue-7664` | Fixed: sanitize quotes from data before passing to GEOLocate URL |
| [#7387](https://github.com/specify/specify7/issues/7387) | `@` in MASTER_PASSWORD breaks SQLAlchemy queries | regression | `done` | `fix/issue-7387` | Fixed: `quote_plus()` on credentials in `get_sa_db_url()` |
| [#7376](https://github.com/specify/specify7/issues/7376) | Date precision not respected in formatted fields | bug | `done` | `fix/issue-7376` | Fixed: `make_expr` now applies `_dateformat` to temporal fields even when `format_expr` is False |
| [#7086](https://github.com/specify/specify7/issues/7086) | Column headers mismatch when reordering Query fields | bug | `done` | `fix/issue-7086` | Fixed: reorder fieldSpecs to match backend series column order |
| [#6699](https://github.com/specify/specify7/issues/6699) | Date field edits do not trigger Save button highlight | bug | `done` | `fix/issue-6699` | Fixed: added onChange handler for native date/month inputs |
| [#6808](https://github.com/specify/specify7/issues/6808) | Batch Edit: Date fields show incorrect `(Year)` heading | regression | `done` | `fix/issue-6808` | Fixed: date-part-aware field names in localization lookup + naive_field_format date suffix |
| [#6406](https://github.com/specify/specify7/issues/6406) | Table formats with null formatted field breaks conditional separator | bug | `done` | `fix/issue-6406` | Fixed: unwrap blank_nulls from relationship fields before separator logic |

## Tier 2 — Maybe Fixable (needs investigation, may be complex)

| # | Title | Labels | Status | Branch | Notes |
|---|-------|--------|--------|--------|-------|
| [#7840](https://github.com/specify/specify7/issues/7840) | WorkBench overrides CreatedByAgent with current user | regression | `triage` | | WB upload pipeline — may be deep in upload logic |
| [#7704](https://github.com/specify/specify7/issues/7704) | Linked Records dialog shows wrong Loan record | bug | `triage` | | Reporter could not reproduce — may be data-dependent |
| [#7667](https://github.com/specify/specify7/issues/7667) | Loan isClosed default value false ignored | bug | `triage` | | Default value handling for boolean fields |
| [#7585](https://github.com/specify/specify7/issues/7585) | Non-numeric formatter on numeric field causes errors | bug | `triage` | | Schema config validation gap — fix may be straightforward but needs investigation |
| [#7487](https://github.com/specify/specify7/issues/7487) | Simple search for numeric Catalog Numbers fails in CO | bug | `triage` | | Search/query logic, possibly formatter-related |
| [#6173](https://github.com/specify/specify7/issues/6173) | Host taxon Rank field no longer renders as picklist | regression | `triage` | | Cross-collection rendering — "only in production" |
| [#5484](https://github.com/specify/specify7/issues/5484) | Taxon Tiles: proportion and name inconsistencies | bug, verified | `triage` | | Tree query logic — may be complex |

## Tier 3 — Skip (too vague, unreproducible, or needs upstream coordination)

| # | Title | Labels | Reason |
|---|-------|--------|--------|
| [#7418](https://github.com/specify/specify7/issues/7418) | TransactionManagementError saving CO form | bug | Only reproducible in one specific database |
| [#7573](https://github.com/specify/specify7/issues/7573) | Can't attach >2000 COs to Accession | bug, performance | Likely needs schema/API pagination design decision |
| [#7572](https://github.com/specify/specify7/issues/7572) | Lock/wait timeout adding large RecordSet to Accession | bug, performance | Database-level concurrency issue |
| [#7515](https://github.com/specify/specify7/issues/7515) | Paginate delete blockers for large DBs | performance | Feature/design work, not a bug fix |
| [#6015](https://github.com/specify/specify7/issues/6015) | Different default sorting for Catalog Number queries | regression | Sorting behavior change may be intentional with SQLAlchemy update |

---

## Notes

- All work targets the `main` branch of `specify/specify7` as of the fork date (2026-04-03).
- Test framework: Python (`pytest`) for backend, frontend tests TBD (Jest/Vitest per existing setup).
- Sync upstream periodically: `git fetch upstream && git rebase upstream/main main`
