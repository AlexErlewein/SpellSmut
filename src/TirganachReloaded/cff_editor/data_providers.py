"""
Data Providers for CFF Editor
Provides abstraction layer between GUI and data sources (CFF files, databases)
"""

import os
import sqlite3
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from TirganachReloaded.tirganach.types import Language

# Database schema version
SCHEMA_VERSION = "1.0.0"


@dataclass
class QuestData:
    """Quest data structure"""

    quest_id: int
    name_id: Optional[int] = None
    description_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class QuestDialogData:
    """Quest dialog data structure"""

    dialog_id: int
    quest_id: int
    speaker_id: Optional[int] = None
    text_id: Optional[int] = None
    next_dialog_id: Optional[int] = None
    conditions: Optional[str] = None
    text: Optional[str] = None


class DataProvider(ABC):
    """Abstract base class for data providers"""

    @abstractmethod
    def get_quests(self) -> List[QuestData]:
        """Get all quests"""
        pass

    @abstractmethod
    def get_quest_by_id(self, quest_id: int) -> Optional[QuestData]:
        """Get quest by ID"""
        pass

    @abstractmethod
    def get_quest_dialogs(self, quest_id: int) -> List[QuestDialogData]:
        """Get dialogs for a quest"""
        pass

    @abstractmethod
    def get_localised_text(self, text_id: int, language: Language) -> Optional[str]:
        """Get localised text"""
        pass

    @abstractmethod
    def get_table(self, table_name: str) -> Any:
        """Get raw table data (for backward compatibility)"""
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if data is loaded"""
        pass


class CFFProvider(DataProvider):
    """Data provider that wraps GameData object directly"""

    def __init__(self, game_data: Any):
        self.game_data = game_data

    def get_quests(self) -> List[QuestData]:
        """Get all quests from CFF"""
        if not self.game_data:
            return []

        quests_table = self.get_table("quests")
        if not quests_table:
            return []

        quests = []
        for quest in quests_table:
            quest_data = QuestData(
                quest_id=getattr(quest, "quest_id", 0),
                name_id=getattr(quest, "name_id", None),
                description_id=getattr(quest, "description_id", None),
            )
            quests.append(quest_data)

        return quests

    def get_quest_by_id(self, quest_id: int) -> Optional[QuestData]:
        """Get quest by ID from CFF"""
        quests = self.get_quests()
        return next((q for q in quests if q.quest_id == quest_id), None)

    def get_quest_dialogs(self, quest_id: int) -> List[QuestDialogData]:
        """Get dialogs for a quest from CFF"""
        if not self.game_data:
            return []

        dialogs_table = self.get_table("quest_dialogs")
        if not dialogs_table:
            return []

        dialogs = []
        for dialog in dialogs_table:
            if getattr(dialog, "quest_id", None) == quest_id:
                dialog_data = QuestDialogData(
                    dialog_id=getattr(dialog, "dialog_id", 0),
                    quest_id=getattr(dialog, "quest_id", 0),
                    speaker_id=getattr(dialog, "speaker_id", None),
                    text_id=getattr(dialog, "text_id", None),
                    next_dialog_id=getattr(dialog, "next_dialog_id", None),
                    conditions=getattr(dialog, "conditions", None),
                )
                dialogs.append(dialog_data)

        return dialogs

    def get_localised_text(self, text_id: int, language: Language) -> Optional[str]:
        """Get localised text from CFF"""
        if not self.game_data:
            return None

        localisation_table = self.get_table("localisation")
        if not localisation_table:
            return None

        for entry in localisation_table:
            if (
                getattr(entry, "text_id", None) == text_id
                and getattr(entry, "language", None) == language
            ):
                return getattr(entry, "text", "")

        return None

    def get_table(self, table_name: str) -> Any:
        """Get raw table data"""
        if not self.game_data:
            return None
        return getattr(self.game_data, table_name, None)

    def is_loaded(self) -> bool:
        """Check if data is loaded"""
        return self.game_data is not None


class DBProvider(DataProvider):
    """Data provider that uses SQLite database"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
        return self._connection

    def _execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute a query and return results"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_quests(self) -> List[QuestData]:
        """Get all quests from database"""
        query = """
        SELECT q.quest_id, q.name_id, q.description_id,
               l1.text as name, l2.text as description
        FROM quests q
        LEFT JOIN localisation l1 ON q.name_id = l1.text_id AND l1.language = 1
        LEFT JOIN localisation l2 ON q.description_id = l2.text_id AND l2.language = 1
        ORDER BY q.quest_id
        """

        results = self._execute_query(query)
        return [
            QuestData(
                quest_id=row[0],
                name_id=row[1],
                description_id=row[2],
                name=row[3],
                description=row[4],
            )
            for row in results
        ]

    def get_quest_by_id(self, quest_id: int) -> Optional[QuestData]:
        """Get quest by ID from database"""
        query = """
        SELECT q.quest_id, q.name_id, q.description_id,
               l1.text as name, l2.text as description
        FROM quests q
        LEFT JOIN localisation l1 ON q.name_id = l1.text_id AND l1.language = 1
        LEFT JOIN localisation l2 ON q.description_id = l2.text_id AND l2.language = 1
        WHERE q.quest_id = ?
        """

        results = self._execute_query(query, (quest_id,))
        if results:
            row = results[0]
            return QuestData(
                quest_id=row[0],
                name_id=row[1],
                description_id=row[2],
                name=row[3],
                description=row[4],
            )
        return None

    def get_quest_dialogs(self, quest_id: int) -> List[QuestDialogData]:
        """Get dialogs for a quest from database"""
        query = """
        SELECT qd.dialog_id, qd.quest_id, qd.speaker_id, qd.text_id,
               qd.next_dialog_id, qd.conditions, l.text
        FROM quest_dialogs qd
        LEFT JOIN localisation l ON qd.text_id = l.text_id AND l.language = 1
        WHERE qd.quest_id = ?
        ORDER BY qd.dialog_id
        """

        results = self._execute_query(query, (quest_id,))
        return [
            QuestDialogData(
                dialog_id=row[0],
                quest_id=row[1],
                speaker_id=row[2],
                text_id=row[3],
                next_dialog_id=row[4],
                conditions=row[5],
                text=row[6],
            )
            for row in results
        ]

    def get_localised_text(self, text_id: int, language: Language) -> Optional[str]:
        """Get localised text from database"""
        # Handle Language enum properly
        if hasattr(language, "value"):
            language_value = language.value
        elif isinstance(language, int):
            language_value = language
        else:
            language_value = 1  # Default to English

        query = "SELECT text FROM localisation WHERE text_id = ? AND language = ?"
        results = self._execute_query(query, (text_id, language_value))
        return results[0][0] if results else None

    def get_table(self, table_name: str) -> Any:
        """Get raw table data - not supported for DB provider"""
        # For backward compatibility, this could return a list-like interface
        # but for now, return None to indicate DB-only provider
        return None

    def is_loaded(self) -> bool:
        """Check if database is accessible"""
        try:
            self._execute_query(
                "SELECT 1 FROM metadata WHERE key = 'schema_version' LIMIT 1"
            )
            return True
        except:
            return False

    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None


