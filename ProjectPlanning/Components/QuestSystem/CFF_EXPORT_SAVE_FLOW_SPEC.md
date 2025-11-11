# CFF Export / Save Flow Spec

## Goals
- Save quests into GameData.cff with robust preview, conflict resolution, and localization handling.

## Flow
1. Validate project (blockers must be resolved).
2. Dry-Run: show planned changes (adds/updates to quests, localization, rewards).
3. ID Assignment: detect conflicts, suggest next-free ID; allow manual override.
4. Localization: generate/update keys (name, description, dialogue tags as needed).
5. Transactional export: create backup, write changes, report summary.

## UI
- Target file picker (GameData.cff).
- Dry-run panel (diff-like summary with counts and details).
- ID conflict widget (current, taken-by, suggested next-free, override field).
- Localization table editor with stub generation/import CSV.
- Final summary with backup path and timings.

## Validation
- Blocks export on invalid references/missing localization keys if configured.
- Warns on ambiguous mappings; provides fix suggestions.
## Technical Notes
- Maintain a persistent ID registry; scan CFF to compute next-free ranges (9000–9999 for new quests per plan).
- Use migration-friendly structure: additive where possible; avoid destructive edits unless confirmed.
- Localization strategy: ensure every displayed string has a key; generate stubs with language placeholders.
- Rollback on failure; emit structured log for audit.

## Acceptance Criteria
- Accurate dry-run reflecting all pending changes.
- Deterministic ID conflict resolution with override path.
- Complete localization generation with stubs for missing languages.
- Export produces a backup and a success/failure report.
