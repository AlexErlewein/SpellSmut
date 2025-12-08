# NPC Chooser / Browser Spec

## Goal
Enable selecting quest giver, involved NPCs, and per-node speakers via a searchable, filterable browser.

## Data Sources
- sql_unit.lua (or CFF-derived unit/NPC tables) with IDs, names, race/faction, map/region hints.
- Localization tables for display names.
- Optional portrait/icon mapping if available.

## UI
- Search box + filters: race, faction, region/map.
- Results list with name (localized), ID, tags; keyboard navigation.
- Preview pane: portrait/icon (if any), location, brief info.
- Selection modes: single (quest giver/speaker) and multi (involved NPCs).

## Integration Points
- Properties tab: `questGiverNpcId` (single).
- Dialogue editor: set `speakerNpcId` per node (inline picker or side panel).
- Quest metadata: `involvedNpcIds[]` multi-select.
## Acceptance Criteria
- Fast search/filter; keyboard selection flows.
- Selected NPCs reflected immediately in Overview and Visual editors.
- Stable ID storage with localized display.
- Invalid/missing references flagged by validation.

## Implementation Notes
- Index units by lowercase name and tags for fast search.
- Provide debounce on search input; lazy-load large lists.
- Expose a minimal API to set/get `questGiverNpcId`, `involvedNpcIds`, and per-node `speakerNpcId`.

## Risks
- Incomplete location metadata → consider optional region annotations.
- Missing portraits → fallback to initials or generic icon.
