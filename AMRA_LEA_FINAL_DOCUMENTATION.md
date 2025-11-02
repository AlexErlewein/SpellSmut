# Amra and Lea - Complete Quest Documentation (Final with Maps)

## Quest Tree Overview

```
📜 Quest 379: Amra and Lea (Main Quest)
    ├── 📋 Quest 380: Talk to Sunder in Liannon about Amra's armor
    ├── 📋 Quest 381: Ask Shan Muir about Arma and Lea
    ├── 📋 Quest 382: Examine the events by the house of the Muir family in Liannon.
    ├── 📋 Quest 383: A search of the aggressors should deliver further information.
    ├── 📋 Quest 384: Confront Sentos in Greyfell
    ├── 📋 Quest 385: Sentos wants to meet with you at the Wildland Pass.
    ├── 📋 Quest 393: Renewed troubles with Sentos
    ├── 📋 Quest 386: Interogate Sentos once again
    ├── 📋 Quest 387: Look for Lea's grave in Whisper
    ├── 📋 Quest 388: Bring Lea's possessions to Shan in Liannon
    ├── 📋 Quest 389: Talk to Tyrgar in Liannon
    ├── 📋 Quest 390: Craig Un'Shallach is our last hope
    ├── 📋 Quest 391: Look for Amra's grave in the desert areas.
```

---

## Data Sources

### Extraction Information
- **CFF File**: `GameData.cff` - Quest metadata, names, IDs
- **Original Lua Scripts**: `OriginalGameFiles/modding/Original Scripts/`
- **Modding Lua Sources**: `ModdingTools/SpellForceLUASources/`
- **Quest Rewards**: `script/GdsQuestRewards.lua`
- **Map Locations**: Extracted from Lua file paths

### Extraction Date
- **Generated**: 2025-11-02
- **CFF Parser**: TirganachReloaded.tirganach
- **Total Quests**: 14 (1 main + 13 subquests)

---

## Quest 379: Amra and Lea

### CFF Metadata
- **Quest ID**: 379
- **Parent Quest ID**: 0
- **Quest Name**: Amra and Lea
- **Name String ID**: 13461
- **Description String ID**: 13462
- **Order Index**: 0

### Map Locations

- **P15**: Desert / Burning Sands
- **P63**: Greyfell

### File References

**Total Files**: 2  
**Total Quest References**: 290  

- `Original Scripts/script/P15/n0.lua` (1 references)
- `Original Scripts/script/P63/n2896.lua` (289 references)

### Dialogues Extracted from Lua

**Total Unique Dialogues**: 3

1. **German**: "Das ist das Ende Deiner Reise! Du wirst meinen Herrn nie erreichen!"
   - *Source*: `Original Scripts/script/P15/n0.lua`

2. **German**: "Lasst die Horde ausrcken! Zerfetzt sie!"
   - *Source*: `Original Scripts/script/P15/n0.lua`

3. **German**: "ffnet das Tor!"
   - *Source*: `Original Scripts/script/P15/n0.lua`

---

## Quest 380: Talk to Sunder in Liannon about Amra's armor

### CFF Metadata
- **Quest ID**: 380
- **Parent Quest ID**: 379
- **Quest Name**: Talk to Sunder in Liannon about Amra's armor
- **Name String ID**: 13463
- **Description String ID**: 13464
- **Order Index**: 1

### Map Locations

- **P63**: Greyfell

### File References

**Total Files**: 2  
**Total Quest References**: 74  

- `Original Scripts/script/P63/n2896.lua` (1 references)
- `Original Scripts/script/p1/n1390.lua` (73 references)

### Extended Story Dialogues

*These dialogues provide narrative context and were extracted from detailed NPC conversations:*

**German**: "Ich suche nach Amras Rüstung! Orthanc sandte mich zu Euch!"  
**English**: "I'm searching for Amra's armor! Orthanc sent me to you!"

