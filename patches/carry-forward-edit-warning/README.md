# Carry Forward Shared Record Edit Warning

**Specify Support Ticket:** #597
**Reported by:** Emily Magnaghi (CAS Botany Collection Manager), Felice Bamford (data entry)
**Date:** February 12, 2026

## Problem

When using Carry Forward to create Collection Objects, Specify copies foreign keys — so every CO created in a session shares the same Locality record (via Collecting Event). If a user clicks the pencil icon to edit that Locality, they are mutating the single shared row in the database, silently overwriting the locality for every CO that references it.

This caused a production data integrity incident where an entire day's data entry had all localities overwritten to a single value. The damage could not be undone by editing individual records, because every edit propagated to all records again.

Specify's response (Grant Fitzsimmons, Feb 13 2026) confirmed this is "known behavior" and recommended hiding the edit button via form XML (`editBtn=false`) or training users to use Clone/Search/Add instead of Edit.

## Fix

Intercepts the edit button click on non-dependent QueryComboBox fields and shows a warning dialog:

> **Shared Record**
>
> This Locality record may be referenced by other records.
> Editing it will change the data for all records that share it.
> To make changes only for this record, clone it first.
>
> [Cancel] [Edit Shared] **[Clone and Edit]**

- **Clone and Edit** (primary action) — clones the record, re-points the current parent to the new copy, opens it for editing. Safe path.
- **Edit Shared** — proceeds to edit the shared record directly. For users who intentionally want to update all references.
- **Cancel** — dismisses the dialog.

Dependent fields (where the child record is owned by the parent) are unaffected.

## Files Changed

| File | Change |
|------|--------|
| `specifyweb/frontend/js_src/lib/components/QueryComboBox/index.tsx` | Add `SharedRecordWarningState`, intercept edit click, render warning dialog with Clone and Edit / Edit Shared / Cancel |
| `specifyweb/frontend/js_src/lib/localization/forms.ts` | Add 4 localization keys: `sharedRecordWarning`, `sharedRecordWarningDescription`, `editShared`, `cloneAndEdit` |
| `specifyweb/frontend/js_src/lib/components/QueryComboBox/__tests__/sharedRecordWarning.test.tsx` | 3 tests verifying localization strings exist and include table name |

## Applying

From the root of a specify7 checkout:

```bash
git apply patches/carry-forward-edit-warning/QueryComboBox-index.tsx.patch
git apply patches/carry-forward-edit-warning/forms.ts.patch
git apply patches/carry-forward-edit-warning/sharedRecordWarning.test.tsx.patch
```

Or apply all at once:

```bash
git apply patches/carry-forward-edit-warning/*.patch
```

## Testing

```bash
cd specifyweb/frontend/js_src
npx jest --testPathPattern=sharedRecordWarning --no-coverage
npx jest --testPathPattern=QueryComboBox --no-coverage  # full suite, 15 tests
```

## Target Version

Developed against specify7 main as of 2026-04-03 (commit `a25a847871`).
