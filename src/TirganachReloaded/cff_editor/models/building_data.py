from dataclasses import dataclass, field
from typing import List, Optional

from PySide6.QtGui import QColor


@dataclass
class BuildingResourceCost:
    """Represents the resource cost for a building or action."""
    resource_name: str
    amount: int


@dataclass
class BuildingButton:
    """Represents a button in a building's UI (e.g., train unit, research)."""
    button_id: int
    name: str
    description: str = ""
    costs: List[BuildingResourceCost] = field(default_factory=list)
    action_type: str = ""  # e.g., 'train_unit', 'research_upgrade'
    action_target_id: int = 0  # e.g., unit_stats_id or upgrade_id
    research_time: int = 0


@dataclass
class BuildingData:
    """Holds all data collected from the Building Wizard."""
    # Step 1: Basic Properties
    building_id: Optional[int] = None
    name: str = ""
    description: str = ""
    race_name: str = "HUMANS"
    health: int = 100
    required_building_id: int = 0

    # Step 2: Visuals
    asset_name: str = ""

    # Step 3: Construction
    construction_costs: List[BuildingResourceCost] = field(default_factory=list)

    # Step 4: Functions
    functions: List[BuildingButton] = field(default_factory=list)

    # Step 5: Plan Item
    plan_item_name: str = ""

    # Metadata
    is_new: bool = True
