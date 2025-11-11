# Validation & Lua Syntax Checking UI Spec

## Goals
Provide a unified validation panel to surface quest/data issues and Lua syntax errors, with jump-to and quick-fix support.

## UI
- Validation panel with filters: Errors, Warnings, Info.
- Categories: Dialogue flow, Speaker assignment, References, Conditions, Rewards, Export readiness.
- Lua Check sub-panel: syntax output with file/line/col and jump-to.

## Behavior
- Runs automatically on change (debounced) and on demand.
- Annotates nodes inline with severity badges; status bar counts.
- Blocks export on Errors; allows export with Warnings if configured.

## Rules (initial)
- Orphaned/looping dialogue nodes.
- Missing speakers or invalid `speakerNpcId`.
- Broken references (items, quests, flags, NPCs).
- Invalid condition shapes/operands; negation misuse.
- Reward quantity/ID issues; duplicate item merge hints.
- Localization key missing for displayed strings.

## Lua Syntax
- Generate Lua temp output and run syntax check (non-interactive).
- Parse errors → map to originating node/section where possible.
## Acceptance Criteria
- Inline annotations and panel list are consistent and clickable.
- Lua syntax errors show line/column, with jump-to.
- Export is blocked on Errors and allowed with Warnings per settings.
- All initial rules implemented and unit-tested.

## Implementation Notes
- Validation engine operates on model; Lua check on generated code.
- Consider caching and incremental validation for large quests.
- Provide Quick Fix hooks for common issues (e.g., auto-assign default speaker, create missing localization keys).
