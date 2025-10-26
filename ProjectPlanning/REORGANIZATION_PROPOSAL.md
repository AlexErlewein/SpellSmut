# ProjectPlanning Directory Reorganization Proposal

## Current Issues Identified

### 1. Icon Extraction Documentation Fragmentation
**Problem**: 13+ files related to icon extraction scattered across locations
**Impact**: Difficult to find current status, redundant information

**Affected Files**:
- `Internal/ICON_EXTRACTION_*` (8 files)
- `ATLAS_EXTRACTION_SUMMARY.md`
- `GUI/ICON_*_SUMMARY.md` (2 files)
- `ICON_INVESTIGATION_PLAN.md`

### 2. GUI Planning Overlap
**Problem**: Multiple GUI-related planning files with overlapping content
**Impact**: Confusing status tracking, duplicate information

**Affected Files**:
- `EDITOR_PLANNING.md` (overview)
- `GUI/GUI_EDITOR_PLAN.md` (detailed implementation)
- `GUI/GUI_ICON_INTEGRATION_*` (2 files)
- `GUI/PENDING_ISSUES.md`

### 3. Quest Planning File Size
**Problem**: `QUEST_EDITOR_PLAN.md` is 370 lines - too detailed for planning directory
**Impact**: Planning directory becomes cluttered with implementation details

### 4. Status Document Scattering
**Problem**: Status updates spread across multiple files and locations
**Impact**: Hard to get complete project status at a glance

## Proposed New Structure

```
ProjectPlanning/
├── PROJECT_OVERVIEW.md           # ← NEW: Consolidated overview (created)
├── DOCS_STRUCTURE_MERMAID.md     # ← NEW: Docs visualization (created)
├── REORGANIZATION_PROPOSAL.md    # ← NEW: This file
│
├── Components/                   # ← NEW: Component-specific planning
│   ├── GUI_EDITOR.md            # ← Merge: EDITOR_PLANNING.md + GUI/*.md
│   ├── ICON_SYSTEM.md           # ← Merge: All icon-related files
│   ├── QUEST_EDITOR.md          # ← Move: QUEST_EDITOR_PLAN.md (summarized)
│   └── ASSET_EXTRACTION.md      # ← Merge: DATA_EXTRACTION_PLAN.md + status files
│
├── Status/                      # ← NEW: Current status tracking
│   ├── CURRENT_STATUS.md        # ← NEW: Live status overview
│   ├── COMPLETED_WORK.md        # ← Extract from MODDING_PLAN.md
│   └── BLOCKERS.md              # ← NEW: Current blockers and issues
│
├── Archive/                     # ← NEW: Old files (keep for reference)
│   ├── GUI/                     # ← Move all GUI/*.md files here
│   ├── Internal/                # ← Move Internal/*.md files here
│   └── Legacy/                  # ← Move standalone files here
│       ├── EDITOR_PLANNING.md
│       ├── MODDING_PLAN.md
│       ├── ICON_INVESTIGATION_PLAN.md
│       └── ATLAS_EXTRACTION_SUMMARY.md
│
└── README.md                    # ← NEW: Navigation guide
```

## Detailed Consolidation Plan

### 1. GUI Editor Consolidation
**Source Files**:
- `EDITOR_PLANNING.md` (high-level overview)
- `GUI/GUI_EDITOR_PLAN.md` (detailed implementation)
- `GUI/GUI_ICON_INTEGRATION_PLAN.md`
- `GUI/GUI_ICON_INTEGRATION_SUMMARY.md`
- `GUI/PENDING_ISSUES.md`

**Target**: `Components/GUI_EDITOR.md`

**Content Strategy**:
- Keep high-level overview from EDITOR_PLANNING.md
- Extract current status and next steps
- Summarize implementation details (not full technical specs)
- Create clear phase tracking

### 2. Icon System Consolidation
**Source Files**: 13+ icon-related files

**Target**: `Components/ICON_SYSTEM.md`

**Content Strategy**:
- Current status and achievements
- Technical findings and solutions
- Remaining challenges (mapping gap)
- Next steps and priorities
- Remove redundant status updates

### 3. Quest Editor Consolidation
**Source**: `Internal/QUEST_EDITOR_PLAN.md` (370 lines)

**Target**: `Components/QUEST_EDITOR.md`

**Content Strategy**:
- Keep executive summary and high-level plan
- Summarize technical specifications
- Extract current status and next steps
- Move detailed implementation to code comments or separate technical docs

### 4. Asset Extraction Consolidation
**Source Files**:
- `Internal/DATA_EXTRACTION_PLAN.md`
- `Internal/UV_MIGRATION_SUMMARY.md`
- Related status files

**Target**: `Components/ASSET_EXTRACTION.md`

**Content Strategy**:
- Current extraction capabilities
- Tool status and automation
- Future extraction needs
- Integration with other components

## Benefits of Reorganization

### 1. Improved Navigation
- **Clear hierarchy**: Overview → Components → Status → Archive
- **Logical grouping**: Related planning in single files
- **Current focus**: Active planning separated from historical

### 2. Reduced Maintenance Burden
- **Single source of truth** for each component
- **Consolidated status** instead of scattered updates
- **Easier updates** with focused, smaller files

### 3. Better Project Visibility
- **PROJECT_OVERVIEW.md** provides complete project status
- **Component files** give detailed status per area
- **Status directory** tracks current blockers and progress

## Implementation Steps

### Phase 1: Create New Structure
1. Create `Components/`, `Status/`, `Archive/` directories
2. Move existing files to `Archive/` (preserve history)
3. Create consolidated component files

### Phase 2: Content Consolidation
1. Extract relevant content from archived files
2. Remove redundancies and outdated information
3. Update with current status

### Phase 3: Update References
1. Update any internal links in documentation
2. Update README files to reference new structure
3. Update any scripts that reference moved files

## Migration Timeline

- **Week 1**: Create new structure and move files
- **Week 2**: Consolidate GUI and Icon components
- **Week 3**: Consolidate Quest and Asset components
- **Week 4**: Update references and test navigation

## Success Criteria

- ✅ **Navigation**: Can find any planning information within 3 clicks
- ✅ **Completeness**: No loss of important information
- ✅ **Currency**: All status information current and accurate
- ✅ **Maintenance**: Easier to update individual component status

## Risk Mitigation

- **Data Loss Prevention**: Archive all original files
- **Reference Updates**: Systematic update of internal links
- **Testing**: Verify all documentation links work
- **Rollback Plan**: Can restore from Archive/ if needed

---

*This proposal maintains all historical information while creating a cleaner, more maintainable structure for active planning.*