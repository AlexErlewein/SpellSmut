# Amra and Lea - Complete Quest Documentation

## Quest Tree Overview

```
📜 Quest 379: Amra and Lea (Main Quest)
    ├── 📋 Quest 380: Talk to Sunder in Liannon about Amra's armor
    ├── 📋 Quest 381: Ask Shan Muir about Arma and Lea
    ├── 📋 Quest 382: Examine the events by the house of the Muir family in Liannon
    ├── 📋 Quest 383: A search of the aggressors should deliver further information
    ├── 📋 Quest 384: Confront Sentos in Greyfell
    ├── 📋 Quest 385: Sentos wants to meet with you at the Wildland Pass
    ├── 📋 Quest 386: Interogate Sentos once again
    ├── 📋 Quest 387: Look for Lea's grave in Whisper
    ├── 📋 Quest 388: Bring Lea's possessions to Shan in Liannon
    ├── 📋 Quest 389: Talk to Tyrgar in Liannon
    ├── 📋 Quest 390: Craig Un'Shallach is our last hope
    ├── 📋 Quest 391: Look for Amra's grave in the desert areas
    └── 📋 Quest 393: Renewed troubles with Sentos
```

---

## Data Sources

### Primary Sources
1. **CFF File**: `GameData.cff`
   - Quest names, descriptions, parent-child relationships
   - Quest metadata and structure
   
2. **Lua Scripts**: `OriginalGameFiles/modding/Original Scripts/`
   - Dialogue text and NPC interactions
   - Quest state logic and triggers
   
3. **Quest Rewards**: `script/GdsQuestRewards.lua`
   - XP rewards and progression flags

### Extraction Tools
- **CFF Parser**: `TirganachReloaded.tirganach.GameData`
- **Dialogue Extractor**: `extract_quest_dialogues.py`
- **Complete Extractor**: `extract_cff_quest_data.py`

---

## Quest 379: Amra and Lea (Main Quest)

### CFF Metadata
- **Quest ID**: 379
- **Parent Quest ID**: 0 (Main Quest)
- **Name**: "Amra and Lea"
- **Name String ID**: 13461
- **Description String ID**: 13462
- **Order Index**: 0

### Quest Description
*Note: Description shows "Minimap" placeholder - actual quest description may be stored differently in CFF*

### Subquests (from CFF)
1. Quest 380: Talk to Sunder in Liannon about Amra's armor
2. Quest 381: Ask Shan Muir about Arma and Lea
3. Quest 382: Examine the events by the house of the Muir family in Liannon
4. Quest 383: A search of the aggressors should deliver further information
5. Quest 384: Confront Sentos in Greyfell
6. Quest 385: Sentos wants to meet with you at the Wildland Pass
7. Quest 386: Interogate Sentos once again
8. Quest 387: Look for Lea's grave in Whisper
9. Quest 388: Bring Lea's possessions to Shan in Liannon
10. Quest 389: Talk to Tyrgar in Liannon
11. Quest 390: Craig Un'Shallach is our last hope
12. Quest 391: Look for Amra's grave in the desert areas
13. Quest 393: Renewed troubles with Sentos

### Lua File References
- **File**: `script/P15/n0.lua` (Battle sequences)
- **File**: `script/P63/n2896.lua` (Orthanc dialogue)

### Dialogues
1. **Outcry**: "ffnet das Tor!" - "Open the gate!"
2. **Outcry**: "Lasst die Horde ausrcken! Zerfetzt sie!" - "Let the horde march! Tear them apart!"
3. **Outcry**: "Das ist das Ende Deiner Reise! Du wirst meinen Herrn nie erreichen!" - "This is the end of your journey! You will never reach my master!"
4. **Dialog**: "Was soll es sein? Ein Schwert fr den Bruder? Oder ein Dolch fr die Liebschaft?" - "What will it be? A sword for the brother? Or a dagger for the loved one?"
5. **Dialog**: "Ah, Krieger! Ich hoffe das... Geschft luft zufriedenstellend!" - "Ah, warrior! I hope the... business is running satisfactorily!"

---

## Quest 380: Talk to Sunder in Liannon about Amra's armor

### CFF Metadata
- **Quest ID**: 380
- **Parent Quest ID**: 379
- **Name**: "Talk to Sunder in Liannon about Amra's armor"
- **Name String ID**: 13463
- **Description String ID**: 13464
- **Order Index**: 1

### Quest Objective
Find and speak with Sunder, the blacksmith in Liannon, to learn about Amra's legendary armor.

### Lua File References
- **File**: `script/p1/n1390.lua` (Sunder dialogue)
- **File**: `script/P63/n2896.lua` (Shared merchant dialogue)