class DatabaseManager:
    """Manages SQLite database creation and population"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_schema(self):
        """Create database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS localisation (
            text_id INTEGER,
            language INTEGER,
            text TEXT,
            PRIMARY KEY (text_id, language)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            quest_id INTEGER PRIMARY KEY,
            name_id INTEGER,
            description_id INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quest_dialogs (
            dialog_id INTEGER PRIMARY KEY,
            quest_id INTEGER,
            speaker_id INTEGER,
            text_id INTEGER,
            next_dialog_id INTEGER,
            conditions TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        # Create indices for performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_quests_name_id ON quests(name_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_quests_description_id ON quests(description_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_quest_dialogs_quest_id ON quest_dialogs(quest_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_quest_dialogs_text_id ON quest_dialogs(text_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_localisation_text_id ON localisation(text_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_localisation_language ON localisation(language)"
        )

        conn.commit()
        conn.close()

    def populate_from_cff(self, game_data: Any, fingerprint: str):
        """Populate database from GameData object"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Clear existing data
            cursor.execute("DELETE FROM localisation")
            cursor.execute("DELETE FROM quests")
            cursor.execute("DELETE FROM quest_dialogs")
            cursor.execute("DELETE FROM metadata")

            # Populate localisation
            localisation_table = getattr(game_data, "localisation", [])
            localisation_data = []
            for entry in localisation_table:
                language_value = getattr(entry, "language", 0)
                # Convert Language enum to int if needed
                try:
                    language_value = int(language_value)
                except (TypeError, ValueError):
                    language_value = 0
                localisation_data.append(
                    (
                        getattr(entry, "text_id", 0),
                        language_value,
                        getattr(entry, "text", ""),
                    )
                )

            if localisation_data:
                cursor.executemany(
                    "INSERT OR REPLACE INTO localisation (text_id, language, text) VALUES (?, ?, ?)",
                    localisation_data,
                )

            # Populate quests
            quests_table = getattr(game_data, "quests", [])
            quests_data = []
            for quest in quests_table:
                quests_data.append(
                    (
                        getattr(quest, "quest_id", 0),
                        getattr(quest, "name_id", None),
                        getattr(quest, "description_id", None),
                    )
                )

            if quests_data:
                cursor.executemany(
                    "INSERT OR REPLACE INTO quests (quest_id, name_id, description_id) VALUES (?, ?, ?)",
                    quests_data,
                )

            # Populate quest dialogs
            quest_dialogs_table = getattr(game_data, "quest_dialogs", [])
            dialogs_data = []
            for dialog in quest_dialogs_table:
                dialogs_data.append(
                    (
                        getattr(dialog, "dialog_id", 0),
                        getattr(dialog, "quest_id", 0),
                        getattr(dialog, "speaker_id", None),
                        getattr(dialog, "text_id", None),
                        getattr(dialog, "next_dialog_id", None),
                        getattr(dialog, "conditions", None),
                    )
                )

            if dialogs_data:
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO quest_dialogs (dialog_id, quest_id, speaker_id, text_id, next_dialog_id, conditions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    dialogs_data,
                )

            # Insert metadata
            metadata = [
                ("schema_version", SCHEMA_VERSION),
                ("fingerprint", fingerprint),
                ("created_at", str(__import__("time").time())),
            ]
            cursor.executemany(
                "INSERT INTO metadata (key, value) VALUES (?, ?)", metadata
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def is_valid_for_fingerprint(self, fingerprint: str) -> tuple[bool, Optional[str]]:
        """Check if database is valid for given fingerprint

        Returns:
            tuple: (is_valid, reason_for_invalid)
            - is_valid: True if database is valid
            - reason_for_invalid: string describing why invalid, None if valid
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check schema version
            cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, "Schema version not found in database"
            db_schema_version = result[0]
            if db_schema_version != SCHEMA_VERSION:
                conn.close()
                return (
                    False,
                    f"Schema version mismatch: {db_schema_version} → {SCHEMA_VERSION}",
                )

            # Check fingerprint
            cursor.execute("SELECT value FROM metadata WHERE key = 'fingerprint'")
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, "Fingerprint not found in database"
            db_fingerprint = result[0]
            if db_fingerprint != fingerprint:
                conn.close()
                return False, "Fingerprint mismatch: file changed"

            conn.close()
            return True, None

        except Exception as e:
            return False, f"Database validation error: {str(e)}"

        except:
            return False