**German**: "Amra? Amra ist fort! Lea ist fort! Nur die Götter wissen, was aus ihnen geworden ist!"  
**English**: "Amra? Amra is gone! Lea is gone! Only the gods know what became of them!"

**German**: "Amra war ein Krieger - ein Hitzkopf! Aber das Herz am rechten Fleck!"  
**English**: "Amra was a warrior - a hothead! But with his heart in the right place!"

**German**: "Und Lea? Lea war das schönste Geschöpf, das die Welt je erblickt hat!"  
**English**: "And Lea? Lea was the most beautiful creature the world has ever seen!"

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraUndLea1Liannon1 = { XP = {200}}
```

---

## Quest 381: Ask Shan Muir about Arma and Lea

### CFF Metadata
- **Quest ID**: 381
- **Parent Quest ID**: 379
- **Quest Name**: Ask Shan Muir about Arma and Lea
- **Name String ID**: 13465
- **Description String ID**: 13466
- **Order Index**: 2

### Map Locations

- **P1**: Liannon

### File References

**Total Files**: 2  
**Total Quest References**: 1154  

- `Original Scripts/script/p1/n1390.lua` (1 references)
- `Original Scripts/script/p1/n1394.lua` (1153 references)

### Extended Story Dialogues

*These dialogues provide narrative context and were extracted from detailed NPC conversations:*

**German**: "Ihr müsst wissen, Amra verdingte sich einst als Söldner für meinen Vater!"  
**English**: "You must know, Amra once served as a mercenary for my father!"

**German**: "So schickte mein Vater Amra fort! Lea gab ihm als Zeichen ihrer Gunst ihren wertvollsten Besitz, das Pfand der Götter!"  
**English**: "So my father sent Amra away! Lea gave him as a sign of her favor her most valuable possession, the Pledge of the Gods!"

**German**: "Tyrgar, der Fischer, war einer der Waffenbrüder Amras!"  
**English**: "Tyrgar, the fisherman, was one of Amra's warrior brothers!"

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraUndLea1Liannon2 = { XP = {400}}
```

---

## Quest 382: Examine the events by the house of the Muir family in Liannon.

### CFF Metadata
- **Quest ID**: 382
- **Parent Quest ID**: 379
- **Quest Name**: Examine the events by the house of the Muir family in Liannon.
- **Name String ID**: 13467
- **Description String ID**: 13468
- **Order Index**: 3

### Map Locations

- **P1**: Liannon

### File References

**Total Files**: 2  
**Total Quest References**: 3  

- `Original Scripts/script/p1/n0.lua` (2 references)
- `Original Scripts/script/p1/n1394.lua` (1 references)

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraUndLea2Liannon1 = { XP = {500}}
```

---

## Quest 383: A search of the aggressors should deliver further information.

### CFF Metadata
- **Quest ID**: 383
- **Parent Quest ID**: 379
- **Quest Name**: A search of the aggressors should deliver further information.
- **Name String ID**: 13469
- **Description String ID**: 13470
- **Order Index**: 4

### Map Locations

- **P1**: Liannon

### File References

**Total Files**: 1  
**Total Quest References**: 3  

- `Original Scripts/script/p1/n0.lua` (3 references)

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraUndLea2Liannon2 = { XP = {300}}
```

---

## Quest 384: Confront Sentos in Greyfell

### CFF Metadata
- **Quest ID**: 384
- **Parent Quest ID**: 379
- **Quest Name**: Confront Sentos in Greyfell
- **Name String ID**: 13471
- **Description String ID**: 13472
- **Order Index**: 5

### Map Locations

- **P63**: Greyfell

### File References

**Total Files**: 2  
**Total Quest References**: 8  

- `Original Scripts/script/P63/n2897.lua` (7 references)
- `Original Scripts/script/p1/n0.lua` (1 references)

### Extended Story Dialogues

*These dialogues provide narrative context and were extracted from detailed NPC conversations:*

**German**: "Ihr sucht nach der Rüstung Amras, nicht wahr?"  
**English**: "You're searching for Amra's armor, aren't you?"

