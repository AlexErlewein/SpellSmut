from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field


class NpcType(Enum):
    FRIENDLY = "friendly"
    MERCHANT = "merchant"
    GUARD = "guard"
    HOSTILE = "hostile"


class CharacterClass(Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    MULTI_CLASS = "multi_class"


class VoiceType(Enum):
    MAIN_CHARACTER_MALE = "main_male"
    MAIN_CHARACTER_FEMALE = "main_female"
    HERO_MALE_1 = "hero_male_1"
    HERO_MALE_2 = "hero_male_2"
    HERO_MALE_3 = "hero_male_3"
    HERO_MALE_4 = "hero_male_4"
    HERO_MALE_5 = "hero_male_5"
    HERO_FEMALE_1 = "hero_female_1"
    HERO_FEMALE_2 = "hero_female_2"
    HERO_FEMALE_3 = "hero_female_3"
    HERO_FEMALE_4 = "hero_female_4"
    HERO_FEMALE_5 = "hero_female_5"
    CREATURE_BEAR = "bear"
    CREATURE_DEMON = "demon"
    CREATURE_DRAGON = "dragon"
    CREATURE_GOBLIN = "goblin"
    CREATURE_OGRE = "ogre"
    CREATURE_SKELETON = "skeleton"
    CREATURE_WOLF = "wolf"
    CREATURE_ZOMBIE = "zombie"


class ItemType(Enum):
    """Item types for merchant price modifiers"""

    UNKNOWN = 0
    EQUIPMENT = 1
    INVENTORY_RUNE = 2
    INSTALLED_RUNE = 3
    QUEST_ITEM = 4
    USABLE_ITEM = 5
    BOOK_SCROLL = 6


@dataclass
class NpcStats:
    """Base stats for NPC"""

    strength: int = 10
    stamina: int = 10
    agility: int = 10
    dexterity: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def to_dict(self) -> dict:
        return {
            "strength": self.strength,
            "stamina": self.stamina,
            "agility": self.agility,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NpcStats":
        return cls(**data)


@dataclass
class NpcCombatStats:
    """Combat-related stats"""

    health: int = 100
    mana: int = 50
    melee_attack: int = 10
    ranged_attack: int = 0
    magic_attack: int = 0
    physical_defense: int = 5
    magic_defense: int = 5
    fire_resistance: int = 0
    ice_resistance: int = 0
    black_resistance: int = 0
    mind_resistance: int = 0

    def to_dict(self) -> dict:
        return {
            "health": self.health,
            "mana": self.mana,
            "melee_attack": self.melee_attack,
            "ranged_attack": self.ranged_attack,
            "magic_attack": self.magic_attack,
            "physical_defense": self.physical_defense,
            "magic_defense": self.magic_defense,
            "fire_resistance": self.fire_resistance,
            "ice_resistance": self.ice_resistance,
            "black_resistance": self.black_resistance,
            "mind_resistance": self.mind_resistance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NpcCombatStats":
        return cls(**data)


@dataclass
class NpcEquipment:
    """Equipment assigned to NPC"""

    helmet_item_id: Optional[int] = None
    chest_item_id: Optional[int] = None
    legs_item_id: Optional[int] = None
    right_hand_item_id: Optional[int] = None
    left_hand_item_id: Optional[int] = None
    right_ring_item_id: Optional[int] = None
    left_ring_item_id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "helmet_item_id": self.helmet_item_id,
            "chest_item_id": self.chest_item_id,
            "legs_item_id": self.legs_item_id,
            "right_hand_item_id": self.right_hand_item_id,
            "left_hand_item_id": self.left_hand_item_id,
            "right_ring_item_id": self.right_ring_item_id,
            "left_ring_item_id": self.left_ring_item_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NpcEquipment":
        return cls(**data)


@dataclass
class NpcAppearance:
    """Visual appearance settings"""

    head_id: int = 0
    race: str = "HUMANS"
    gender: str = "MALE"
    voice_type: VoiceType = VoiceType.MAIN_CHARACTER_MALE

    def to_dict(self) -> dict:
        return {
            "head_id": self.head_id,
            "race": self.race,
            "gender": self.gender,
            "voice_type": self.voice_type.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NpcAppearance":
        data_copy = data.copy()
        data_copy["voice_type"] = VoiceType(data.get("voice_type", "main_male"))
        return cls(**data_copy)


@dataclass
class NpcBehavior:
    """AI and behavior settings"""

    movement_type: str = "stationary"
    interaction_radius: int = 5
    spawn_location: Optional[Tuple[int, int]] = None
    spawn_conditions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "movement_type": self.movement_type,
            "interaction_radius": self.interaction_radius,
            "spawn_location": list(self.spawn_location)
            if self.spawn_location
            else None,
            "spawn_conditions": self.spawn_conditions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NpcBehavior":
        data_copy = data.copy()
        if data.get("spawn_location"):
            data_copy["spawn_location"] = tuple(data["spawn_location"])
        return cls(**data_copy)


@dataclass
class NpcRewards:
    """Quest rewards when NPC is defeated or completes objective"""

    experience: int = 0
    gold: int = 0
    items: List[Dict[str, int]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"experience": self.experience, "gold": self.gold, "items": self.items}

    @classmethod
    def from_dict(cls, data: dict) -> "NpcRewards":
        return cls(**data)


@dataclass
class NpcSkill:
    """Individual skill data"""

    school: str
    level: int = 0

    def to_dict(self) -> dict:
        return {"school": self.school, "level": self.level}

    @classmethod
    def from_dict(cls, data: dict) -> "NpcSkill":
        return cls(**data)


@dataclass
class NpcSpell:
    """Individual spell data"""

    spell_id: int
    position: int = 0

    def to_dict(self) -> dict:
        return {"spell_id": self.spell_id, "position": self.position}

    @classmethod
    def from_dict(cls, data: dict) -> "NpcSpell":
        return cls(**data)


@dataclass
class MerchantItem:
    """Individual item in merchant inventory"""

    item_id: int
    stock: int = 1

    def to_dict(self) -> dict:
        return {"item_id": self.item_id, "stock": self.stock}

    @classmethod
    def from_dict(cls, data: dict) -> "MerchantItem":
        return cls(**data)


@dataclass
class MerchantPriceModifier:
    """Price multiplier for item types (CFF category 2047)"""

    item_type: ItemType = ItemType.EQUIPMENT
    multiplier: int = 100

    def to_dict(self) -> dict:
        return {"item_type": self.item_type.value, "multiplier": self.multiplier}

    @classmethod
    def from_dict(cls, data: dict) -> "MerchantPriceModifier":
        item_type = ItemType(data.get("item_type", 1))
        return cls(item_type=item_type, multiplier=data.get("multiplier", 100))


@dataclass
class MerchantData:
    """Complete merchant configuration (CFF categories 2041, 2042, 2047)"""

    merchant_id: int = 0
    linked_npc_id: int = 0
    inventory: List[MerchantItem] = field(default_factory=list)
    price_modifiers: List[MerchantPriceModifier] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "merchant_id": self.merchant_id,
            "linked_npc_id": self.linked_npc_id,
            "inventory": [item.to_dict() for item in self.inventory],
            "price_modifiers": [pm.to_dict() for pm in self.price_modifiers],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MerchantData":
        return cls(
            merchant_id=data.get("merchant_id", 0),
            linked_npc_id=data.get("linked_npc_id", 0),
            inventory=[MerchantItem.from_dict(i) for i in data.get("inventory", [])],
            price_modifiers=[
                MerchantPriceModifier.from_dict(pm)
                for pm in data.get("price_modifiers", [])
            ],
        )


@dataclass
class NpcCreationData:
    """Complete NPC definition for creation wizard"""

    npc_id: int
    creation_mode: str = "new"
    source_npc_id: Optional[int] = None

    name: str = ""
    title: str = ""
    description: str = ""
    npc_type: NpcType = NpcType.FRIENDLY
    character_class: CharacterClass = CharacterClass.WARRIOR
    level: int = 1
    faction: str = "HUMANS"

    base_stats: NpcStats = field(default_factory=NpcStats)
    derived_stats: NpcCombatStats = field(default_factory=NpcCombatStats)

    appearance: NpcAppearance = field(default_factory=NpcAppearance)

    behavior: NpcBehavior = field(default_factory=NpcBehavior)

    equipment: NpcEquipment = field(default_factory=NpcEquipment)
    rewards: NpcRewards = field(default_factory=NpcRewards)
    special_abilities: List[str] = field(default_factory=list)
    skills: List[NpcSkill] = field(default_factory=list)
    spells: List[NpcSpell] = field(default_factory=list)

    merchant_data: Optional[MerchantData] = None

    def to_dict(self) -> dict:
        result = {
            "npc_id": self.npc_id,
            "creation_mode": self.creation_mode,
            "source_npc_id": self.source_npc_id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "npc_type": self.npc_type.value,
            "character_class": self.character_class.value,
            "level": self.level,
            "faction": self.faction,
            "base_stats": self.base_stats.to_dict(),
            "derived_stats": self.derived_stats.to_dict(),
            "appearance": self.appearance.to_dict(),
            "behavior": self.behavior.to_dict(),
            "equipment": self.equipment.to_dict(),
            "rewards": self.rewards.to_dict(),
            "special_abilities": self.special_abilities,
            "skills": [skill.to_dict() for skill in self.skills],
            "spells": [spell.to_dict() for spell in self.spells],
        }
        if self.merchant_data:
            result["merchant_data"] = self.merchant_data.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "NpcCreationData":
        data_copy = data.copy()

        data_copy["npc_type"] = NpcType(data.get("npc_type", "friendly"))
        data_copy["character_class"] = CharacterClass(
            data.get("character_class", "warrior")
        )

        data_copy["base_stats"] = NpcStats.from_dict(data.get("base_stats", {}))
        data_copy["derived_stats"] = NpcCombatStats.from_dict(
            data.get("derived_stats", {})
        )
        data_copy["appearance"] = NpcAppearance.from_dict(data.get("appearance", {}))
        data_copy["behavior"] = NpcBehavior.from_dict(data.get("behavior", {}))
        data_copy["equipment"] = NpcEquipment.from_dict(data.get("equipment", {}))
        data_copy["rewards"] = NpcRewards.from_dict(data.get("rewards", {}))
        data_copy["skills"] = [NpcSkill.from_dict(s) for s in data.get("skills", [])]
        data_copy["spells"] = [NpcSpell.from_dict(s) for s in data.get("spells", [])]

        if data.get("merchant_data"):
            data_copy["merchant_data"] = MerchantData.from_dict(
                data.get("merchant_data", {})
            )

        return cls(**data_copy)


@dataclass
class NpcValidationResult:
    """Result of NPC validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
