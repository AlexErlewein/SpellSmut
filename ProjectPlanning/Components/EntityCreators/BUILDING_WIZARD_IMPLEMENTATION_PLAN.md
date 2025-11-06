# Building Wizard - Implementation Plan

## 1. Overview

This document outlines a concrete implementation plan for the **Building Wizard**, a new tool for creating and editing custom buildings in SpellForce. This plan is based on the successful completion of the research phase outlined in `BUILDING_CREATOR_PLAN.md`.

**Status**: 📋 PLANNING COMPLETE - READY FOR IMPLEMENTATION
**Priority**: Medium

## 2. Core Features

The Building Wizard will be a 6-step guided process, enabling users to:
1.  Define a building's core statistics (health, race, etc.).
2.  Establish its construction requirements (resources and dependencies).
3.  Assign a 3D model and other visual assets.
4.  Define its functions, such as unit training or research, by creating UI buttons.
5.  Automatically generate the required "building plan" item.
6.  Export all necessary data to the game files.

## 3. Implementation Phases

### Phase 1: Wizard Foundation & Core Stats (Week 1) - COMPLETED

- **Task 1.1: Create the Wizard UI Shell**
  - Create a new `BuildingWizard` class inheriting from `QWizard`.
  - Implement the 6-page structure with placeholder pages.
  - Integrate the wizard into the main application's "Tools" menu.

- **Task 1.2: Implement Step 1: Basic Properties**
  - Create a form for users to input core building stats identified during research:
    - `building_id` (using the shared `IDManager`)
    - `race` (dropdown enum)
    - `health` (integer input)
    - `name` and `description` (string inputs, will later link to `name_id` and `description_id`)
    - `required_building_id` (dropdown of existing buildings)
  - Create a `BuildingData` dataclass to hold the wizard's state.

### Phase 2: Asset & Resource Integration (Week 2) - UI IMPLEMENTED

- **Task 2.1: Implement Step 2: Visuals & Assets**
  - Create a UI for asset selection.
  - Based on research, this will primarily be based on **naming conventions**.
  - The UI will show a preview of model files found in `ExtractedAssets/Models/` that match the pattern `building_<race>_<name>`.
  - User will confirm the asset name to be used.

- **Task 2.2: Implement Step 3: Construction**
  - Create a UI to define the building's cost.
  - Allow users to add multiple resource requirements (e.g., Wood, Stone, Iron).
  - This page will write to the "building costs" data category, linking resource types and amounts to the `building_id`.

### Phase 3: Function Definition (Weeks 3-4) - UI IMPLEMENTED

- **Task 3.1: Implement Step 4: Functions & Buttons**
  - This is the most complex step. Create a UI to add "buttons" to the building's production menu.
  - A "button" can either train a unit or research an upgrade.
  - **For Unit Training:**
    - User selects a unit from a list (read from the `creature_stats` category).
    - The wizard automatically creates a button linking the `building_id` to the `unit_stats_id`.
  - **For Research/Upgrades:**
    - User defines an upgrade (e.g., "Improve Armor").
    - The wizard creates a button and links it to the appropriate action (this may require further research into the upgrade system).
  - The UI will allow setting resource costs and time for each button action.

### Phase 4: Automation & Export (Week 5) - UI IMPLEMENTED

- **Task 4.1: Implement Step 5: Building Plan**
  - This step will be mostly automated.
  - The wizard will automatically create a new entry in the `items` data category.
  - This item will have `item_type: BUILDING_PLAN_INVENTORY` and will be linked to the new `building_id`.
  - The user will be able to set the name for the plan (e.g., "Plan: Human Sawmill").

- **Task 4.2: Implement Step 6: Review & Export**
  - Create a summary page that displays all configured data for the new building.
  - Upon clicking "Finish", the wizard will write all the new entries to the respective data categories in `GameData.json` (or a mod-specific CFF file):
    - `buildings`
    - `building_costs`
    - `buttons`
    - `items` (for the plan)
    - `localisation` (for new names/descriptions)

### Phase 5: Testing & Refinement (Week 6)

- **Task 5.1: In-Game Testing**
  - Manually place the new building plan in the game world.
  - Test if the building can be constructed.
  - Test if the building's functions (training, research) work as configured.
- **Task 5.2: Bug Fixing and Polish**
  - Address any issues found during testing.
  - Improve UI/UX based on the creation workflow.

## 4. Data Dependencies

The wizard will need to read from and write to the following data categories (as identified in the research phase):

- **Read/Write:**
  - `buildings` (c2029)
  - `items` (c2003)
  - A new "building costs" category (to be identified or created).
  - A new "buttons" category (to be identified or created).
  - `localisation` (c2016)
- **Read-Only:**
  - `creature_stats` (c2024)
  - `races`

## 5. Success Criteria

- A non-technical user can successfully create a new, functional building from start to finish.
- The created building can be constructed in-game using its generated plan.
- The building's defined functions (e.g., training a unit) work correctly in-game.
- All necessary CFF data is generated correctly and without conflicts.