**German**: "Schön! Lasst uns reden... aber nicht hier! Die Stadt hat zu viele Ohren! Trefft mich am Wildland Pass!"  
**English**: "Good! Let's talk... but not here! The city has too many ears! Meet me at Wildland Pass!"

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraUndLea3Sentos = { XP = {500}}
```

---

## Quest 385: Sentos wants to meet with you at the Wildland Pass.

### CFF Metadata
- **Quest ID**: 385
- **Parent Quest ID**: 379
- **Quest Name**: Sentos wants to meet with you at the Wildland Pass.
- **Name String ID**: 13473
- **Description String ID**: 13474
- **Order Index**: 6

### Map Locations

- **P6**: Wildland Pass / Greyfell area
- **P63**: Greyfell

### File References

**Total Files**: 3  
**Total Quest References**: 23  

- `Original Scripts/script/P6/n2898.lua` (18 references)
- `Original Scripts/script/P63/n0.lua` (1 references)
- `Original Scripts/script/P63/n2897.lua` (4 references)

### Dialogues Extracted from Lua

**Total Unique Dialogues**: 3

1. **German**: "Da sind sie!"
   - *Source*: `Original Scripts/script/P63/n0.lua`

2. **German**: "Der Runenkrieger ist zurck! Schnell Ihr msst ins Haupthaus des Ordens kommen!"
   - *Source*: `Original Scripts/script/P63/n0.lua`

3. **German**: "Haltet sie von der Stadt fern!"
   - *Source*: `Original Scripts/script/P63/n0.lua`

### Extended Story Dialogues

*These dialogues provide narrative context and were extracted from detailed NPC conversations:*

**German**: "Ihr seid doch auf der Suche nach Lea und Amra, nicht wahr?"  
**English**: "You're searching for Lea and Amra, aren't you?"

**German**: "Ich weiß nur... dass es ein Grab gibt... eine Grabstätte in Wisper... man sagt, Lea liege dort!"  
**English**: "I only know... that there is a grave... a tomb in Wisper... they say Lea lies there!"

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraUndLea2Sentos = { XP = {800}}
```

---

## Quest 393: Renewed troubles with Sentos

### CFF Metadata
- **Quest ID**: 393
- **Parent Quest ID**: 379
- **Quest Name**: Renewed troubles with Sentos
- **Name String ID**: 14152
- **Description String ID**: 14153
- **Order Index**: 7

### Map Locations

- **P6**: Wildland Pass / Greyfell area

### File References

**Total Files**: 5  
**Total Quest References**: 5  

- `Original Scripts/script/P6/n0.lua` (1 references)
- `Original Scripts/script/P6/n2898.lua` (1 references)
- `Original Scripts/script/P6/n2899.lua` (1 references)
- `Original Scripts/script/P6/n2900.lua` (1 references)
- `Original Scripts/script/P6/n2901.lua` (1 references)

### Dialogues Extracted from Lua

**Total Unique Dialogues**: 3

1. **German**: "Los Mnner! Zum Monument!"
   - *Source*: `Original Scripts/script/P6/n0.lua`

2. **German**: "Nein! Die Gtter mgen Euch verfluchen, Runensklave! Aargh!"
   - *Source*: `Original Scripts/script/P6/n0.lua`

3. **German**: "Steht nicht so rum! Ttet irgendwas!"
   - *Source*: `Original Scripts/script/P6/n0.lua`

---

## Quest 386: Interogate Sentos once again

### CFF Metadata
- **Quest ID**: 386
- **Parent Quest ID**: 379
- **Quest Name**: Interogate Sentos once again
- **Name String ID**: 13475
- **Description String ID**: 13476
- **Order Index**: 8

### Map Locations

- **P6**: Wildland Pass / Greyfell area

### File References

**Total Files**: 2  
**Total Quest References**: 2  

- `Original Scripts/script/P6/n0.lua` (1 references)
- `Original Scripts/script/P6/n2898.lua` (1 references)

### Dialogues Extracted from Lua

