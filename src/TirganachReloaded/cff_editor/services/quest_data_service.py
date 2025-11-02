"""
Quest Data Service
Central service for loading and merging quest data from multiple sources
Includes caching mechanism similar to CFF loading
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from ..models.quest_models import (
    Dialogue,
    EnhancedQuestData,
    FileReference,
    MapLocation,
    QuestRelationship,
    QuestReward,
    QuestStatistics,
)


class QuestDataService:
    """Service for accessing enhanced quest data"""
    
    def __init__(self, project_root: Path, use_cache: bool = True):
        """
        Initialize the quest data service
        
        Args:
            project_root: Root directory of the project
            use_cache: Whether to use cached data (default: True)
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "src" / "TirganachReloaded" / "data"
        self.cache_dir = self.data_dir / "cache" / "quest_data"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_cache = use_cache
        
        # Cache file paths
        self.cache_file = self.cache_dir / "quest_data_cache.pkl"
        self.cache_timestamp_file = self.cache_dir / "cache_timestamp.txt"
        
        # In-memory cache for loaded data
        self._quest_descriptions_cache: Optional[Dict] = None
        self._quest_maps_cache: Optional[Dict] = None
        self._quest_rewards_cache: Optional[Dict] = None
        self._merged_cache: Optional[Dict] = None  # Cache for merged quest data
        
        # Extended dialogues (hardcoded from our extraction)
        self._extended_dialogues = self._load_extended_dialogues()
        
        # Try to load from cache
        if self.use_cache:
            if not self._load_from_cache():
                # Cache doesn't exist or is expired, build it
                logger.info("Building quest data cache...")
                self.rebuild_cache(force=False)
    
    def _load_extended_dialogues(self) -> Dict[int, List[tuple]]:
        """Load extended story dialogues (from our extraction)"""
        return {
            380: [
                ("Ich suche nach Amras Rüstung! Orthanc sandte mich zu Euch!", 
                 "I'm searching for Amra's armor! Orthanc sent me to you!"),
                ("Amra? Amra ist fort! Lea ist fort! Nur die Götter wissen, was aus ihnen geworden ist!", 
                 "Amra? Amra is gone! Lea is gone! Only the gods know what became of them!"),
                ("Amra war ein Krieger - ein Hitzkopf! Aber das Herz am rechten Fleck!", 
                 "Amra was a warrior - a hothead! But with his heart in the right place!"),
                ("Und Lea? Lea war das schönste Geschöpf, das die Welt je erblickt hat!", 
                 "And Lea? Lea was the most beautiful creature the world has ever seen!"),
            ],
            381: [
                ("Ihr müsst wissen, Amra verdingte sich einst als Söldner für meinen Vater!", 
                 "You must know, Amra once served as a mercenary for my father!"),
                ("So schickte mein Vater Amra fort! Lea gab ihm als Zeichen ihrer Gunst ihren wertvollsten Besitz, das Pfand der Götter!", 
                 "So my father sent Amra away! Lea gave him as a sign of her favor her most valuable possession, the Pledge of the Gods!"),
                ("Tyrgar, der Fischer, war einer der Waffenbrüder Amras!", 
                 "Tyrgar, the fisherman, was one of Amra's warrior brothers!"),
            ],
            384: [
                ("Ihr sucht nach der Rüstung Amras, nicht wahr?", 
                 "You're searching for Amra's armor, aren't you?"),
                ("Schön! Lasst uns reden... aber nicht hier! Die Stadt hat zu viele Ohren! Trefft mich am Wildland Pass!", 
                 "Good! Let's talk... but not here! The city has too many ears! Meet me at Wildland Pass!"),
            ],
            385: [
                ("Ihr seid doch auf der Suche nach Lea und Amra, nicht wahr?", 
                 "You're searching for Lea and Amra, aren't you?"),
                ("Ich weiß nur... dass es ein Grab gibt... eine Grabstätte in Wisper... man sagt, Lea liege dort!", 
                 "I only know... that there is a grave... a tomb in Wisper... they say Lea lies there!"),
            ],
            390: [
                ("Wochenlang irrten wir in der Wüstenei umher! Amra war wie rasend!", 
                 "For weeks we wandered through the desert! Amra was like a madman!"),
                ("Ja! Ein Magier mit dunkler Kapuze, und von unglaublicher Macht!", 
                 "Yes! A magician with a dark hood, and of incredible power!"),
                ("Als ich erwachte, fand ich Amra tot neben mir! Das Pfand der Götter war verschwunden.", 
                 "When I awoke, I found Amra dead beside me! The Pledge of the Gods had disappeared."),
            ],
            391: [
                ("(Hier fiel Amra im ehrenvollen Kampf)", 
                 "(Here Amra fell in honorable combat)"),
                ("(Ein verwitterter Grabstein)", 
                 "(A weathered tombstone)"),
            ]
        }
    
    def _load_quest_descriptions(self) -> Dict:
        """Load quest descriptions from our extraction"""
        if self._quest_descriptions_cache is None:
            # Use the existing quest_maps_and_descriptions.json file
            file_path = self.data_dir / "quest_maps_and_descriptions.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Transform the data to match expected structure
                    self._quest_descriptions_cache = {}
                    for quest_id, quest_info in data.items():
                        self._quest_descriptions_cache[quest_id] = {
                            'cff_data': {
                                'name': quest_info.get('name'),
                                'parent_id': 0,  # Default value
                                'order_index': 0  # Default value
                            },
                            'lua_original': {
                                'files': [],
                                'dialogues': []
                            }
                        }
            else:
                self._quest_descriptions_cache = {}
        return self._quest_descriptions_cache or {}
    
    def _load_quest_maps(self) -> Dict:
        """Load quest map locations from our extraction"""
        if self._quest_maps_cache is None:
            file_path = self.data_dir / "quest_maps_and_descriptions.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._quest_maps_cache = json.load(f)
            else:
                self._quest_maps_cache = {}
        return self._quest_maps_cache or {}
    
    def _load_quest_rewards(self) -> Dict:
        """Load quest rewards mapping"""
        if self._quest_rewards_cache is None:
            # Try to load from existing reward mappings
            file_path = self.data_dir / "quest_reward_mappings.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._quest_rewards_cache = json.load(f)
            else:
                # Fallback to hardcoded rewards from our extraction
                self._quest_rewards_cache = self._get_hardcoded_rewards()
        return self._quest_rewards_cache or {}
    
    def _get_hardcoded_rewards(self) -> Dict:
        """Hardcoded rewards from our extraction"""
        return {
            "380": {"xp": 200, "flags": ["AmraUndLea1Liannon1"]},
            "381": {"xp": 400, "flags": ["AmraUndLea1Liannon2"]},
            "382": {"xp": 500, "flags": ["AmraUndLea2Liannon1"]},
            "383": {"xp": 300, "flags": ["AmraUndLea2Liannon2"]},
            "384": {"xp": 500, "flags": ["AmraUndLea3Sentos"]},
            "385": {"xp": 800, "flags": ["AmraUndLea2Sentos"]},
            "390": {"xp": 1200, "flags": ["AmraUndLea4"]},
            "391": {"xp": 2000, "flags": ["AmraLeaGrab", "AmraUndLea5"]},
        }
    
    def _infer_map_locations(self, quest_id: int) -> List[MapLocation]:
        """Infer map locations for quests without explicit data"""
        # Quests in Liannon (based on NPC names)
        liannon_quests = [381, 382, 383, 388, 389]
        if quest_id in liannon_quests:
            return [MapLocation(code="P1", name="Liannon")]
        return []
    
    def get_enhanced_quest_data(self, quest_id: int, cff_quest_data: Optional[Dict] = None) -> EnhancedQuestData:
        """
        Get complete enhanced quest data by merging all sources
        
        Args:
            quest_id: Quest ID to retrieve
            cff_quest_data: Optional CFF quest data (from GameData)
            
        Returns:
            EnhancedQuestData object with all available information
        """
        # Check merged cache first
        quest_id_str = str(quest_id)
        if self._merged_cache and quest_id_str in self._merged_cache:
            cached_data = self._merged_cache[quest_id_str]
            # If CFF data provided, update the cached data with it
            if cff_quest_data:
                cached_data.name = cff_quest_data.get('name', cached_data.name)
                cached_data.description = cff_quest_data.get('description', cached_data.description)
                cached_data.parent_id = cff_quest_data.get('parent_quest_id', cached_data.parent_id)
                cached_data.order_index = cff_quest_data.get('order_index', cached_data.order_index)
                cached_data.name_id = cff_quest_data.get('name_id', cached_data.name_id)
                cached_data.description_id = cff_quest_data.get('description_id', cached_data.description_id)
            return cached_data
        
        # Load data sources
        quest_descriptions = self._load_quest_descriptions()
        quest_maps = self._load_quest_maps()
        quest_rewards = self._load_quest_rewards()
        
        # Start with basic data
        quest_data = EnhancedQuestData(quest_id=quest_id, name=f"Quest {quest_id}")
        
        # Merge CFF data if provided
        if cff_quest_data:
            quest_data.name = cff_quest_data.get('name', quest_data.name)
            quest_data.description = cff_quest_data.get('description', '')
            quest_data.parent_id = cff_quest_data.get('parent_quest_id', 0)
            quest_data.order_index = cff_quest_data.get('order_index', 0)
            quest_data.name_id = cff_quest_data.get('name_id', 0)
            quest_data.description_id = cff_quest_data.get('description_id', 0)
        
        # Get quest description data
        quest_id_str = str(quest_id)
        if quest_id_str in quest_descriptions:
            desc_data = quest_descriptions[quest_id_str]
            
            # Update basic info from our extraction
            if 'cff_data' in desc_data:
                cff = desc_data['cff_data']
                if not quest_data.name or quest_data.name == f"Quest {quest_id}":
                    quest_data.name = cff.get('name', quest_data.name)
                quest_data.parent_id = cff.get('parent_id', quest_data.parent_id)
                quest_data.order_index = cff.get('order_index', quest_data.order_index)
            
            # Add file references
            if 'lua_original' in desc_data:
                lua_data = desc_data['lua_original']
                for file_info in lua_data.get('files', []):
                    quest_data.file_references.append(
                        FileReference(
                            path=file_info['path'],
                            reference_count=file_info['references']
                        )
                    )
                
                # Add dialogues from Lua
                for dlg in lua_data.get('dialogues', []):
                    quest_data.dialogues.append(
                        Dialogue(
                            text=dlg['text'],
                            source_file=dlg['file'],
                            dialogue_type="Extracted"
                        )
                    )
        
        # Add map locations
        if quest_id_str in quest_maps:
            map_data = quest_maps[quest_id_str]
            for map_info in map_data.get('maps', []):
                quest_data.map_locations.append(
                    MapLocation(
                        code=map_info['code'],
                        name=map_info['name']
                    )
                )
        
        # Infer missing map locations
        if not quest_data.map_locations:
            quest_data.map_locations = self._infer_map_locations(quest_id)
        
        # Add extended story dialogues
        if quest_id in self._extended_dialogues:
            quest_data.has_extended_dialogues = True
            for de_text, en_text in self._extended_dialogues[quest_id]:
                quest_data.dialogues.append(
                    Dialogue(
                        text=de_text,
                        translation=en_text,
                        source_file="Extended Story Context",
                        dialogue_type="Story"
                    )
                )
        
        # Add rewards
        if quest_id_str in quest_rewards:
            reward_data = quest_rewards[quest_id_str]
            quest_data.rewards = QuestReward(
                xp=reward_data.get('xp', 0),
                reward_flags=reward_data.get('flags', []),
                items=reward_data.get('items', []),
                gold=reward_data.get('gold', 0)
            )
        
        # Calculate statistics
        quest_data.lua_files_count = len(quest_data.file_references)
        quest_data.total_lua_references = sum(f.reference_count for f in quest_data.file_references)
        
        quest_data.statistics = QuestStatistics(
            total_dialogues=len(quest_data.dialogues),
            total_files=quest_data.lua_files_count,
            total_references=quest_data.total_lua_references,
            total_maps=len(quest_data.map_locations),
            xp_reward=quest_data.rewards.xp if quest_data.rewards else 0
        )
        
        return quest_data
    
    def get_quest_relationships(self, quest_id: int, all_quests: List[Dict]) -> List[QuestRelationship]:
        """
        Get quest relationships (parent, siblings)
        
        Args:
            quest_id: Quest ID
            all_quests: List of all quests from CFF
            
        Returns:
            List of QuestRelationship objects
        """
        relationships = []
        
        # Find current quest
        current_quest = None
        for q in all_quests:
            if q.get('id') == quest_id or q.get('quest_id') == quest_id:
                current_quest = q
                break
        
        if not current_quest:
            return relationships
        
        parent_id = current_quest.get('parent_quest_id', 0)
        
        # Add parent
        if parent_id > 0:
            for q in all_quests:
                q_id = q.get('id') or q.get('quest_id')
                if isinstance(q_id, (int, str)) and int(q_id) == parent_id:
                    relationships.append(
                        QuestRelationship(
                            quest_id=int(q_id),
                            name=q.get('name', f'Quest {q_id}'),
                            relationship_type='parent'
                        )
                    )
                    break
        
        # Add siblings (same parent)
        if parent_id > 0:
            for q in all_quests:
                q_id = q.get('id') or q.get('quest_id')
                q_parent = q.get('parent_quest_id', 0)
                if (isinstance(q_id, (int, str)) and 
                    isinstance(q_parent, (int, str)) and 
                    int(q_id) != quest_id and 
                    int(q_parent) == parent_id):
                    relationships.append(
                        QuestRelationship(
                            quest_id=int(q_id),
                            name=q.get('name', f'Quest {q_id}'),
                            relationship_type='sibling'
                        )
                    )
        
        # Add children
        for q in all_quests:
            q_id = q.get('id') or q.get('quest_id')
            q_parent = q.get('parent_quest_id', 0)
            if (isinstance(q_id, (int, str)) and 
                isinstance(q_parent, (int, str)) and 
                int(q_parent) == quest_id):
                relationships.append(
                    QuestRelationship(
                        quest_id=int(q_id),
                        name=q.get('name', f'Quest {q_id}'),
                        relationship_type='child'
                    )
                )
        
        return relationships
    
    def _load_from_cache(self):
        """Load quest data from cache if available and valid"""
        if not self.cache_file.exists():
            return False
        
        try:
            # Check if cache is still valid (less than 24 hours old)
            cache_age = datetime.now().timestamp() - self.cache_file.stat().st_mtime
            if cache_age > 86400:  # 24 hours in seconds
                logger.info("Quest data cache expired, will reload")
                return False
            
            # Load cached data
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self._quest_descriptions_cache = cache_data.get('descriptions')
            self._quest_maps_cache = cache_data.get('maps')
            self._quest_rewards_cache = cache_data.get('rewards')
            self._merged_cache = cache_data.get('merged')
            
            logger.info(f"Loaded quest data from cache ({len(self._merged_cache or {})} quests)")
            return True
        except Exception as e:
            logger.warning(f"Failed to load quest data cache: {e}")
            return False
    
    def _save_to_cache(self):
        """Save quest data to cache"""
        try:
            cache_data = {
                'descriptions': self._quest_descriptions_cache,
                'maps': self._quest_maps_cache,
                'rewards': self._quest_rewards_cache,
                'merged': self._merged_cache,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            # Save timestamp
            with open(self.cache_timestamp_file, 'w') as f:
                f.write(datetime.now().isoformat())
            
            logger.info("Saved quest data to cache")
            return True
        except Exception as e:
            logger.warning(f"Failed to save quest data cache: {e}")
            return False
    
    def rebuild_cache(self, force: bool = True):
        """Rebuild the quest data cache"""
        logger.info("Rebuilding quest data cache...")
        
        # Clear existing cache
        self.clear_cache()
        
        # Force reload all data
        self._quest_descriptions_cache = None
        self._quest_maps_cache = None
        self._quest_rewards_cache = None
        
        # Load fresh data
        self._load_quest_descriptions()
        self._load_quest_maps()
        self._load_quest_rewards()
        
        # Build merged cache for common quests
        self._merged_cache = {}
        for quest_id in [379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 393]:
            try:
                quest_data = self.get_enhanced_quest_data(quest_id)
                self._merged_cache[str(quest_id)] = quest_data
            except Exception as e:
                logger.warning(f"Failed to cache quest {quest_id}: {e}")
        
        # Save to disk
        self._save_to_cache()
        logger.info(f"Cache rebuilt with {len(self._merged_cache)} quests")
    
    def clear_cache(self):
        """Clear all cached data (in-memory and disk)"""
        # Clear in-memory cache
        self._quest_descriptions_cache = None
        self._quest_maps_cache = None
        self._quest_rewards_cache = None
        self._merged_cache = None
        
        # Clear disk cache
        if self.cache_file.exists():
            self.cache_file.unlink()
        if self.cache_timestamp_file.exists():
            self.cache_timestamp_file.unlink()
        
        logger.info("Quest data cache cleared")