### Dialogues
1. **Dialog**: "Hm?" - Initial questioning
2. **Dialog**: "Hmh?!" - Emphatic response

### Extended Story Dialogues
```
"Ich suche nach Amras Rüstung! Orthanc sandte mich zu Euch!"
"I'm searching for Amra's armor! Orthanc sent me to you!"

"Amra? Amra ist fort! Lea ist fort! Nur die Götter wissen, was aus ihnen geworden ist!"
"Amra? Amra is gone! Lea is gone! Only the gods know what became of them!"

"Amra war ein Krieger - ein Hitzkopf! Aber das Herz am rechten Fleck!"
"Amra was a warrior - a hothead! But with his heart in the right place!"

"Und Lea? Lea war das schönste Geschöpf, das die Welt je erblickt hat!"
"And Lea? Lea was the most beautiful creature the world has ever seen!"
```

### Quest Reward
```lua
AmraUndLea1Liannon1 = { XP = {200}}
```

---

## Quest 381: Ask Shan Muir about Arma and Lea

### CFF Metadata
- **Quest ID**: 381
- **Parent Quest ID**: 379
- **Name**: "Ask Shan Muir about Arma and Lea"
- **Name String ID**: 13465
- **Description String ID**: 13466
- **Order Index**: 2

### Quest Objective
Speak with Shan Muir, the healer in Liannon and Lea's brother, to learn the backstory of Amra and Lea's tragic romance.

### Lua File References
- **File**: `script/p1/n1394.lua` (Shan Muir dialogue)

### Dialogues
1. **Dialog**: "Willkommen Fremder! Ich bin Shan Muir, die Heilerin!" - "Welcome stranger! I am Shan Muir, the healer!"
2. **Dialog**: "Ah, Ihr seid zurück!" - "Ah, you're back!"

### Extended Story Dialogues
```
"Ihr müsst wissen, Amra verdingte sich einst als Söldner für meinen Vater!"
"You must know, Amra once served as a mercenary for my father!"

"Zu jener Zeit verfiel ihm meine Schwester Lea und wäre sicherlich seine Frau geworden, 
hätte nicht bereits ein reicher Magier um sie geworben!"
"At that time, my sister Lea fell for him and would surely have become his wife, 
had a rich magician not already courted her!"

"So schickte mein Vater Amra fort! Lea gab ihm als Zeichen ihrer Gunst ihren wertvollsten Besitz, 
das Pfand der Götter! Einen goldenen Ring, den sie einst von der Göttin Elen selbst erhalten hat!"
"So my father sent Amra away! Lea gave him as a sign of her favor her most valuable possession, 
the Pledge of the Gods! A golden ring that she once received from the goddess Elen herself!"

"Tyrgar, der Fischer, war einer der Waffenbrüder Amras!"
"Tyrgar, the fisherman, was one of Amra's warrior brothers!"
```

### Quest Reward
```lua
AmraUndLea1Liannon2 = { XP = {400}}
```

---

## Quest 382: Examine the events by the house of the Muir family in Liannon

### CFF Metadata
- **Quest ID**: 382
- **Parent Quest ID**: 379
- **Name**: "Examine the events by the house of the Muir family in Liannon"
- **Name String ID**: 13467
- **Description String ID**: 13468
- **Order Index**: 3

### Quest Objective
Investigate the Muir family house in Liannon to uncover clues about what happened to Amra and Lea.