**Total Unique Dialogues**: 3

1. **German**: "Los Mnner! Zum Monument!"
   - *Source*: `Original Scripts/script/P6/n0.lua`

2. **German**: "Nein! Die Gtter mgen Euch verfluchen, Runensklave! Aargh!"
   - *Source*: `Original Scripts/script/P6/n0.lua`

3. **German**: "Steht nicht so rum! Ttet irgendwas!"
   - *Source*: `Original Scripts/script/P6/n0.lua`

---

## Quest 387: Look for Lea's grave in Whisper

### CFF Metadata
- **Quest ID**: 387
- **Parent Quest ID**: 379
- **Quest Name**: Look for Lea's grave in Whisper
- **Name String ID**: 13477
- **Description String ID**: 13478
- **Order Index**: 9

### Map Locations

- **P6**: Wildland Pass / Greyfell area

### File References

**Total Files**: 10  
**Total Quest References**: 11  

- `Original Scripts/script/P6/n2898.lua` (1 references)
- `Original Scripts/script/p1/n0.lua` (1 references)
- `Original Scripts/script/p16/n0.lua` (1 references)
- `Original Scripts/script/p16/n2903.lua` (2 references)
- `Original Scripts/script/p16/n2909.lua` (1 references)
- `Original Scripts/script/p16/n5163.lua` (1 references)
- `Original Scripts/script/p16/n5164.lua` (1 references)
- `Original Scripts/script/p16/n5165.lua` (1 references)
- `Original Scripts/script/p16/n5166.lua` (1 references)
- `Original Scripts/script/p16/n5167.lua` (1 references)

### Dialogues Extracted from Lua

**Total Unique Dialogues**: 3

1. **German**: "Ah, mein treuer Freund!"
   - *Source*: `Original Scripts/script/p16/n0.lua`

2. **German**: "Das ist Dein Ende, Totenbeschwrer! Meine Rache ist nah!"
   - *Source*: `Original Scripts/script/p16/n0.lua`

3. **German**: "Kommt nur! Gleich werdet Ihr Bekanntschaft mit dem Tod schlieen!"
   - *Source*: `Original Scripts/script/p16/n0.lua`

---

## Quest 388: Bring Lea's possessions to Shan in Liannon

### CFF Metadata
- **Quest ID**: 388
- **Parent Quest ID**: 379
- **Quest Name**: Bring Lea's possessions to Shan in Liannon
- **Name String ID**: 13479
- **Description String ID**: 13480
- **Order Index**: 10

### Map Locations

- **P1**: Liannon

### File References

**Total Files**: 3  
**Total Quest References**: 3  

- `Original Scripts/script/p1/n0.lua` (1 references)
- `Original Scripts/script/p1/n1394.lua` (1 references)
- `Original Scripts/script/p16/n0.lua` (1 references)

### Dialogues Extracted from Lua

**Total Unique Dialogues**: 3

1. **German**: "Ah, mein treuer Freund!"
   - *Source*: `Original Scripts/script/p16/n0.lua`

2. **German**: "Das ist Dein Ende, Totenbeschwrer! Meine Rache ist nah!"
   - *Source*: `Original Scripts/script/p16/n0.lua`

3. **German**: "Kommt nur! Gleich werdet Ihr Bekanntschaft mit dem Tod schlieen!"
   - *Source*: `Original Scripts/script/p16/n0.lua`

---

## Quest 389: Talk to Tyrgar in Liannon

### CFF Metadata
- **Quest ID**: 389
- **Parent Quest ID**: 379
- **Quest Name**: Talk to Tyrgar in Liannon
- **Name String ID**: 13481
- **Description String ID**: 13482
- **Order Index**: 11

### Map Locations

- **P1**: Liannon

### File References

**Total Files**: 2  
**Total Quest References**: 34  

- `Original Scripts/script/p1/n1394.lua` (1 references)
- `Original Scripts/script/p1/n1396.lua` (33 references)

---

