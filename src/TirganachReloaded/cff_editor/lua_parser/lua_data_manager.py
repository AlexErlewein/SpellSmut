"""
Lua Data Manager
Manages loading, caching, and accessing Lua quest script data
Similar to CFF caching but for Lua script files
"""

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from .quest_lua_parser import (
    LuaQuestParser,
    QuestData,
    QuestDialogue,
    QuestObjective,
    QuestRequirement,
    QuestReward,
)


class LuaDataManager:
    """Manages Lua quest data with caching"""

    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            cache_dir = Path.home() / ".spellforce_editor" / "lua_cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Note: Logging is now handled by the global logging system

        self.db_path = self.cache_dir / "lua_quest_cache.db"
        self.parser = LuaQuestParser()

        # In-memory cache
        self.quest_cache: Dict[int, QuestData] = {}
        self.cache_loaded = False

        self._init_database()



    def _init_database(self):
        """Initialize SQLite database for caching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Quests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lua_quests (
                quest_id INTEGER PRIMARY KEY,
                quest_name TEXT,
                description TEXT,
                platform TEXT,
                npc_id INTEGER,
                author TEXT,
                notes TEXT,
                file_path TEXT,
                last_modified REAL
            )
        """)

        # Objectives table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_id INTEGER,
                description TEXT,
                objective_type TEXT,
                target TEXT,
                count INTEGER,
                lua_condition TEXT,
                FOREIGN KEY (quest_id) REFERENCES lua_quests (quest_id)
            )
        """)

        # Requirements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_id INTEGER,
                description TEXT,
                requirement_type TEXT,
                value TEXT,
                lua_condition TEXT,
                FOREIGN KEY (quest_id) REFERENCES lua_quests (quest_id)
            )
        """)

        # Rewards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_rewards (
                quest_id INTEGER PRIMARY KEY,
                xp INTEGER,
                gold INTEGER,
                silver INTEGER,
                copper INTEGER,
                items TEXT,
                flags TEXT,
                FOREIGN KEY (quest_id) REFERENCES lua_quests (quest_id)
            )
        """)

        # Dialogues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_dialogues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_id INTEGER,
                dialogue_id TEXT,
                speaker TEXT,
                text TEXT,
                is_player_choice INTEGER,
                FOREIGN KEY (quest_id) REFERENCES lua_quests (quest_id)
            )
        """)

        # Metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
        conn.close()

    def parse_lua_directory(self, lua_dir: Path, force_refresh: bool = False) -> int:
        """
        Parse all Lua quest files in a directory

        Args:
            lua_dir: Directory containing Lua quest scripts
            force_refresh: If True, reparse even if cached

        Returns:
            Number of quests parsed
        """
        lua_dir = Path(lua_dir)
        if not lua_dir.exists():
            logger.warning(f"Lua directory not found: {lua_dir}")
            return 0

        # Find all .lua files
        lua_files = list(lua_dir.glob("**/*.lua"))
        logger.info(f"Found {len(lua_files)} Lua files in {lua_dir}")

        quests_parsed = 0

        for lua_file in lua_files:
            try:
                # Check if file needs reparsing
                if not force_refresh and self._is_file_cached(lua_file):
                    continue

                # Skip very large files (likely not quest files)
                file_size = lua_file.stat().st_size
                if file_size > 1 * 1024 * 1024:  # 1MB
                    logger.debug(
                        f"Skipping large file: {lua_file.name} ({file_size / 1024:.0f}KB)"
                    )
                    continue

                # Parse the file with timeout protection
                logger.debug(f"Parsing: {lua_file.name}")

                try:
                    quests = self.parser.parse_file(str(lua_file))
                except Exception as parse_error:
                    logger.debug(f"Parse error in {lua_file.name}: {parse_error}")
                    continue

                # Detect platform from file path (e.g., P1, P2, P3)
                platform = self._detect_platform_from_path(lua_file)

                if quests:
                    for quest in quests:
                        # Set platform if detected and not already set
                        if platform and (not quest.platform or quest.platform == "P7"):
                            quest.platform = platform
                        self._store_quest(quest, lua_file)
                        quests_parsed += 1
                        logger.debug(
                            f"Found quest {quest.quest_id}: {quest.quest_name}"
                        )

            except Exception as e:
                logger.error(f"Error processing {lua_file.name}: {e}")
                continue

        # Update metadata
        self._update_metadata("last_parse_time", str(Path(lua_dir).stat().st_mtime))
        self._update_metadata("lua_directory", str(lua_dir))

        logger.info(f"Parsed {quests_parsed} quests from Lua files")

        # Parse GdsQuestRewards.lua if it exists
        # Try multiple locations
        rewards_file = None

        # Location 1: In the selected directory
        if (lua_dir / "GdsQuestRewards.lua").exists():
            rewards_file = lua_dir / "GdsQuestRewards.lua"
        # Location 2: Search in subdirectories
        elif list(lua_dir.glob("**/GdsQuestRewards.lua")):
            rewards_file = list(lua_dir.glob("**/GdsQuestRewards.lua"))[0]

        if rewards_file:
            logger.debug(f"Found GdsQuestRewards.lua at: {rewards_file}")
            logger.debug("Parsing GdsQuestRewards.lua for reward data...")
            self._parse_rewards_file(rewards_file)
        else:
            logger.warning(
                "GdsQuestRewards.lua not found - rewards will not be available"
            )
            logger.debug(f"Searched in: {lua_dir}")

        # Preload cache into memory for fast access
        self.preload_cache()

        return quests_parsed

    def _parse_rewards_file(self, rewards_file: Path):
        """Parse GdsQuestRewards.lua file to extract reward data"""
        try:
            logger.debug(f"Reading rewards file: {rewards_file}")
            # Try multiple encodings
            encodings = ["utf-8", "windows-1252", "latin-1"]
            content = None

            for encoding in encodings:
                try:
                    with open(rewards_file, "r", encoding=encoding) as f:
                        content = f.read()
                    logger.debug(
                        f"Successfully read file with encoding: {encoding}"
                    )
                    break
                except (UnicodeDecodeError, LookupError):
                    continue

            if not content:
                with open(rewards_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                logger.debug("Used UTF-8 with errors ignored")

            logger.debug(f"File content length: {len(content)} characters")

            # Parse each platform's rewards (P1, P2, P63, etc.)
            platform_pattern = r"QuestRewardsP(\d+)\s*=\s*\{(.*?)(?=\nQuestRewardsP|\Z)"

            logger.debug("Searching for platform patterns...")
            platforms_found = 0
            # Accumulate a mapping of (platform, reward_name) -> reward tuple for deterministic joining later
            reward_map = {}

            for platform_match in re.finditer(platform_pattern, content, re.DOTALL):
                platforms_found += 1
                platform = f"P{platform_match.group(1)}"
                rewards_section = platform_match.group(2)
                logger.debug(
                    f"Parsing rewards for platform {platform}... (section length: {len(rewards_section)})"
                )

                # Parse individual quest rewards
                # Format: QuestName = { XP = {25}, Items = {626}, Money = {Gold = 1} }
                quest_pattern = r"(\w+)\s*=\s*{([^}]+(?:{[^}]*}[^}]*)*?)}"

                quest_count = 0
                matches_list = list(re.finditer(quest_pattern, rewards_section))
                logger.debug(
                    f"Found {len(matches_list)} quest patterns in {platform}"
                )

                for quest_match in matches_list:
                    quest_count += 1
                    quest_name = quest_match.group(1)
                    reward_data = quest_match.group(2)

                    if quest_count <= 3:  # Show first 3 for debugging
                        logger.debug(
                            f"Quest name: '{quest_name}', reward data: '{reward_data[:50]}...'"
                        )
                    # Extract reward values
                    xp = 0
                    gold = 0
                    silver = 0
                    copper = 0
                    items = []

                    # XP: can be {25} or just 25
                    xp_match = re.search(r"XP\s*=\s*{?\s*(\d+)\s*}?", reward_data)
                    if xp_match:
                        xp = int(xp_match.group(1))

                    # Money: {Gold = 1, Silver = 2, Copper = 3}
                    gold_match = re.search(r"Gold\s*=\s*(\d+)", reward_data)
                    if gold_match:
                        gold = int(gold_match.group(1))

                    silver_match = re.search(r"Silver\s*=\s*(\d+)", reward_data)
                    if silver_match:
                        silver = int(silver_match.group(1))

                    copper_match = re.search(r"Copper\s*=\s*(\d+)", reward_data)
                    if copper_match:
                        copper = int(copper_match.group(1))

                    # Items: {626, 707} or {626}
                    items_match = re.search(r"Items\s*=\s*{([^}]+)}", reward_data)
                    if items_match:
                        items_str = items_match.group(1)
                        items = [
                            int(x.strip())
                            for x in items_str.split(",")
                            if x.strip().isdigit()
                        ]

                    # Store in a mapping (we'll match to quest IDs later)
                    if quest_count <= 3:  # Show first 3 for debugging
                        logger.debug(
                            f"Storing: {quest_name} - XP:{xp}, Gold:{gold}, Items:{items}"
                        )

                    # Store via heuristic match (kept for backward compatibility)
                    self._store_reward_by_name(
                        quest_name, platform, xp, gold, silver, copper, items
                    )

                    # Also record for deterministic flag-based join
                    reward_map[(platform, quest_name)] = {
                        "xp": xp,
                        "gold": gold,
                        "silver": silver,
                        "copper": copper,
                        "items": items,
                    }

                lua_logger.debug(f"Found {quest_count} quest rewards for {platform}")

            logger.info(
                f"Parsed rewards from GdsQuestRewards.lua - {platforms_found} platforms found"
            )

            # Deterministic join pass: use quest reward flags to match reward names on the same platform
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # For each quest, get platform and its reward flags
                cursor.execute(
                    """
                    SELECT q.quest_id, q.platform, r.flags
                    FROM lua_quests q
                    LEFT JOIN quest_rewards r ON r.quest_id = q.quest_id
                    """
                )
                rows = cursor.fetchall()
                updated = 0
                for quest_id, platform, flags_json in rows:
                    if not flags_json:
                        continue
                    try:
                        flags = json.loads(flags_json)
                    except Exception:
                        continue
                    if not isinstance(flags, list):
                        continue

                    # Try each flag against the reward map
                    matched = None
                    for flag in flags:
                        key = (platform, flag)
                        if key in reward_map:
                            matched = reward_map[key]
                            break

                    if matched:
                        cursor.execute(
                            """
                            UPDATE quest_rewards
                            SET xp = ?, gold = ?, silver = ?, copper = ?, items = ?
                            WHERE quest_id = ?
                            """,
                            (
                                matched["xp"],
                                matched["gold"],
                                matched["silver"],
                                matched["copper"],
                                json.dumps(matched["items"]),
                                quest_id,
                            ),
                        )
                        updated += 1

                conn.commit()
                lua_logger.info(f"Reward join via flags updated {updated} quests")
                conn.close()
            except Exception as join_err:
                lua_logger.debug(f"Reward join via flags skipped: {join_err}")

        except Exception as e:
            logger.error(f"Error parsing GdsQuestRewards.lua: {e}")

    def _store_reward_by_name(
        self,
        quest_name: str,
        platform: str,
        xp: int,
        gold: int,
        silver: int,
        copper: int,
        items: list,
    ):
        """Store reward data by quest name (will need to match to quest ID later)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if there are any quests for this platform first
        cursor.execute(
            "SELECT COUNT(*) FROM lua_quests WHERE platform = ?", (platform,)
        )
        quest_count = cursor.fetchone()[0]
        if quest_count == 0:
            logger.debug(
                f"WARNING: No quests found in database for platform {platform}"
            )
            conn.close()
            return

        # German quest names are compound words - break them up for better matching
        # e.g., "DariusDerKarthograph" → ["Darius", "Der", "Karthograph"]
        # Split on capital letters and numbers
        name_parts = re.findall(r"[A-Z][a-z]*|[0-9]+", quest_name)

        # Try multiple matching strategies
        quest_id = None

        # Strategy 1: Exact match on full name
        cursor.execute(
            "SELECT quest_id FROM lua_quests WHERE platform = ? AND (quest_name LIKE ? OR description LIKE ?)",
            (platform, f"%{quest_name}%", f"%{quest_name}%"),
        )
        result = cursor.fetchone()
        if result:
            quest_id = result[0]

        # Strategy 2: Match on name parts (German compound words)
        if not quest_id and len(name_parts) >= 2:
            # Build a query that checks if ALL parts appear in the description
            # This handles German compound words well
            conditions = " AND ".join(["description LIKE ?" for _ in name_parts])
            query = (
                f"SELECT quest_id FROM lua_quests WHERE platform = ? AND ({conditions})"
            )
            params = [platform] + [f"%{part}%" for part in name_parts]

            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                quest_id = result[0]
                logger.debug(
                    f"Matched '{quest_name}' using parts: {name_parts} → Quest {quest_id}"
                )

        # Strategy 3: Try first significant word (often the main keyword)
        if not quest_id and len(name_parts) > 0:
            # Skip common German words
            skip_words = [
                "Der",
                "Die",
                "Das",
                "Ein",
                "Eine",
                "Und",
                "Nach",
                "Vor",
                "Part",
            ]
            significant_parts = [
                p for p in name_parts if p not in skip_words and len(p) > 2
            ]

            if significant_parts:
                first_word = significant_parts[0]
                cursor.execute(
                    "SELECT quest_id FROM lua_quests WHERE platform = ? AND description LIKE ?",
                    (platform, f"%{first_word}%"),
                )
                result = cursor.fetchone()
                if result:
                    quest_id = result[0]
                    logger.debug(
                        f"Matched '{quest_name}' using keyword '{first_word}' → Quest {quest_id}"
                    )

        # Try to match by reward flag first (exact match inside JSON flags)
        if not quest_id:
            try:
                cursor.execute(
                    """
                    SELECT r.quest_id
                    FROM quest_rewards r
                    JOIN lua_quests q ON q.quest_id = r.quest_id
                    WHERE q.platform = ? AND r.flags LIKE ?
                    LIMIT 1
                    """,
                    (platform, f'%"{quest_name}"%'),
                )
                row = cursor.fetchone()
                if row:
                    quest_id = row[0]
            except Exception:
                pass

        # Store the reward if we found a match
        if quest_id:
            # Merge quest_name from GdsQuestRewards.lua into existing flags without overwriting
            try:
                cursor.execute(
                    "SELECT flags FROM quest_rewards WHERE quest_id = ?",
                    (quest_id,),
                )
                existing = cursor.fetchone()
                current_flags = []
                if existing and existing[0]:
                    try:
                        current_flags = json.loads(existing[0])
                        if not isinstance(current_flags, list):
                            current_flags = []
                    except Exception:
                        current_flags = []
                if quest_name and quest_name not in current_flags:
                    current_flags.append(quest_name)
            except Exception:
                current_flags = [quest_name] if quest_name else []

            cursor.execute(
                """
                INSERT OR REPLACE INTO quest_rewards
                (quest_id, xp, gold, silver, copper, items, flags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (quest_id, xp, gold, silver, copper, json.dumps(items), json.dumps(current_flags)),
            )
            conn.commit()
        else:
            # Debug: show what quests ARE available on this platform
            cursor.execute(
                "SELECT quest_id, description FROM lua_quests WHERE platform = ? LIMIT 3",
                (platform,),
            )
            sample_quests = cursor.fetchall()
            logger.debug(
                f"Could not match reward '{quest_name}' on platform {platform}"
            )
            logger.debug(f"Name parts: {name_parts}")
            if sample_quests:
                logger.debug(f"Sample quests on {platform}:")
                for qid, desc in sample_quests:
                    logger.debug(
                        f"Quest {qid}: {desc[:60] if desc else 'No description'}..."
                    )

        conn.close()

    def _detect_platform_from_path(self, lua_file: Path) -> Optional[str]:
        """Detect platform ID from file path (e.g., /script/P1/n0.lua → P1)"""
        # Check parent directories for pattern like P1, P2, P3, etc.
        for part in lua_file.parts:
            if re.match(r"^P\d+$", part):
                return part
        return None

    def _is_file_cached(self, lua_file: Path) -> bool:
        """Check if file is already cached and up-to-date"""
        file_mtime = lua_file.stat().st_mtime

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_modified FROM lua_quests WHERE file_path = ?", (str(lua_file),)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            cached_mtime = result[0]
            return file_mtime <= cached_mtime

        return False

    def _store_quest(self, quest: QuestData, lua_file: Path):
        """Store quest data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        file_mtime = lua_file.stat().st_mtime

        # Store main quest data
        cursor.execute(
            """
            INSERT OR REPLACE INTO lua_quests
            (quest_id, quest_name, description, platform, npc_id, author, notes, file_path, last_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                quest.quest_id,
                quest.quest_name,
                quest.description,
                quest.platform,
                quest.npc_id,
                quest.author,
                quest.notes,
                str(lua_file),
                file_mtime,
            ),
        )

        # Clear old objectives/requirements/dialogues
        cursor.execute(
            "DELETE FROM quest_objectives WHERE quest_id = ?", (quest.quest_id,)
        )
        cursor.execute(
            "DELETE FROM quest_requirements WHERE quest_id = ?", (quest.quest_id,)
        )
        cursor.execute(
            "DELETE FROM quest_dialogues WHERE quest_id = ?", (quest.quest_id,)
        )

        # Store objectives
        for obj in quest.objectives:
            cursor.execute(
                """
                INSERT INTO quest_objectives
                (quest_id, description, objective_type, target, count, lua_condition)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    quest.quest_id,
                    obj.description,
                    obj.objective_type,
                    obj.target,
                    obj.count,
                    obj.lua_condition,
                ),
            )

        # Store requirements
        for req in quest.requirements:
            cursor.execute(
                """
                INSERT INTO quest_requirements
                (quest_id, description, requirement_type, value, lua_condition)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    quest.quest_id,
                    req.description,
                    req.requirement_type,
                    str(req.value) if req.value is not None else None,
                    req.lua_condition,
                ),
            )

        # Store rewards
        items_json = json.dumps(quest.rewards.items)
        flags_json = json.dumps(quest.rewards.flags)

        cursor.execute(
            """
            INSERT OR REPLACE INTO quest_rewards
            (quest_id, xp, gold, silver, copper, items, flags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                quest.quest_id,
                quest.rewards.xp,
                quest.rewards.gold,
                quest.rewards.silver,
                quest.rewards.copper,
                items_json,
                flags_json,
            ),
        )

        # Store dialogues
        for dlg in quest.dialogues:
            cursor.execute(
                """
                INSERT INTO quest_dialogues
                (quest_id, dialogue_id, speaker, text, is_player_choice)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    quest.quest_id,
                    dlg.dialogue_id,
                    dlg.speaker,
                    dlg.text,
                    1 if dlg.is_player_choice else 0,
                ),
            )

        conn.commit()
        conn.close()

    def get_quest_data(self, quest_id: int) -> Optional[QuestData]:
        """Get cached quest data by ID"""
        # Check in-memory cache first
        if quest_id in self.quest_cache:
            return self.quest_cache[quest_id]

        # Load from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get main quest data
        cursor.execute(
            """
            SELECT quest_name, description, platform, npc_id, author, notes
            FROM lua_quests WHERE quest_id = ?
        """,
            (quest_id,),
        )

        result = cursor.fetchone()
        if not result:
            conn.close()
            return None

        quest = QuestData(
            quest_id=quest_id,
            quest_name=result[0],
            description=result[1] or "",
            platform=result[2] or "P7",
            npc_id=result[3],
            author=result[4] or "",
            notes=result[5] or "",
        )

        # Load objectives
        cursor.execute(
            """
            SELECT description, objective_type, target, count, lua_condition
            FROM quest_objectives WHERE quest_id = ?
        """,
            (quest_id,),
        )

        for row in cursor.fetchall():
            quest.objectives.append(
                QuestObjective(
                    description=row[0],
                    objective_type=row[1] or "Unknown",
                    target=row[2],
                    count=row[3] or 1,
                    lua_condition=row[4],
                )
            )

        # Load requirements
        cursor.execute(
            """
            SELECT description, requirement_type, value, lua_condition
            FROM quest_requirements WHERE quest_id = ?
        """,
            (quest_id,),
        )

        for row in cursor.fetchall():
            quest.requirements.append(
                QuestRequirement(
                    description=row[0],
                    requirement_type=row[1] or "Unknown",
                    value=row[2],
                    lua_condition=row[3],
                )
            )

        # Load rewards
        cursor.execute(
            """
            SELECT xp, gold, silver, copper, items, flags
            FROM quest_rewards WHERE quest_id = ?
        """,
            (quest_id,),
        )

        reward_row = cursor.fetchone()
        if reward_row:
            items = json.loads(reward_row[4]) if reward_row[4] else []
            flags = json.loads(reward_row[5]) if reward_row[5] else []

            quest.rewards = QuestReward(
                xp=reward_row[0] or 0,
                gold=reward_row[1] or 0,
                silver=reward_row[2] or 0,
                copper=reward_row[3] or 0,
                items=items,
                flags=flags,
            )

        # Load dialogues
        cursor.execute(
            """
            SELECT dialogue_id, speaker, text, is_player_choice
            FROM quest_dialogues WHERE quest_id = ?
        """,
            (quest_id,),
        )

        for row in cursor.fetchall():
            quest.dialogues.append(
                QuestDialogue(
                    dialogue_id=row[0],
                    speaker=row[1] or "NPC",
                    text=row[2] or "",
                    is_player_choice=bool(row[3]),
                )
            )

        conn.close()

        # Cache in memory
        self.quest_cache[quest_id] = quest

        return quest

    def get_all_quest_ids(self) -> List[int]:
        """Get list of all cached quest IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT quest_id FROM lua_quests ORDER BY quest_id")
        quest_ids = [row[0] for row in cursor.fetchall()]

        conn.close()
        return quest_ids

    def has_quest_data(self, quest_id: int) -> bool:
        """Check if quest data exists in cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM lua_quests WHERE quest_id = ? LIMIT 1", (quest_id,)
        )
        exists = cursor.fetchone() is not None

        conn.close()
        return exists

    def clear_cache(self):
        """Clear all cached Lua quest data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM lua_quests")
        cursor.execute("DELETE FROM quest_objectives")
        cursor.execute("DELETE FROM quest_requirements")
        cursor.execute("DELETE FROM quest_rewards")
        cursor.execute("DELETE FROM quest_dialogues")

        conn.commit()
        conn.close()

        self.quest_cache.clear()
        self.cache_loaded = False

        logger.info("Lua quest cache cleared")

    def _update_metadata(self, key: str, value: str):
        """Update metadata in cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO cache_metadata (key, value)
            VALUES (?, ?)
        """,
            (key, value),
        )

        conn.commit()
        conn.close()

    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata from cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM cache_metadata WHERE key = ?", (key,))
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else None

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) FROM lua_quests")
        stats["total_quests"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM quest_objectives")
        stats["total_objectives"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM quest_requirements")
        stats["total_requirements"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM quest_dialogues")
        stats["total_dialogues"] = cursor.fetchone()[0]

        conn.close()
        return stats

    def preload_cache(self):
        """Preload all quest data into memory cache"""
        if self.cache_loaded:
            return

        quest_ids = self.get_all_quest_ids()
        logger.info(f"Preloading {len(quest_ids)} quests into memory...")

        for quest_id in quest_ids:
            self.get_quest_data(quest_id)  # This will cache in memory

        self.cache_loaded = True
        logger.info(f"Preloaded {len(self.quest_cache)} quests")


# Singleton instance
_lua_data_manager_instance: Optional[LuaDataManager] = None


def get_lua_data_manager() -> LuaDataManager:
    """Get singleton instance of LuaDataManager"""
    global _lua_data_manager_instance
    if _lua_data_manager_instance is None:
        _lua_data_manager_instance = LuaDataManager()
    return _lua_data_manager_instance


def parse_lua_scripts(lua_directory: str, force_refresh: bool = False) -> int:
    """Convenience function to parse Lua scripts"""
    manager = get_lua_data_manager()
    return manager.parse_lua_directory(Path(lua_directory), force_refresh)


def get_quest_lua_data(quest_id: int) -> Optional[QuestData]:
    """Convenience function to get quest Lua data"""
    manager = get_lua_data_manager()
    return manager.get_quest_data(quest_id)