### Lua File References
- **File**: `script/p1/n1394.lua` (Shan's house investigation)

### Dialogues
1. **Dialog**: "Was fehlt ihm?" - "What's wrong with him?"

### Quest Reward
```lua
AmraUndLea2Liannon1 = { XP = {500}}
```

---

## Quest 383: A search of the aggressors should deliver further information

### CFF Metadata
- **Quest ID**: 383
- **Parent Quest ID**: 379
- **Name**: "A search of the aggressors should deliver further information"
- **Name String ID**: 13469
- **Description String ID**: 13470
- **Order Index**: 4

### Quest Objective
Search for and confront the aggressors who attacked the Muir family house.

### Lua File References
- **File**: `script/p1/n1396.lua` (Tyrgar Brannon dialogue)

### Dialogues
1. **Dialog**: "Welch eigentümlicher Besuch! Seid gegrüßt! Man nennt mich Tyrgar Brannon!" - "What a peculiar visit! Be greeted! They call me Tyrgar Brannon!"
2. **Dialog**: "Willkommen zurück!" - "Welcome back!"

### Quest Reward
```lua
AmraUndLea2Liannon2 = { XP = {300}}
```

---

## Quest 384: Confront Sentos in Greyfell

### CFF Metadata
- **Quest ID**: 384
- **Parent Quest ID**: 379
- **Name**: "Confront Sentos in Greyfell"
- **Name String ID**: 13471
- **Description String ID**: 13472
- **Order Index**: 5

### Quest Objective
Travel to Greyfell and confront Sentos, the merchant who has been tracking Amra's trail.

### Lua File References
- **File**: `script/P63/n2897.lua` (Sentos dialogue)

### Extended Story Dialogues
```
"Ihr sucht nach der Rüstung Amras, nicht wahr?"
"You're searching for Amra's armor, aren't you?"

"Schön! Lasst uns reden... aber nicht hier! Die Stadt hat zu viele Ohren! 
Trefft mich am Wildland Pass!"
"Good! Let's talk... but not here! The city has too many ears! 
Meet me at Wildland Pass!"
```

### Quest Reward
```lua
AmraUndLea3Sentos = { XP = {500}}
```

---

## Quest 385: Sentos wants to meet with you at the Wildland Pass

### CFF Metadata
- **Quest ID**: 385
- **Parent Quest ID**: 379
- **Name**: "Sentos wants to meet with you at the Wildland Pass"
- **Name String ID**: 13473
- **Description String ID**: 13474
- **Order Index**: 6

### Quest Objective
Travel to Wildland Pass to meet Sentos and learn crucial information about Amra's fate.

### Lua File References
- **File**: `script/P6/n2898.lua` (Sentos at Wildland Pass)

### Extended Story Dialogues
```
"Ihr seid doch auf der Suche nach Lea und Amra, nicht wahr?"
"You're searching for Lea and Amra, aren't you?"

"Ich weiß nur... dass es ein Grab gibt... eine Grabstätte in Wisper... 
man sagt, Lea liege dort! Der Schlüssel zu Amras Rüstung befindet sich in dieser Grabstätte!"
"I only know... that there is a grave... a tomb in Wisper... 
they say Lea lies there! The key to Amra's armor is located in this tomb!"
```

### Quest Reward
```lua
AmraUndLea2Sentos = { XP = {800}}
```

---

## Quest 386: Interogate Sentos once again

### CFF Metadata
- **Quest ID**: 386
- **Parent Quest ID**: 379
- **Name**: "Interogate Sentos once again"
- **Name String ID**: 13475
- **Description String ID**: 13476
- **Order Index**: 7

### Quest Objective
Question Sentos further to extract more details about the quest.

---

## Quest 387: Look for Lea's grave in Whisper

### CFF Metadata
- **Quest ID**: 387
- **Parent Quest ID**: 379
- **Name**: "Look for Lea's grave in Whisper"
- **Name String ID**: 13477
- **Description String ID**: 13478
- **Order Index**: 8

### Quest Objective
Travel to Whisper and locate Lea's grave to find the key to Amra's armor.

---

## Quest 388: Bring Lea's possessions to Shan in Liannon

### CFF Metadata
- **Quest ID**: 388
- **Parent Quest ID**: 379
- **Name**: "Bring Lea's possessions to Shan in Liannon"
- **Name String ID**: 13479
- **Description String ID**: 13480
- **Order Index**: 9

### Quest Objective
Return Lea's belongings to her brother Shan in Liannon.

---

## Quest 389: Talk to Tyrgar in Liannon

### CFF Metadata
- **Quest ID**: 389
- **Parent Quest ID**: 379
- **Name**: "Talk to Tyrgar in Liannon"
- **Name String ID**: 13481
- **Description String ID**: 13482
- **Order Index**: 10

### Quest Objective
Speak with Tyrgar, Amra's warrior brother and fisherman, to learn more about Amra's final journey.

### Extended Story Dialogues
```
"Was ist aus Amra geworden? Hat er Lea je gefunden?"
"What became of Amra? Did he ever find Lea?"

"Wenn einer weiß, was aus Amra geworden ist, dann er!"
"If anyone knows what became of Amra, then he does!"
```

---

## Quest 390: Craig Un'Shallach is our last hope

### CFF Metadata
- **Quest ID**: 390
- **Parent Quest ID**: 379
- **Name**: "Craig Un'Shallach is our last hope"
- **Name String ID**: 13483
- **Description String ID**: 13484
- **Order Index**: 11

### Quest Objective
Find Craig Un'Shallach, the last surviving member of Amra's warrior brotherhood, who witnessed Amra's final battle.

### Lua File References
- **File**: `script/P25/n2910.lua` (Craig at Godmark)
- **File**: `script/P7/n4010.lua` (Craig at Ice Gate)

### Dialogues
1. **Dialog**: "Ein Runenkrieger... welch Ironie des Schicksals!" - "A Rune warrior... what irony of fate!"
2. **Dialog**: "Runenkrieger?" - "Rune warrior?"
3. **Dialog**: "Ihr müsst weiter, ins Nachtflüstertal!" - "You must continue, to the Night Whisper Valley!"
4. **Dialog**: "Was gibt es noch zu sagen?" - "What is there left to say?"

### Extended Story Dialogues
```
"Wochenlang irrten wir in der Wüstenei umher! Amra war wie rasend! 
Weder Durst noch die Heere der Untoten konnten ihn aufhalten!"
"For weeks we wandered through the desert! Amra was like a madman! 
Neither thirst nor the armies of the undead could stop him!"

"Ja! Ein Magier mit dunkler Kapuze, und von unglaublicher Macht! 
Er schwebte aus dem Himmel herab... fegte uns beiseite wie Strohhalme im Wind!"
"Yes! A magician with a dark hood, and of incredible power! 
He floated down from the sky... swept us aside like straws in the wind!"

"Als ich erwachte, fand ich Amra tot neben mir! Das Pfand der Götter war verschwunden. 
Ich begrub seinen Leichnam an jenem Ort! Mitsamt seinen Waffen und seiner Rüstung!"
"When I awoke, I found Amra dead beside me! The Pledge of the Gods had disappeared. 
I buried his body at that place! Along with his weapons and his armor!"
```

### Quest Reward
```lua
AmraUndLea4 = { XP = {1200}}
```

---

## Quest 391: Look for Amra's grave in the desert areas

### CFF Metadata
- **Quest ID**: 391
- **Parent Quest ID**: 379
- **Name**: "Look for Amra's grave in the desert areas"
- **Name String ID**: 13485
- **Description String ID**: 13486
- **Order Index**: 12

### Quest Objective
Travel to the desert and locate Amra's final resting place where Craig buried him with his armor.

### Lua File References
- **File**: `script/P15/n2911.lua` (Amra's gravestone)
- **File**: `script/P15/n0.lua` (Battle area)

### Dialogues
1. **Dialog**: "(Hier fiel Amra im ehrenvollen Kampf)" - "(Here Amra fell in honorable combat)"
2. **Dialog**: "(Ein verwitterter Grabstein)" - "(A weathered tombstone)"
3. **Outcry**: "ffnet das Tor!" - "Open the gate!"
4. **Outcry**: "Lasst die Horde ausrcken! Zerfetzt sie!" - "Let the horde march! Tear them apart!"
5. **Outcry**: "Das ist das Ende Deiner Reise!" - "This is the end of your journey!"

### Quest Reward
```lua
AmraLeaGrab = { XP = {800}}
AmraUndLea5 = { XP = {1200}}
```

---

## Quest 393: Renewed troubles with Sentos

### CFF Metadata
- **Quest ID**: 393
- **Parent Quest ID**: 379
- **Name**: "Renewed troubles with Sentos"
- **Name String ID**: 13487
- **Description String ID**: 13488
- **Order Index**: 13

### Quest Objective
Deal with Sentos one final time regarding the monument and complete the quest cycle.

### Lua File References
- **File**: `script/P6/n2898.lua` (Sentos final dialogue)
- **File**: `script/P6/n0.lua` (Monument area)

### Dialogues
1. **Dialog**: "Ah, tretet näher, Freund! Schön, dass Ihr es geschafft habt!" - "Ah, come closer, friend! Good that you made it!"
2. **Dialog**: "Was genau tun wir hier?" - "What exactly are we doing here?"
3. **Outcry**: "Los Männer! Zum Monument!" - "Go men! To the monument!"
4. **Outcry**: "Steht nicht so rum! Tötet irgendwas!" - "Don't just stand around! Kill something!"
5. **Outcry**: "Nein! Die Götter mögen Euch verfluchen, Runensklave! Aargh!" - "No! May the gods curse you, Rune slave! Aargh!"

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
- **Shan Muir** (Lea's brother, healer)
- **Tyrgar** (fisherman, warrior brother)
- **Sentos** (merchant tracking the story)
- **Craig Un'Shallach** (final witness)

The quest culminates in finding Amra's grave in the desert and dealing with Sentos at a monument, completing the tragic tale of star-crossed lovers separated by fate, magic, and death.

---

## Total Quest Statistics

- **Main Quest**: 1 (Quest 379)
- **Subquests**: 13 (Quests 380-391, 393)
- **Total XP Rewards**: 6,700+ XP
- **Lua Files Referenced**: 10+ files
- **Unique Dialogues**: 50+ (excluding duplicates)
- **Languages**: German (primary), English (translations provided)
- **Key NPCs**: 5 (Sunder, Shan, Tyrgar, Sentos, Craig)
- **Locations**: Liannon, Greyfell, Wildland Pass, Whisper, Desert, Godmark, Ice Gate

---

*Complete documentation compiled from CFF files and Lua scripts*  
*Generated: 2025-11-02*
