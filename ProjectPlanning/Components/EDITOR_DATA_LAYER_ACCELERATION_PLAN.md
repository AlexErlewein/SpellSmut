## Editor Data Layer Acceleration Plan (CFF ? Cache/DB)

Last updated: 2025-10-29
Owner: TirganachReloaded Editor
Status: Proposed (ready for implementation)

### Goals and Success Criteria
- Reduce startup and quest/dialog browsing latency by avoiding full `.cff` re-parses during typical runs.
- Enable fast, user-triggered refresh from source `.cff` and a built-in diff workflow.
- Establish an upgrade path toward richer querying without sacrificing correctness.

**Success metrics**
- Cold load: ? 2s after initial cache/DB build.
- Quest view open: ? 500ms to display quest and dialogues.
- Refresh: ? 10s to rebuild from `.cff` on a modern machine.
- Diff: ? 5s for a visual text diff summary between two `.cff` files.

### Scope
- In scope
  - Local, fast data layer (cache now; optional DB next).
  - UI: ?Reload from CFF and Rebuild Cache??, ?Compare with??.
  - Data-layer validation/invalidation and integrity checks.
  - Optional: DB schema for quests/dialogues/localisation (Phase 2).
- Out of scope (for now)
  - Live filesystem watch of `.cff` changes.
  - Network/multi-user DB.
  - Editing in DB; `.cff` remains the write-back source of truth.

### Constraints and Assumptions
- Source of truth: `GameData.cff`.
- GUI expects a `GameData`-like API via `CFFDataModel`; minimize widget changes.
- Local filesystem storage only.
- Keep dependencies minimal; add SQLite/DuckDB only in Phase 2.

### Option Analysis
- Option A ? Serialized object cache (pickle of `GameData`)
  - Pros: minimal change, immediate speedup, preserves GUI.
  - Cons: Python-version dependent; opaque; limited ad?hoc queries.
  - When: MVP for quick wins.
- Option B ? SQLite/DuckDB database
  - Pros: structured, indexable, diffable; integrity checks; partial loads.
  - Cons: schema and access layer work.
  - When: richer queries and scale (quests/dialogues/localisation).

Decision: Phase 1 uses Option A; Phase 2 adds Option B.

### Functional Requirements
- Data layer
  - Initialize once from selected `.cff`.
  - Load from cache if fingerprint (path, size, mtime, SHA-256 partial) matches.
  - Rebuild on user request (?Reload from CFF and Rebuild Cache??).
  - Allow selecting alternative `.cff` on open.
- Diff
  - ?Compare with?? selects second `.cff`; compute differences (table/row/field).
  - Present diff in UI with option to save to file.
- UI
  - Add File menu entries: 
    - ?Reload from CFF and Rebuild Cache??
    - ?Compare with??
  - Show non-blocking progress in status bar; clear success/failure messages.
- Integrity
  - Detect stale/invalid cache; fall back to full parse and rebuild.
  - Display source fingerprint and build info (tooltip/About or info panel).

### Non-Functional Requirements
- Performance: meet success metrics above.
- Robustness: safe fallback to `.cff` parse on any cache/DB error.
- Portability: macOS (dev), should remain cross-platform.
- Security: local files only; handle untrusted inputs defensively.
- Observability: log timings for parse, cache load, DB build.

### Phase Plan

#### Phase 1: Object Cache MVP
- Storage
  - Directory: `src/TirganachReloaded/data/cache/`
  - Files: `GameData_{fingerprint}.pkl`, `GameData_{fingerprint}.meta.json`
  - Fingerprint: absolute path, file size, mtime, SHA-256 of first 32MB, `CACHE_VERSION`.
- Load strategy
  - On open: if fingerprint matches, load pickle; else parse `.cff`, then write cache+meta.
- UI
  - File ? ?Reload from CFF and Rebuild Cache??: force parse and rewrite cache; reload UI.
  - File ? ?Compare with??: pick second `.cff`, run comparator, show results; allow ?Save As??.
- Acceptance
  - Warm start uses cache and meets load target.
  - Refresh rebuilds and updates views correctly.

#### Phase 2: SQLite/DuckDB Read-Optimized Store (optional)
- Schema (initial focus)
  - `localisation(text_id INTEGER, language INTEGER, text TEXT, PRIMARY KEY(text_id, language))`
  - `quests(quest_id INTEGER PRIMARY KEY, name_id INTEGER, description_id INTEGER, ?)`
  - `quest_dialogs(dialog_id INTEGER PRIMARY KEY, quest_id INTEGER, speaker_id INTEGER, text_id INTEGER, next_dialog_id INTEGER, conditions TEXT, ?)`
  - Additional: `spells`, `items`, `item_ui`, `spell_names`, ?
  - `metadata(key TEXT PRIMARY KEY, value TEXT)`; include fingerprint and `SCHEMA_VERSION`.
- Ingestion
  - Parse `.cff` ? single-transaction populate with indices on hot columns.
- Integration
  - Introduce `DataProvider` abstraction in `CFFDataModel`:
    - `CFFProvider` (current `GameData` path) and `DBProvider` (SQL-backed) with the same consumer-facing methods for targeted views.
  - Start by switching quests/dialogues/localisation to `DBProvider`.
- Diff
  - Continue `tirganach.compare` or DB-level diffs via SQL joins.
- Acceptance
  - Quest/dialogue views meet sub-500ms target consistently, even on cold start.
  - Refresh rebuilds DB and reloads views.

#### Phase 3: UX and Reliability Enhancements
- Progress UI: modal with step breakdown and ETA (runs in worker thread to keep UI responsive).
- Cache/DB info panel: fingerprint, build time, source path, versions.
- Automated migrations: bump `CACHE_VERSION`/`SCHEMA_VERSION`; auto-rebuild when outdated.

### UI/UX Changes
- New File menu items:
  - ?Reload from CFF and Rebuild Cache??
  - ?Compare with??
- Status bar messages:
  - ?Loaded from cache in 0.34s? / ?Rebuilding from CFF?? with progress.
- Diff presentation:
  - Scrollable dialog with copy and save actions; optional export to Markdown.

### Data Model and API Notes
- Phase 1: extend `CFFDataModel.load_file` with cache awareness only (no widget changes).
- Phase 2: add `DataProvider` abstraction to minimize downstream changes.

### Testing and Validation
- Unit tests
  - Fingerprinting, cache write/read, invalidation on size/mtime/hash change.
  - Corrupted cache ? safe fallback.
- Integration tests
  - Cold start ? cache created; warm start ? cache used.
  - Refresh rebuild reflects changes in visible data (quests/spells).
  - Diff between Original and Modded `.cff` produces expected sample differences.
- Performance checks
  - Log timings for parse, cache load, DB load; assert thresholds in CI (where feasible).

### Risks and Mitigations
- Pickle portability across Python versions
  - Use `CACHE_VERSION` and graceful rebuild on mismatch.
- Memory footprint of pickled `GameData`
  - Accept for MVP; move to DB sooner if memory becomes an issue.
- Schema drift (Phase 2)
  - `SCHEMA_VERSION` with automatic rebuilds.

### Acceptance Criteria (MVP)
- Editor warm start ? 2s and shows ?Loaded from cache?.
- ?Reload from CFF and Rebuild Cache?? completes and updates views.
- ?Compare with?? returns readable differences and can be saved.

### Estimates
- Phase 1 (cache + UI + tests): 0.5?1 day.
- Phase 2 (SQLite/DuckDB + provider + targeted views + tests): 1?2 days.
- Phase 3 (UX polish, background workers, info panel): ~0.5 day.
