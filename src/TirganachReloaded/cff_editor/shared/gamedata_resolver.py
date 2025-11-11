from pathlib import Path
from typing import Optional


def find_gamedata_path() -> Optional[str]:
    """Locate GameData.cff using a unified search order.

    Order:
    1) forge/OriginalGameFiles/data/GameData.cff
    2) forge/OriginalGameFiles/GameData.cff
    3) forge/src/OriginalGameFiles/data/GameData.cff
    4) forge/src/OriginalGameFiles/GameData.cff
    5) ~/SpellForce Platinum Edition/data/GameData.cff
    """
    here = Path(__file__).resolve()
    candidates = []

    try:
        # .../forge/src/TirganachReloaded/cff_editor/shared/gamedata_resolver.py
        # parents[4] -> .../forge
        forge_root = here.parents[4]
        candidates.append(forge_root / "OriginalGameFiles" / "data" / "GameData.cff")
        candidates.append(forge_root / "OriginalGameFiles" / "GameData.cff")
    except Exception:
        pass

    try:
        # parents[3] -> .../forge/src
        src_root = here.parents[3]
        candidates.append(src_root / "OriginalGameFiles" / "data" / "GameData.cff")
        candidates.append(src_root / "OriginalGameFiles" / "GameData.cff")
    except Exception:
        pass

    candidates.append(Path.home() / "SpellForce Platinum Edition" / "data" / "GameData.cff")

    for p in candidates:
        if p.exists():
            return str(p)
    return None
