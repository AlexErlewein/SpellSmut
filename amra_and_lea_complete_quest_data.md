# Amra and Lea Quest (ID 379) - Complete Data Collection

## Overview
This document contains all available data for the "Amra and Lea" quest (Quest ID 379) and its related subquests, extracted from the SpellForce game files.

---

## 1. Quest Identification

### Quest ID 379 - Main Quest
- **Name**: Amra and Lea (Amra und Lea)
- **Type**: Main Storyline Quest
- **Language**: German
- **Status**: Multi-part quest series

### Related Quest ID 380
- **Type**: Subquest or related content
- **Connection**: Shares dialogue files with main quest

---

## 2. File Locations and References

### 2.1 Lua Script Files Containing Quest Data

#### Primary Quest Files:
- `script/P63/n0.lua` - Main quest header and initialization
- `script/P63/n2896.lua` - Core dialogue content
- `script/P63/n2897.lua` - Additional dialogue content
- `script/P15/n0.lua` - Quest spawn conditions
- `script/P15/n2911.lua` - Amra's gravestone
- `script/P15/n2912.lua` - Amra spawn trigger

#### Supporting Character Files:
- `script/p1/n1390.lua` - Sunder (blacksmith) dialogues
- `script/p1/n1394.lua` - Shan (Lea's brother) dialogues  
- `script/p1/n1396.lua` - Tyrgar (fisherman) dialogues
- `script/P25/n2910.lua` - Craig (warrior brother) dialogues
- `script/P6/n2898.lua` - Sentos (merchant) dialogues
- `script/P7/n4010.lua` - Additional Craig dialogues

#### Quest Reward System:
- `script/GdsQuestRewards.lua` - XP rewards and quest flags

#### Unit Data:
- `script/sql_unit.lua` - Character definitions (Amra ID: 1114)

### 2.2 Quest Flags and Progression

```
AmraUndLea1Liannon1    = { XP = {200}}  -- Sunder's first dialogue
AmraUndLea1Liannon2    = { XP = {400}}  -- Shan's backstory
AmraUndLea2Liannon1    = { XP = {500}}  -- Additional Shan content
AmraUndLea2Liannon2    = { XP = {300}}  -- Tyrgar's information
AmraUndLea2Sentos      = { XP = {800}}  -- Sentos meeting
AmraUndLea3Sentos      = { XP = {500}}  -- Sentos follow-up
AmraUndLea4            = { XP = {1200}} -- Craig's desert story
AmraUndLea5            = { XP = {1200}} -- Final quest part
AmraLeaGrab            = { XP = {800}}  -- Grave discovery
```

---

## 3. Complete Dialogue Collection

### 3.1 Quest ID 379 Dialogues

#### From script/P15/n0.lua:
1. **"ffnet das Tor!"**
   - Translation: "Open the gate!"
   - Context: Battle cry or command

2. **"Lasst die Horde ausrcken! Zerfetzt sie!"**
   - Translation: "Let the horde march! Tear them apart!"
   - Context: Combat command

3. **"Das ist das Ende Deiner Reise! Du wirst meinen Herrn nie erreichen!"**
   - Translation: "This is the end of your journey! You will never reach my master!"
   - Context: Enemy confrontation

#### From script/P63/n2896.lua:
4. **"Was soll es sein? Ein Schwert fr den Bruder? Oder ein Dolch fr die Liebschaft?"**
   - Translation: "What will it be? A sword for the brother? Or a dagger for the loved one?"
   - Context: Merchant or craftsman offering choices

5. **"Ah, Krieger! Ich hoffe das... Geschft luft zufriedenstellend!"**
   - Translation: "Ah, warrior! I hope the... business is running satisfactorily!"
   - Context: Merchant greeting (repeated multiple times in game mechanics)

### 3.2 Quest ID 380 Dialogues

#### From script/p1/n1390.lua:
1. **"Hm?"**
   - Context: Questioning sound, likely from Sunder

2. **"Hmh?!"**
   - Context: More emphatic questioning

#### From script/P63/n2896.lua:
3. **"Was soll es sein? Ein Schwert fr den Bruder? Oder ein Dolch fr die Liebschaft?"**
   - Same as Quest 379, shared dialogue

4. **"Ah, Krieger! Ich hoffe das... Geschft luft zufriedenstellend!"**
   - Same as Quest 379, shared dialogue

---

## 4. Extended Story Dialogues (From Related Files)

### 4.1 Orthanc's Dialogue (script/P63/n2896.lua)
```
"Amra hat sie getragen, als er auszog, um Lea zu suchen! Was aus ihm geworden ist? Ich wei� es nicht... er ist nie von seiner Reise zur�ckgekehrt!"
```
**Translation**: "Amra wore it when he set out to search for Lea! What became of him? I don't know... he never returned from his journey!"

```
"Mein alter Lehrling, Sunder, hat eine Weile nach Amra gesucht! Aber ohne Erfolg. Er hat jetzt eine Schmiede in Liannon! Falls Ihr ihn trefft, gr�t ihn von mir!"
```
**Translation**: "My old apprentice, Sunder, searched for Amra for a while! But without success. He now has a smithy in Liannon! If you meet him, greet him from me!"

### 4.2 Sunder's Dialogue (script/p1/n1390.lua)
```
"Amra? Amra ist fort! Lea ist fort! Nur die G�tter wissen, was aus ihnen geworden ist!"
```
**Translation**: "Amra? Amra is gone! Lea is gone! Only the gods know what became of them!"

```
"Amra war ein Krieger - ein Hitzkopf! Aber das Herz am rechten Fleck! Und Lea? Lea war das sch�nste Gesch�pf, das die Welt je erblickt hat!"
```
**Translation**: "Amra was a warrior - a hothead! But with his heart in the right place! And Lea? Lea was the most beautiful creature the world has ever seen!"

```
"Die beiden h�tten ein h�bsches Paar abgegeben. Doch dann ging Lea fort, mit so einem vermummten Kerl! Und Amra war nicht mehr derselbe! Tobte und schrie den ganzen Tag!"
```
**Translation**: "The two would have made a lovely couple. But then Lea left, with some masked fellow! And Amra was never the same! Raged and screamed all day!"

```
"Ich suche nach Amras R�stung! Orthanc sandte mich zu Euch!"
```
**Translation**: "I'm searching for Amra's armor! Orthanc sent me to you!"

### 4.3 Shan's Dialogue (script/p1/n1394.lua)
```
"Ihr m�sst wissen, Amra verdingte sich einst als S�ldner f�r meinen Vater! Zu jener Zeit verfiel ihm meine Schwester Lea und w�re sicherlich seine Frau geworden, h�tte nicht bereits ein reicher Magier um sie geworben!"
```
**Translation**: "You must know, Amra once served as a mercenary for my father! At that time, my sister Lea fell for him and would surely have become his wife, had a rich magician not already courted her!"

```
"So schickte mein Vater Amra fort! Lea gab ihm als Zeichen ihrer Gunst ihren wertvollsten Besitz, das Pfand der G�tter! Einen goldenen Ring, den sie einst von der G�ttin Elen selbst erhalten hat!"
```
**Translation**: "So my father sent Amra away! Lea gave him as a sign of her favor her most valuable possession, the Pledge of the Gods! A golden ring that she once received from the goddess Elen herself!"

```
"Ich hoffe nur, Amra ist weit weg und reitet wie der Wind, auf dass mein Gemahl ihn nie finden m�ge, denn sein Zorn ist grausam!"
```
**Translation**: "I only hope Amra is far away and rides like the wind, so that my husband may never find him, for his anger is cruel!"

```
"Tyrgar, der Fischer, war einer der Waffenbr�der Amras! Sie waren wie Pech und Schwefel! Krieger und S�ldner, sogar ein Dunkelelf war unter ihnen!"
```
**Translation**: "Tyrgar, the fisherman, was one of Amra's warrior brothers! They were like pitch and sulfur! Warriors and mercenaries, even a dark elf was among them!"

```
"Befragt Tyrgar, wenn ihr mehr �ber Amra wissen wollt! Ich werde mich dem Andenken meiner Schwester widmen!"
```
**Translation**: "Ask Tyrgar if you want to know more about Amra! I will devote myself to the memory of my sister!"

### 4.4 Tyrgar's Dialogue (script/p1/n1396.lua)
```
"Was ist aus Amra geworden? Hat er Lea je gefunden?"
```
**Translation**: "What became of Amra? Did he ever find Lea?"

```
"Wenn einer wei�, was aus Amra geworden ist, dann er! Viel Gl�ck bei Eurer Suche! Ich muss mich jetzt wieder um meine Netze k�mmern!"
```
**Translation**: "If anyone knows what became of Amra, then he does! Good luck with your search! I must now tend to my nets again!"

### 4.5 Craig's Dialogue (script/P25/n2910.lua)
```
"Wochenlang irrten wir in der W�stenei umher! Amra war wie rasend! Weder Durst noch die Heere der Untoten konnten ihn aufhalten! Doch wir fanden nur Staub und Tod!"
```
**Translation**: "For weeks we wandered through the desert! Amra was like a madman! Neither thirst nor the armies of the undead could stop him! But we found only dust and death!"

```
"Ja! Ein Magier mit dunkler Kapuze, und von unglaublicher Macht! Er schwebte aus dem Himmel herab... fegte uns beiseite wie Strohhalme im Wind! Geifernd verlangte er von Amra das Pfand der G�tter, jenen unseligen Ring!"
```
**Translation**: "Yes! A magician with a dark hood, and of incredible power! He floated down from the sky... swept us aside like straws in the wind! Foaming, he demanded from Amra the Pledge of the Gods, that unholy ring!"

```
"Ich sah noch, wie Amra sich aufrichtete! Wie er der Magie trotzend auf den Zauberer zuschritt... dann l�schte ein Blitz mein Bewusstsein..."
```
**Translation**: "I still saw how Amra rose up! How he defied the magic and walked toward the wizard... then a lightning bolt extinguished my consciousness..."

```
"Als ich erwachte, fand ich Amra tot neben mir! Das Pfand der G�tter war verschwunden. Ich begrub seinen Leichnam an jenem Ort! Mitsamt seinen Waffen und seiner R�stung, wie es einem Krieger geb�hrt!"
```
**Translation**: "When I awoke, I found Amra dead beside me! The Pledge of the Gods had disappeared. I buried his body at that place! Along with his weapons and his armor, as befits a warrior!"

### 4.6 Sentos' Dialogue (script/P6/n2898.lua)
```
"Ihr seid doch auf der Suche nach Lea und Amra, nicht wahr?"
```
**Translation**: "You're searching for Lea and Amra, aren't you?"

```
"Ich wei� nur... dass es ein Grab gibt... eine Grabst�tte in Wisper... man sagt, Lea liege dort! Der Schl�ssel zu Amras R�stung befindet sich in dieser Grabst�tte!"
```
**Translation**: "I only know... that there is a grave... a tomb in Wisper... they say Lea lies there! The key to Amra's armor is located in this tomb!"

```
"Sch�n! Lasst uns reden... aber nicht hier! Die Stadt hat zu viele Ohren! Trefft mich am Wildland Pass! Ich habe Amras Spur bis dorthin verfolgt!"
```
**Translation**: "Good! Let's talk... but not here! The city has too many ears! Meet me at Wildland Pass! I have tracked Amra's trail to there!"

### 4.7 Amra's Gravestone (script/P15/n2911.lua)
```
"(Hier fiel Amra im ehrenvollen Kampf)"
```
**Translation**: "(Here Amra fell in honorable combat)"

---

## 5. Quest Progression and Game Mechanics

### 5.1 Global Flags Used
```
AmraSpawn
SpawnAmra
AmraLeaGrab
LeaFollowP110
LeaFollowP111
```

### 5.2 NPC References
- **Amra**: Unit ID 1114
- **Amras Wchter**: Unit ID 1453 (Amra's Guardian)

### 5.3 Map Locations
- **P1**: Liannon (city area)
- **P6**: Wildland Pass area
- **P15**: Desert/burial area
- **P25**: Mountain area
- **P63**: General quest hub
- **P7**: Ice gate area

---

## 6. Story Analysis

### 6.1 Character Relationships
- **Amra & Lea**: Star-crossed lovers
- **Shan**: Lea's protective brother
- **Orthanc**: Master smith, quest giver
- **Sunder**: Orthanc's apprentice, blacksmith in Liannon
- **Tyrgar**: Amra's warrior brother, now a fisherman
- **Craig**: Amra's warrior brother, survivor of the final battle
- **Sentos**: Merchant who tracked Amra

### 6.2 Key Plot Elements
1. **The Ring**: "Pfand der Götter" - divine artifact from goddess Elen
2. **The Conflict**: Love vs. arranged marriage, mortal vs. magical power
3. **The Tragedy**: Amra's death protecting the ring
4. **The Legacy**: Search for Amra's armor and uncovering the truth

### 6.3 Themes
- Tragic romance
- Warrior brotherhood
- Divine intervention
- Sacrifice and honor
- The corruption of power

---

## 7. Technical Implementation Notes

### 7.1 Quest Structure
- Multi-part quest with 8+ stages
- Non-linear progression through different NPCs
- Cross-map quest mechanics
- Reward flag system for tracking progress

### 7.2 Dialogue System
- Heavy use of repeated dialogue for game mechanics
- Conditional dialogue based on quest flags
- Multiple language support (German primary)

### 7.3 File Organization
- Quest data distributed across multiple map files
- Centralized reward system in GdsQuestRewards.lua
- Character-specific dialogue in separate files

---

## 8. Summary

The "Amra and Lea" quest is one of the most comprehensive storylines in SpellForce, featuring:
- **9 unique dialogues** directly extracted
- **20+ extended dialogues** from supporting characters
- **8 quest stages** with XP rewards from 200-1200
- **6 major locations** across the game world
- **7 key NPCs** each with unique story contributions
- **Tragic romance** storyline with warrior themes

This quest represents a significant narrative arc in the game, combining elements of romance, tragedy, warrior brotherhood, and divine intervention into a cohesive multi-part storyline.

---

*Data extracted from SpellForce game files using custom dialogue extraction tools*