## Quest 390: Craig Un'Shallach is our last hope

### CFF Metadata
- **Quest ID**: 390
- **Parent Quest ID**: 379
- **Quest Name**: Craig Un'Shallach is our last hope
- **Name String ID**: 13483
- **Description String ID**: 13484
- **Order Index**: 12

### Map Locations

- **P25**: Godmark / Mountains
- **P7**: Ice Gate

### File References

**Total Files**: 3  
**Total Quest References**: 77  

- `Original Scripts/script/P25/n2910.lua` (20 references)
- `Original Scripts/script/P7/n4010.lua` (56 references)
- `Original Scripts/script/p1/n1396.lua` (1 references)

### Extended Story Dialogues

*These dialogues provide narrative context and were extracted from detailed NPC conversations:*

**German**: "Wochenlang irrten wir in der Wüstenei umher! Amra war wie rasend!"  
**English**: "For weeks we wandered through the desert! Amra was like a madman!"

**German**: "Ja! Ein Magier mit dunkler Kapuze, und von unglaublicher Macht!"  
**English**: "Yes! A magician with a dark hood, and of incredible power!"

**German**: "Als ich erwachte, fand ich Amra tot neben mir! Das Pfand der Götter war verschwunden."  
**English**: "When I awoke, I found Amra dead beside me! The Pledge of the Gods had disappeared."

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraUndLea4 = { XP = {1200}}
```

---

## Quest 391: Look for Amra's grave in the desert areas.

### CFF Metadata
- **Quest ID**: 391
- **Parent Quest ID**: 379
- **Quest Name**: Look for Amra's grave in the desert areas.
- **Name String ID**: 13485
- **Description String ID**: 13486
- **Order Index**: 13

### Map Locations

- **P15**: Desert / Burning Sands
- **P25**: Godmark / Mountains
- **P7**: Ice Gate

### File References

**Total Files**: 35  
**Total Quest References**: 47  

- `Original Scripts/script/P15/n0.lua` (2 references)
- `Original Scripts/script/P15/n2911.lua` (2 references)
- `Original Scripts/script/P15/n2912.lua` (1 references)
- `Original Scripts/script/P15/n5088.lua` (1 references)
- `Original Scripts/script/P15/n5089.lua` (1 references)
- `Original Scripts/script/P15/n5090.lua` (1 references)
- `Original Scripts/script/P15/n5091.lua` (1 references)
- `Original Scripts/script/P15/n5092.lua` (1 references)
- `Original Scripts/script/P15/n5093.lua` (1 references)
- `Original Scripts/script/P15/n5094.lua` (1 references)
- `Original Scripts/script/P15/n5095.lua` (1 references)
- `Original Scripts/script/P15/n5096.lua` (1 references)
- `Original Scripts/script/P15/n5097.lua` (1 references)
- `Original Scripts/script/P15/n5098.lua` (1 references)
- `Original Scripts/script/P15/n5099.lua` (1 references)
- `Original Scripts/script/P15/n5100.lua` (1 references)
- `Original Scripts/script/P15/n5101.lua` (1 references)
- `Original Scripts/script/P15/n5102.lua` (1 references)
- `Original Scripts/script/P15/n5103.lua` (1 references)
- `Original Scripts/script/P15/n5104.lua` (1 references)
- `Original Scripts/script/P15/n5105.lua` (1 references)
- `Original Scripts/script/P15/n5106.lua` (1 references)
- `Original Scripts/script/P15/n5107.lua` (1 references)
- `Original Scripts/script/P15/n5108.lua` (1 references)
- `Original Scripts/script/P15/n5109.lua` (1 references)
- `Original Scripts/script/P15/n5110.lua` (1 references)
- `Original Scripts/script/P15/n5111.lua` (1 references)
- `Original Scripts/script/P15/n5112.lua` (1 references)
- `Original Scripts/script/P15/n5113.lua` (1 references)
- `Original Scripts/script/P15/n5114.lua` (1 references)
- `Original Scripts/script/P15/n5115.lua` (1 references)
- `Original Scripts/script/P15/n5116.lua` (1 references)
- `Original Scripts/script/P15/n5117.lua` (1 references)
- `Original Scripts/script/P25/n2910.lua` (4 references)
- `Original Scripts/script/P7/n4010.lua` (8 references)

### Dialogues Extracted from Lua

**Total Unique Dialogues**: 3

1. **German**: "Das ist das Ende Deiner Reise! Du wirst meinen Herrn nie erreichen!"
   - *Source*: `Original Scripts/script/P15/n0.lua`

2. **German**: "Lasst die Horde ausrcken! Zerfetzt sie!"
   - *Source*: `Original Scripts/script/P15/n0.lua`

3. **German**: "ffnet das Tor!"
   - *Source*: `Original Scripts/script/P15/n0.lua`

### Extended Story Dialogues

*These dialogues provide narrative context and were extracted from detailed NPC conversations:*

**German**: "(Hier fiel Amra im ehrenvollen Kampf)"  
**English**: "(Here Amra fell in honorable combat)"

**German**: "(Ein verwitterter Grabstein)"  
**English**: "(A weathered tombstone)"

### Quest Reward

From `script/GdsQuestRewards.lua`:
```lua
AmraLeaGrab = { XP = {800}}, AmraUndLea5 = { XP = {1200}}
```

---

## Map Overview

### All Locations Used in Quest Chain

- **P1** - Liannon
  - Used in quests: 381, 382, 383, 388, 389

- **P15** - Desert / Burning Sands
  - Used in quests: 379, 391

- **P25** - Godmark / Mountains
  - Used in quests: 390, 391

- **P6** - Wildland Pass / Greyfell area
  - Used in quests: 385, 386, 387, 393

- **P63** - Greyfell
  - Used in quests: 379, 380, 384, 385

- **P7** - Ice Gate
  - Used in quests: 390, 391

---

## Summary Statistics

- **Total Quests**: 14 (1 main + 13 subquests)
- **Total Lua Files**: 55
- **Total Quest References in Lua**: 1734
- **Total Unique Dialogues**: 12
- **Total XP Available**: 6,700+ XP
- **Total Maps Used**: 6
- **Languages**: German (primary), English (translations)

---

## Complete Story Summary

### The Tragic Romance
Amra, a hot-headed but good-hearted warrior, fell in love with Lea, the most beautiful woman in the land. Lea's father, a wealthy man, disapproved of the match and favored a rich magician instead. When Amra was sent away, Lea gave him her most precious possession: the "Pfand der Götter" (Pledge of the Gods), a golden ring gifted to her by the goddess Elen herself.

### The Search
Amra set out to find Lea, accompanied by his warrior brothers: Tyrgar (a fisherman), Craig Un'Shallach, and others including a dark elf. For weeks they wandered the desert, driven by Amra's desperate search. Neither thirst nor undead armies could stop him.

### The Final Battle
A powerful dark magician descended from the sky, demanding the divine ring. Amra fought bravely, defying the magic and walking toward the wizard. A lightning bolt struck, and when Craig awoke, he found Amra dead. The Pledge of the Gods had vanished. Craig buried Amra with his weapons and armor, as befits a warrior.

### The Aftermath
Lea's fate remains mysterious - she may lie buried in Whisper. The player must piece together this tragic story by speaking with:
- **Sunder** (blacksmith in Liannon)
- **Shan Muir** (Lea's brother, healer in Liannon)
- **Tyrgar** (fisherman in Liannon, warrior brother)
- **Sentos** (merchant in Greyfell, tracking the story)
- **Craig Un'Shallach** (final witness, found at Godmark or Ice Gate)

The quest culminates in finding Amra's grave in the desert and dealing with Sentos at a monument, completing the tragic tale of star-crossed lovers separated by fate, magic, and death.

---

*Complete documentation compiled from CFF files and Lua scripts*  
*Generated: 2025-11-02*  
*Includes map locations extracted from file paths*