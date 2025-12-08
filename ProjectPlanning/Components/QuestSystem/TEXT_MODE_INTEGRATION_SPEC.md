# Text Mode (ASCII) Overview Integration Spec

## Goals
- Provide a keyboard-first, text/ASCII overview for quest structure and dialogues.
- Keep the existing visual dialogue editor for detailed node editing.
- Ensure live two-way sync between Overview (Text) and Visual modes.

## UX Overview
- Tabs: Overview (Text) | Dialogue (Visual) | Properties | Rewards | Requirements
- Overview shows an indented, readable tree of dialogue and actions with node IDs.
- Inline quick actions: edit, add reply, branch, delete, reorder.
- Command palette for power users.

## Layout
- Left: Search/filter and jump-to.
- Center: ASCII tree with nodes (#id), choices (-> [A]/[B]), and actions.
- Right: Context panel (node details, speaker, conditions).

## Sync & Data Model
- Read/write live model shared with Visual editor.
- Editing in either view updates the other immediately.
- Nodes: id, speakerNpcId, text/tag, answers[], conditions[], actions[].
## ASCII Tree Format
```
[ Quest Editor - Text Mode ]  [Ctrl+S Save] [V Validate] [E Export]
Quest: [QID 9031]  "Lost Hammer"   Campaign: [FreeGame]  Type: [Side]

Dialog Tree
  #1  (NPC) Rolf: "Greetings, traveler."            [edit] [add reply] [del]
    -> [A] (Player): "Need help?"                   [edit] [branch]    [del]
         #2  (NPC) Rolf: "I've lost my hammer."     [edit] [add reply] [del]
           -> [A] (Player): "I'll find it."         [edit] [branch]    [del]
                #3  (Action): AddObjective "Find Hammer"  [edit] [del]
           -> [B] (Player): "Not interested."       [edit] [branch]    [del]
                #4  (NPC) Rolf: "Very well."        [edit] [del]

[+] Add Node   [F] Find   [R] Reorder   [C] Conditions   [H] Help
```

## Keyboard Shortcuts
- Enter: edit
- A: add reply / add node
- Del/Backspace: delete
- R: reorder (move up/down)
- S: set speaker (opens NPC chooser)
- C: toggle/open conditions editor
- Cmd/Ctrl+F: search

## Validation Indicators
- Inline [ERROR]/[WARN]/[INFO] badges on nodes.
- Status bar summary with counts; click to filter.
## Acceptance Criteria
- Edits in Text Mode reflect in Visual mode immediately (and vice versa).
- Users can add/edit/remove nodes, choices, speakers, conditions.
- Search/jump-to navigates large trees quickly.
- Exported Lua matches Visual-only output for equivalent data.

## Implementation Notes
- Use existing data models; add lightweight renderer for ASCII.
- Diff-aware apply: operations generate model mutations, not string diffs.
- Support large dialogues with virtualized rendering (paginate or lazy-load).

## Risks
- Large trees may be hard to scan: mitigate via filters and collapse.
- Command discoverability: mitigate with command palette and help overlay.
