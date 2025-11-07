# Dialogue System Documentation

## Overview

The SpellForce CFF Editor includes a comprehensive **Dialog Branching Editor** that supports:
- Multi-level dialogue trees
- Player dialogue choices (branching conversations)
- NPC responses
- Conversation previews
- Quest integration

## Dialogue Node Structure

Each dialogue in the system is represented by a `DialogNode` with the following properties:

- **dialogue_name**: Unique identifier (e.g., `ashawe001`, `ashawe002`)
- **text**: The actual dialogue text shown in-game
- **speaker**: Either "NPC" or "Player"
- **is_player_choice**: Boolean flag indicating if this is a player choice
- **parent_choice**: Reference to which player choice led to this response
- **children**: List of follow-up dialogues (player choices or NPC responses)
- **order_index**: Sort order for multiple choices/responses

## How Player Choices Work

### Basic Conversation Flow

```
NPC: "Hello, adventurer! How can I help you?"
  ├─ Player Choice 1: "Tell me about the quest."
  │   └─ NPC Response: "The quest is to retrieve..."
  │       ├─ Player Choice: "I'll do it."
  │       └─ Player Choice: "Tell me more."
  └─ Player Choice 2: "Goodbye."
      └─ NPC Response: "Farewell, traveler."
```

### Creating Branching Dialogues

1. **Start with an NPC Dialogue** (root node)
   - Right-click → "Add Player Choice"
   - This creates options for what the player can say

2. **Add Multiple Player Choices**
   - Each choice represents a different response option
   - Players see these as clickable options in-game

3. **Add NPC Responses**
   - Right-click on a player choice → "Add NPC Response"
   - This is what the NPC says after the player selects that option

4. **Continue the Conversation**
   - From NPC responses, add more player choices
   - Create complex branching narratives

## Visual Representation

### In the Dialog Tree Widget

- **NPC Dialogues**: 
  - Bold text
  - Green color
  - Speaker column shows "NPC"

- **Player Choices**:
  - Italic text
  - Blue color (being updated to remove colors)
  - Speaker column shows "Player"

### Tree Structure Example

```
[NPC] ashawe001: "Welcome to our village!"
├─ [Player] ashawe002: "What can you tell me about this place?"
│  └─ [NPC] ashawe003: "We've lived here for generations..."
│     ├─ [Player] ashawe004: "Are there any problems?"
│     │  └─ [NPC] ashawe005: "Yes, bandits have been..."
│     └─ [Player] ashawe006: "Thank you for the information."
└─ [Player] ashawe007: "I must be going."
   └─ [NPC] ashawe008: "Safe travels!"
```

## Using the Dialog Branching Editor

### Location

The Dialog Branching Editor is accessible in two places:

1. **Quest Editor Tab**: Integrated into quest creation
2. **Standalone Dialog Editor Tab**: For creating dialogues independent of quests

### Interface Components

#### Left Side - Dialog Tree
- Hierarchical tree view of all dialogues
- Right-click for context menu options
- Click to select and edit

#### Right Side - Properties Panel
- **Dialog Name**: Auto-generated identifier
- **Speaker**: Dropdown to select NPC or Player
- **Dialog Text**: Edit the actual text
- **Conversation Preview**: Shows the full conversation path

### Controls

- **Add Root Dialog**: Create a new conversation starter
- **Add NPC Response**: Add what NPC says next (right-click menu)
- **Add Player Choice**: Add an option for player to respond (right-click menu)
- **Edit Dialog Text**: Modify the text (right-click or use properties panel)
- **Delete Dialog**: Remove a dialogue and all its branches
- **Update Dialog**: Save changes to the selected dialogue

## Best Practices

### Dialogue Naming Convention

Use a consistent naming pattern:
```
questname001 - First NPC dialogue
questname002 - First player choice option A
questname003 - First player choice option B
questname004 - NPC response to option A
questname005 - NPC response to option B
```

### Structuring Conversations

1. **Linear Path**: Simple back-and-forth
   ```
   NPC → Player → NPC → Player → NPC
   ```

2. **Branching Choices**: Multiple player options
   ```
   NPC → Player Choice A → NPC Response A
       → Player Choice B → NPC Response B
       → Player Choice C → NPC Response C
   ```

3. **Nested Branches**: Multi-level choices
   ```
   NPC → Player → NPC → Player Choice 1 → NPC → Player...
                      → Player Choice 2 → NPC → Player...
   ```

4. **Converging Paths**: Different choices lead to same outcome
   ```
   Player Choice A ──┐
   Player Choice B ──┼→ Same NPC Response
   Player Choice C ──┘
   ```

### Text Guidelines

- Keep player choices concise (one sentence)
- NPC responses can be longer
- Use clear language for player options
- Consider quest state and conditions

## Integration with Quests

### Quest-Dialog Relationship

Each quest can have associated dialogue trees:
- Quest start dialogues
- Quest progress dialogues
- Quest completion dialogues
- Optional flavor dialogues

### Linking to Quests

1. In the Quest Tree Editor, select a quest
2. Go to the "Dialogs" tab
3. The Dialog Branching Editor shows that quest's dialogues
4. Create and edit dialogues specific to that quest

## Example: Creating a Quest Dialogue

### Step 1: Create Root Dialogue
```
NPC: "I need your help, adventurer!"
```

### Step 2: Add Player Choices
```
├─ Player: "What do you need?"
├─ Player: "I'm busy right now."
└─ Player: "Tell me more."
```

### Step 3: Add NPC Responses
```
├─ Player: "What do you need?"
│  └─ NPC: "Bandits stole my family heirloom..."
│     ├─ Player: "I'll help you retrieve it." [Accept Quest]
│     └─ Player: "That's unfortunate, but I can't help."
├─ Player: "I'm busy right now."
│  └─ NPC: "I understand. Come back when you have time."
└─ Player: "Tell me more."
   └─ NPC: "My grandfather's sword was taken..."
      └─ Player: "What do you need?" [Loop back]
```

## Technical Details

### Data Structure

```python
class DialogNode:
    dialogue_name: str           # Unique identifier
    text: str                    # Dialogue text
    speaker: str                 # "NPC" or "Player"
    is_player_choice: bool       # True if player choice
    parent_choice: Optional[str] # Parent choice reference
    children: List[DialogNode]   # Follow-up dialogues
    order_index: int             # Sort order
```

### Serialization

Dialogues are saved as hierarchical JSON structures:
```json
{
  "dialogue_name": "quest001",
  "text": "Hello!",
  "speaker": "NPC",
  "is_player_choice": false,
  "children": [
    {
      "dialogue_name": "quest002",
      "text": "Hi there!",
      "speaker": "Player",
      "is_player_choice": true,
      "children": [...]
    }
  ]
}
```

## Known Limitations

1. Parent tracking in conversation preview is simplified
2. Circular dialogue references are not fully validated
3. Condition-based dialogue branching requires manual Lua scripting

## Future Enhancements

- Visual flow diagram view
- Condition editor for branching logic
- Voice acting metadata support
- Translation management
- Dialogue testing/playback mode

## See Also

- [Quest System Documentation](QUEST_SYSTEM.md)
- [Quest Hierarchy Guide](../tests/quest_hierarchy/README.md)
- [CFF Editor User Guide](USER_GUIDE.md)