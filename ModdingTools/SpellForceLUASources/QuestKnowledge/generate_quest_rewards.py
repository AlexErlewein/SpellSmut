#!/usr/bin/env python3
from __future__ import annotations
import re
import os
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import argparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "script"
REWARDS_LUA = SCRIPT_DIR / "GdsQuestRewards.lua"
OUT_DIR = ROOT / "QuestKnowledge"
CSV_PATH = OUT_DIR / "QuestRewards.csv"
MD_PATH = OUT_DIR / "QuestRewards.md"
# Workspace root (cleanup TirganachReloaded)
WORKSPACE_ROOT = ROOT.parents[1]
DATA_DIR = WORKSPACE_ROOT / "src" / "TirganachReloaded" / "data"

# ---------- Utility ----------

def read_text(path: Path) -> str:
    # Use latin-1 to be permissive with special chars
    with open(path, "r", encoding="latin-1", errors="replace") as f:
        return f.read()


def skip_comment(s: str, i: int) -> int:
    # Skip -- comment to end of line
    end = s.find("\n", i)
    return len(s) if end == -1 else end + 1


def skip_string(s: str, i: int) -> int:
    q = s[i]
    i += 1
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == q:
            i += 1
            break
        i += 1
    return i


def find_matching_brace(s: str, open_pos: int) -> int:
    assert s[open_pos] == "{"
    depth = 1
    i = open_pos + 1
    while i < len(s):
        c = s[i]
        if c == "-" and i + 1 < len(s) and s[i + 1] == "-":
            i = skip_comment(s, i)
            continue
        if c in ('"', "'"):
            i = skip_string(s, i)
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("No matching closing brace found")


# ---------- Parse GdsQuestRewards.lua ----------

Section = Dict[str, object]
Entry = Dict[str, object]

def parse_rewards_file(text: str) -> List[Section]:
    sections: List[Section] = []
    # Find each section header and following QuestRewardsP<ID> = {
    header_re = re.compile(r"^\s*--\s*quest rewards on\s+(.+?)\s*\n\s*QuestRewardsP(\d+)\s*=\s*\{", re.M)
    for m in header_re.finditer(text):
        platform_name = m.group(1).strip()
        platform_id = int(m.group(2))
        open_pos = m.end() - 1  # position of '{'
        close_pos = find_matching_brace(text, open_pos)
        block = text[open_pos:close_pos + 1]
        entries = parse_entries(block)
        sections.append({
            "platform_id": platform_id,
            "platform_name": platform_name,
            "entries": entries,
        })
    return sections


def parse_entries(block: str) -> List[Entry]:
    # block starts with '{' and ends with '}'
    assert block and block[0] == "{" and block[-1] == "}"
    content = block[1:-1]
    i = 0
    n = len(content)
    entries: List[Entry] = []

    while i < n:
        # skip whitespace and commas and newlines
        while i < n and content[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        # At top level, look for Key = {
        m = re.match(r"([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{", content[i:])
        if not m:
            # skip to next line if no key here
            nl = content.find("\n", i)
            i = n if nl == -1 else nl + 1
            continue
        key = m.group(1)
        open_pos = i + m.end() - 1
        inner_close = find_matching_brace(content, open_pos)
        inner = content[open_pos + 1:inner_close]

        # Extract fields
        xp = None
        m_xp = re.search(r"XP\s*=\s*\{\s*(\d+)\s*\}", inner)
        if m_xp:
            xp = int(m_xp.group(1))

        gold = silver = copper = 0
        m_money = re.search(r"Money\s*=\s*\{([^}]*)\}", inner)
        if m_money:
            money_str = m_money.group(1)
            m_gold = re.search(r"Gold\s*=\s*(\d+)", money_str)
            if m_gold: gold = int(m_gold.group(1))
            m_silver = re.search(r"Silver\s*=\s*(\d+)", money_str)
            if m_silver: silver = int(m_silver.group(1))
            m_copper = re.search(r"Copper\s*=\s*(\d+)", money_str)
            if m_copper: copper = int(m_copper.group(1))

        items: List[int] = []
        m_items = re.search(r"Items\s*=\s*\{([^}]*)\}", inner)
        if m_items:
            items_str = m_items.group(1)
            items = [int(x) for x in re.findall(r"\d+", items_str)]

        entries.append({
            "flag": key,
            "xp": xp,
            "gold": gold,
            "silver": silver,
            "copper": copper,
            "items_given": items,
            "items_taken": [],  # reward system only gives items here
        })

        i = inner_close + 1  # move after closing '}'
        # consume trailing spaces/commas
        while i < n and content[i] in " \t\r\n,":
            i += 1

    return entries


# ---------- Map reward flags -> quest ids from QuestXP.lua files ----------

def collect_reward_to_questid() -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    # Scan all lua files, not only *QuestXP.lua
    for p in SCRIPT_DIR.rglob("*.lua"):
        # skip the rewards file itself
        if p.name == "GdsQuestRewards.lua":
            continue
        try:
            text = read_text(p)
        except Exception:
            continue
        # Look for pairs in proximity: QuestState{QuestId=..., State=StateSolved} ... SetRewardFlagTrue{Name="Flag"}
        # Widen window to capture multi-line blocks.
        for m in re.finditer(
            r"QuestState\s*\{\s*QuestId\s*=\s*(\d+)\s*,\s*State\s*=\s*StateSolved\s*\}(.{0,2000}?)SetRewardFlagTrue\s*\{\s*Name\s*=\s*\"([^\"]+)\"\s*\}",
            text,
            flags=re.S,
        ):
            qid = int(m.group(1))
            flag = m.group(3)
            mapping[flag] = qid
    return mapping


# Improved mapping: analyze OnOneTimeEvent blocks
def collect_reward_to_questid_from_events() -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    qstate_re = re.compile(r"QuestState\s*\{\s*QuestId\s*=\s*(\d+)\s*,\s*State\s*=\s*StateSolved\s*\}")
    flag_re = re.compile(r"SetRewardFlagTrue\s*\{\s*Name\s*=\s*\"([^\"]+)\"\s*\}")

    for p in SCRIPT_DIR.rglob("*.lua"):
        if p.name == "GdsQuestRewards.lua":
            continue
        try:
            text = read_text(p)
        except Exception:
            continue

        idx = 0
        while True:
            pos = text.find("OnOneTimeEvent", idx)
            if pos == -1:
                break
            brace = text.find("{", pos)
            if brace == -1:
                idx = pos + 1
                continue
            try:
                end = find_matching_brace(text, brace)
            except Exception:
                idx = brace + 1
                continue
            block = text[brace:end+1]

            qids = [(m.start(), int(m.group(1))) for m in qstate_re.finditer(block)]
            flags = [(m.start(), m.group(1)) for m in flag_re.finditer(block)]

            unique_qids = sorted(set(q for _, q in qids))
            if unique_qids:
                if len(unique_qids) == 1:
                    qid = unique_qids[0]
                    for _, flg in flags:
                        mapping[flg] = qid
                else:
                    # multiple quest ids; assign nearest qid to each flag by position
                    for fpos, flg in flags:
                        nearest = None
                        best = None
                        for qpos, qid in qids:
                            dist = abs(qpos - fpos)
                            if best is None or dist < best:
                                best = dist
                                nearest = qid
                        if nearest is not None:
                            mapping[flg] = nearest

            idx = end + 1
    return mapping

# ---------- Collect SetRewardFlagTrue contexts and taken items ----------

def collect_reward_matches(window: int = 2500) -> List[Dict[str, object]]:
    """Find occurrences of SetRewardFlagTrue and capture a window around them for later scans.
    Returns a list of dicts: {flag, file, start, end}
    """
    matches: List[Dict[str, object]] = []
    setflag_re = re.compile(r"SetRewardFlagTrue\s*\{\s*Name\s*=\s*\"([^\"]+)\"\s*\}")
    for p in SCRIPT_DIR.rglob("*.lua"):
        if p.name == "GdsQuestRewards.lua":
            continue
        try:
            text = read_text(p)
        except Exception:
            continue
        for m in setflag_re.finditer(text):
            flag = m.group(1)
            s = max(0, m.start() - window)
            e = min(len(text), m.end() + window)
            matches.append({"flag": flag, "file": p, "start": s, "end": e})
    return matches


def find_taken_items_for_flags() -> Dict[str, List[int]]:
    """Scan windows around SetRewardFlagTrue for TransferItem{TakeItem=...} and map to flags."""
    flag2taken: Dict[str, List[int]] = {}
    take_re = re.compile(r"TransferItem\s*\{[^}]*TakeItem\s*=\s*(\d+)[^}]*\}", re.S)
    for m in collect_reward_matches():
        p: Path = m["file"]  # type: ignore[assignment]
        try:
            text = read_text(p)
        except Exception:
            continue
        slice_txt = text[m["start"]:m["end"]]  # type: ignore[index]
        taken = [int(x) for x in take_re.findall(slice_txt) if int(x) != 0]
        if taken:
            flag = m["flag"]  # type: ignore[index]
            lst = flag2taken.setdefault(flag, [])
            # keep unique while preserving order
            for t in taken:
                if t not in lst:
                    lst.append(t)
    return flag2taken


def annotate_taken_items(sections: List[Section], flag2taken: Dict[str, List[int]]):
    for sec in sections:
        for e in sec["entries"]:
            flag = e["flag"]
            if flag in flag2taken:
                e["items_taken"] = flag2taken[flag]


# ---------- External data integration (JSON in src/TirganachReloaded/data) ----------

def _load_json(path: Path) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_external_flag_to_qid_mappings() -> Dict[str, int]:
    """Load flag->quest_id mappings from data directory JSONs and merge."""
    mapping: Dict[str, int] = {}
    files = [
        DATA_DIR / "REWARD_TO_QUEST_ID_MASTER_MAP.json",
        DATA_DIR / "quest_id_to_reward_name_mappings.json",
        DATA_DIR / "REWARD_NAME_TO_QUEST_ID_MAPPINGS.json",
    ]
    for fp in files:
        data = _load_json(fp)
        if not data:
            continue
        if "mappings" in data and isinstance(data["mappings"], dict):
            for k, v in data["mappings"].items():
                try:
                    mapping[k] = int(v)
                except Exception:
                    continue
        else:
            # flat mapping
            for k, v in data.items():
                try:
                    mapping[k] = int(v)
                except Exception:
                    continue
    return mapping


def load_quest_rewards_complete() -> Dict[int, dict]:
    """Load quest_rewards_complete.json and return rewards_by_quest_id mapping."""
    path = DATA_DIR / "quest_rewards_complete.json"
    data = _load_json(path)
    by_id: Dict[int, dict] = {}
    if not data:
        return by_id
    rewards = data.get("rewards_by_quest_id", {}) if isinstance(data, dict) else {}
    for k, v in rewards.items():
        try:
            by_id[int(k)] = v
        except Exception:
            continue
    return by_id


def load_quest_maps_and_names() -> Dict[int, dict]:
    """Load quest_maps_and_descriptions.json and return quest_id -> {name, maps:[{code,name}]}"""
    path = DATA_DIR / "quest_maps_and_descriptions.json"
    data = _load_json(path)
    by_id: Dict[int, dict] = {}
    if not data or not isinstance(data, dict):
        return by_id
    for k, v in data.items():
        try:
            qid = int(k)
        except Exception:
            continue
        if isinstance(v, dict):
            by_id[qid] = v
    return by_id


def integrate_rewards_complete(sections: List[Section], reward2qid: Dict[str, int], complete: Dict[int, dict]):
    """Optionally fill missing XP/Money/Items from quest_rewards_complete for entries with a mapped quest_id."""
    for sec in sections:
        for e in sec["entries"]:
            flag = e["flag"]
            qid = reward2qid.get(flag)
            if qid is None:
                continue
            comp = complete.get(qid)
            if not comp:
                continue
            # Only fill if missing/zero in parsed entry
            if e.get("xp") in (None, 0):
                xp = comp.get("xp")
                if isinstance(xp, int) and xp > 0:
                    e["xp"] = xp
            # Money
            if e.get("gold", 0) == 0 and e.get("silver", 0) == 0 and e.get("copper", 0) == 0:
                for k in ("gold", "silver", "copper"):
                    val = comp.get(k)
                    if isinstance(val, int) and val > 0:
                        e[k] = val
            # Items (given): merge unique
            citems = comp.get("items")
            if isinstance(citems, list) and citems:
                existing = set(e.get("items_given", []))
                for it in citems:
                    try:
                        itn = int(it)
                    except Exception:
                        continue
                    if itn not in existing:
                        e["items_given"].append(itn)
                        existing.add(itn)


# ---------- Dynamic text-based matching (copied, decoupled) ----------

def load_cff_quest_data() -> Dict[int, dict]:
    """Load cff_quest_data.json for quest names/descriptions in multiple langs."""
    path = DATA_DIR / "cff_quest_data.json"
    data = _load_json(path)
    by_id: Dict[int, dict] = {}
    if not data or not isinstance(data, dict):
        return by_id
    for k, v in data.items():
        try:
            qid = int(k)
        except Exception:
            continue
        if isinstance(v, dict):
            by_id[qid] = v
    return by_id


def _texts_from_cff_record(rec: dict) -> List[str]:
    texts: List[str] = []
    # direct fields
    for key in ("name", "name_en", "name_de", "description_en", "description_de"):
        val = rec.get(key)
        if isinstance(val, str):
            texts.append(val)
    # attributes nested
    attrs = rec.get("attributes") or {}
    if isinstance(attrs, dict):
        for key in ("name", "description", "description2"):
            val = attrs.get(key)
            if isinstance(val, str):
                texts.append(val)
    return texts


_STOPWORDS_DE = {"der", "die", "das", "ein", "eine", "und", "nach", "vor", "part", "im", "in", "zu", "zum", "zur", "mit", "von", "den", "dem"}


def split_compound_parts(name: str) -> List[str]:
    # split German compound CamelCase and digits
    parts = re.findall(r"[A-ZÄÖÜ][a-zäöüß]+|[0-9]+|[A-Za-z]+", name)
    parts = [p for p in parts if p]
    # normalize
    norm = []
    for p in parts:
        pn = p.strip()
        if not pn:
            continue
        norm.append(pn)
    return norm


def match_flag_to_qid_by_text(flag: str, platform_code: str, qmeta: Dict[int, dict], cff: Dict[int, dict], loc_map: Optional[Dict[int, str]] = None) -> Optional[int]:
    parts = split_compound_parts(flag)
    # significant parts
    sig = [p for p in parts if p.lower() not in _STOPWORDS_DE and len(p) > 2 and not p.isdigit()]
    if not sig:
        sig = [p for p in parts if len(p) > 2]
    best_q = None
    best_score = 0
    # iterate quests that mention this platform
    for qid, meta in qmeta.items():
        maps = meta.get("maps") or []
        codes = [m.get("code") for m in maps if isinstance(m, dict) and m.get("code")]
        if platform_code and codes and platform_code not in codes:
            continue
        cff_rec = cff.get(qid) or {}
        texts_all = " \n ".join(_texts_from_cff_record(cff_rec)).lower()
        name_de = ""
        desc_de = ""
        if loc_map and isinstance(cff_rec, dict):
            name_id = cff_rec.get("name_id") or (cff_rec.get("attributes") or {}).get("name_id")
            desc_id = cff_rec.get("description_id") or (cff_rec.get("attributes") or {}).get("description_id")
            if isinstance(name_id, int) and name_id in loc_map:
                name_de = loc_map[name_id] or ""
            if isinstance(desc_id, int) and desc_id in loc_map:
                desc_de = loc_map[desc_id] or ""
        texts_de = (name_de + " \n " + desc_de).strip().lower()
        if not texts_all and not texts_de:
            continue
        # score as number of sig parts present
        score = 0
        for p in sig:
            pl = p.lower()
            if name_de and pl in name_de.lower():
                score += 3  # strongest signal
            elif desc_de and pl in desc_de.lower():
                score += 2  # strong signal
            elif texts_all and pl in texts_all:
                score += 1  # fallback
        # boost exact substring of the raw flag (lower)
        flag_l = flag.lower()
        if name_de and flag_l in name_de.lower():
            score += 4
        elif desc_de and flag_l in desc_de.lower():
            score += 3
        elif texts_all and flag_l in texts_all:
            score += 2
        if score > best_score:
            best_score = score
            best_q = qid
    # thresholds
    if best_q is not None and (best_score >= 3 or (best_score >= 2 and len(sig) <= 2)):
        return best_q
    return None


def augment_reward2qid_with_text_matching(sections: List[Section], reward2qid: Dict[str, int], qmeta: Dict[int, dict], cff: Dict[int, dict], loc_map: Optional[Dict[int, str]] = None):
    for sec in sections:
        platform_code = f"P{sec['platform_id']}"
        for e in sec["entries"]:
            flag = e["flag"]
            if flag in reward2qid:
                continue
            qid = match_flag_to_qid_by_text(flag, platform_code, qmeta, cff, loc_map)
            if qid is not None:
                reward2qid[flag] = qid


# ---------- Quest hierarchy helpers ----------

def _immediate_parent_id(cff_rec: dict) -> Optional[int]:
    attrs = cff_rec.get("attributes") or {}
    p1 = attrs.get("parent_quest_id")
    p2 = cff_rec.get("parent_id")
    if isinstance(p1, int) and p1:
        return p1
    if isinstance(p2, int) and p2:
        return p2
    return None


def build_parent_chain(qid: int, cff: Dict[int, dict], max_depth: int = 20) -> List[int]:
    chain: List[int] = []
    seen: set[int] = set()
    current = qid
    depth = 0
    while depth < max_depth:
        rec = cff.get(current)
        if not isinstance(rec, dict):
            break
        pid = _immediate_parent_id(rec)
        if not isinstance(pid, int) or pid == 0 or pid in seen:
            break
        chain.append(pid)
        seen.add(pid)
        current = pid
        depth += 1
    return chain


def resolve_quest_name(qid: int, cff: Dict[int, dict], loc_map: Dict[int, str], qmeta: Dict[int, dict]) -> str:
    cff_rec = cff.get(qid) or {}
    name_id = cff_rec.get("name_id") or (cff_rec.get("attributes") or {}).get("name_id")
    if isinstance(name_id, int) and name_id in loc_map:
        return loc_map.get(name_id, "") or ""
    meta = qmeta.get(qid) or {}
    return meta.get("name") or meta.get("quest_name") or ""


# ---------- Minimal CFF reader for NPC names ----------

def _decode_fixed_string(b: bytes) -> str:
    s = b.decode("latin-1", errors="ignore")
    s = s.split("\x00", 1)[0]
    return s.strip()


def load_cff_npc_map(cff_path: Optional[Path] = None) -> Dict[int, str]:
    tables_order = [
        "spells", "spell_names", "unknown3", "creature_stats", "creature_skills", "hero_spells",
        "items", "armor", "item_installs", "weapons", "item_requirements", "item_effects", "item_ui",
        "spell_effects", "localisation", "races", "heads", "creatures", "creature_equipment",
        "creature_spells", "creature_resources", "drops", "unit_building_requirements", "buildings",
        "building_graphics", "building_requirements", "skills", "skill_requirements", "merchant_inventories",
        "merchant_inventory_items", "merchant_price_multipliers", "resource_names", "levels", "objects",
        "object_graphics", "object_loot", "npc_names", "maps", "portals", "unknown40", "descriptions",
        "advanced_descriptions", "quests", "weapon_type_names", "weapon_material_names", "terrain",
        "unknown47", "upgrades", "item_sets",
    ]

    if cff_path is None:
        candidates = [
            WORKSPACE_ROOT / "OriginalGameFiles" / "data" / "GameData.cff",
            WORKSPACE_ROOT / "ModdedGameFiles" / "GameData.cff",
        ]
        cff_path = next((p for p in candidates if p.exists()), None)
        if cff_path is None:
            return {}

    try:
        with open(cff_path, "rb") as f:
            header = f.read(20)
            if len(header) < 20:
                return {}
            loc_body = None
            npc_body = None
            for name in tables_order:
                th = f.read(12)
                if len(th) < 12:
                    break
                size = int.from_bytes(th[6:10], "little", signed=False)
                body = f.read(size)
                if len(body) < size:
                    break
                if name == "localisation":
                    loc_body = body
                elif name == "npc_names":
                    npc_body = body
            if loc_body is None or npc_body is None:
                return {}

            # Parse localisation (row len 566)
            row_len_loc = 566
            en_texts: Dict[int, str] = {}
            de_texts: Dict[int, str] = {}
            rows = len(loc_body) // row_len_loc
            for i in range(rows):
                off = i * row_len_loc
                text_id = int.from_bytes(loc_body[off:off+2], "little", signed=False)
                language = loc_body[off+2]
                text = _decode_fixed_string(loc_body[off+54:off+566])
                if not text:
                    continue
                if language == 1:
                    en_texts[text_id] = text
                elif language == 0:
                    de_texts[text_id] = text

            # Parse npc_names (row len 6)
            row_len_npc = 6
            npc_rows = len(npc_body) // row_len_npc
            npc_map: Dict[int, str] = {}
            for i in range(npc_rows):
                off = i * row_len_npc
                npc_id = int.from_bytes(npc_body[off:off+4], "little", signed=False)
                name_id = int.from_bytes(npc_body[off+4:off+6], "little", signed=False)
                name = en_texts.get(name_id) or de_texts.get(name_id)
                if name:
                    npc_map[npc_id] = name
            return npc_map
    except Exception:
        return {}


def load_cff_localisation(lang: str = "de", cff_path: Optional[Path] = None) -> Dict[int, str]:
    """Return mapping of text_id -> localised text from CFF localisation table for the given language.
    Supported langs: 'de' (0), 'en' (1). Defaults to 'de'.
    """
    tables_order = [
        "spells", "spell_names", "unknown3", "creature_stats", "creature_skills", "hero_spells",
        "items", "armor", "item_installs", "weapons", "item_requirements", "item_effects", "item_ui",
        "spell_effects", "localisation", "races", "heads", "creatures", "creature_equipment",
        "creature_spells", "creature_resources", "drops", "unit_building_requirements", "buildings",
        "building_graphics", "building_requirements", "skills", "skill_requirements", "merchant_inventories",
        "merchant_inventory_items", "merchant_price_multipliers", "resource_names", "levels", "objects",
        "object_graphics", "object_loot", "npc_names", "maps", "portals", "unknown40", "descriptions",
        "advanced_descriptions", "quests", "weapon_type_names", "weapon_material_names", "terrain",
        "unknown47", "upgrades", "item_sets",
    ]

    if cff_path is None:
        candidates = [
            WORKSPACE_ROOT / "OriginalGameFiles" / "data" / "GameData.cff",
            WORKSPACE_ROOT / "ModdedGameFiles" / "GameData.cff",
        ]
        cff_path = next((p for p in candidates if p.exists()), None)
        if cff_path is None:
            return {}

    try:
        with open(cff_path, "rb") as f:
            header = f.read(20)
            if len(header) < 20:
                return {}
            loc_body = None
            for name in tables_order:
                th = f.read(12)
                if len(th) < 12:
                    break
                size = int.from_bytes(th[6:10], "little", signed=False)
                body = f.read(size)
                if len(body) < size:
                    break
                if name == "localisation":
                    loc_body = body
                    break
            if loc_body is None:
                return {}
            row_len_loc = 566
            texts: Dict[int, str] = {}
            lang_code = 0 if (lang or "de").lower() == "de" else 1
            rows = len(loc_body) // row_len_loc
            for i in range(rows):
                off = i * row_len_loc
                text_id = int.from_bytes(loc_body[off:off+2], "little", signed=False)
                language = loc_body[off+2]
                if language != lang_code:
                    continue
                text = _decode_fixed_string(loc_body[off+54:off+566])
                if text:
                    texts[text_id] = text
            return texts
    except Exception:
        return {}

def collect_taken_items_from_events() -> Dict[str, List[int]]:
    """Within each OnOneTimeEvent block, associate any TransferItem{TakeItem} with any SetRewardFlagTrue in the same block."""
    mapping: Dict[str, List[int]] = {}
    qstate_re = re.compile(r"QuestState\s*\{\s*QuestId\s*=\s*(\d+)\s*,\s*State\s*=\s*StateSolved\s*\}")
    flag_re = re.compile(r"SetRewardFlagTrue\s*\{\s*Name\s*=\s*\"([^\"]+)\"\s*\}")
    take_re = re.compile(r"TransferItem\s*\{[^}]*TakeItem\s*=\s*(\d+)[^}]*\}", re.S)

    for p in SCRIPT_DIR.rglob("*.lua"):
        if p.name == "GdsQuestRewards.lua":
            continue
        try:
            text = read_text(p)
        except Exception:
            continue

        idx = 0
        while True:
            pos = text.find("OnOneTimeEvent", idx)
            if pos == -1:
                break
            brace = text.find("{", pos)
            if brace == -1:
                idx = pos + 1
                continue
            try:
                end = find_matching_brace(text, brace)
            except Exception:
                idx = brace + 1
                continue
            block = text[brace:end+1]

            flags = [m.group(1) for m in flag_re.finditer(block)]
            taken = [int(x) for x in take_re.findall(block) if int(x) != 0]
            if flags and taken:
                for flg in flags:
                    lst = mapping.setdefault(flg, [])
                    for t in taken:
                        if t not in lst:
                            lst.append(t)
            idx = end + 1
    return mapping


# ---------- Guess quest giver NPC by scanning for QuestId appearances ----------

def guess_quest_giver_npc(quest_ids: List[int]) -> Dict[int, Optional[int]]:
    result: Dict[int, Optional[int]] = {qid: None for qid in quest_ids}
    if not quest_ids:
        return result

    # Pre-compile patterns for efficiency
    patt_by_qid: Dict[int, re.Pattern] = {qid: re.compile(rf"QuestId\s*=\s*{qid}(?!\d)") for qid in quest_ids}

    for path in SCRIPT_DIR.rglob("*.lua"):
        # ignore reward and variables main files
        if path.name in {"GdsQuestRewards.lua", "GdsVariables.lua"}:
            continue
        try:
            text = read_text(path)
        except Exception:
            continue
        for qid, patt in patt_by_qid.items():
            if result[qid] is not None:
                continue
            if patt.search(text):
                # infer npc from filename like n12345_*.lua
                m = re.match(r"n(\d+)", path.stem)
                if m and m.group(1) != "0":
                    result[qid] = int(m.group(1))
    return result


# ---------- Emit CSV and Markdown ----------

def write_csv(sections: List[Section], reward2qid: Dict[str, int], qid2giver: Dict[int, Optional[int]], qmeta: Dict[int, dict], npc_map: Dict[int, str], cff: Dict[int, dict], loc_map: Dict[int, str], lang: str):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "platform_id", "platform_name", "quest_flag", "quest_id", "quest_name", "quest_name_de", "quest_description_de", "quest_name_loc", "quest_description_loc", "quest_giver_npc_id", "quest_giver_name", "parent_quest_id", "parent_chain", "order_index", "quest_maps",
            "xp", "gold", "silver", "copper", "items_given", "items_taken",
        ])
        for sec in sorted(sections, key=lambda s: int(s["platform_id"])):
            pid = sec["platform_id"]
            pname = sec["platform_name"]
            for e in sec["entries"]:
                flag = e["flag"]
                qid = reward2qid.get(flag)
                giver = qid2giver.get(qid) if qid is not None else None
                giver_name = npc_map.get(giver, "") if giver is not None else ""
                qname = ""
                qname_de = ""
                qdesc_de = ""
                qname_loc = ""
                qdesc_loc = ""
                parent_qid = ""
                order_index = ""
                qmaps = ""
                if qid is not None and qid in qmeta:
                    meta = qmeta[qid]
                    # prefer German name via localisation
                    cff_rec = cff.get(qid) or {}
                    name_id = cff_rec.get("name_id") or (cff_rec.get("attributes") or {}).get("name_id")
                    if isinstance(name_id, int) and name_id in loc_map:
                        qname_loc = loc_map.get(name_id, "")
                    # Also try DE for explicit de column if current lang isn't de
                    # Note: we don't require both maps; de column may be empty in non-DE mode
                    # Fill qname_de only if lang is de and available via loc_map
                    if isinstance(name_id, int) and lang.lower() == "de" and name_id in loc_map:
                        qname_de = loc_map.get(name_id, "")
                    desc_id = cff_rec.get("description_id") or (cff_rec.get("attributes") or {}).get("description_id")
                    if isinstance(desc_id, int) and desc_id in loc_map:
                        qdesc_loc = loc_map.get(desc_id, "")
                    if isinstance(desc_id, int) and lang.lower() == "de" and desc_id in loc_map:
                        qdesc_de = loc_map.get(desc_id, "")
                    # fallback to meta name
                    qname = (qname_loc or qname_de) or meta.get("name") or meta.get("quest_name") or ""
                    # parent / order
                    attrs = cff_rec.get("attributes") or {}
                    p1 = attrs.get("parent_quest_id")
                    p2 = cff_rec.get("parent_id")
                    oi = attrs.get("order_index")
                    if isinstance(p1, int) and p1:
                        parent_qid = p1
                    elif isinstance(p2, int) and p2:
                        parent_qid = p2
                    if isinstance(oi, int):
                        order_index = oi
                    maps = meta.get("maps") or []
                    if isinstance(maps, list):
                        codes = [m.get("code") for m in maps if isinstance(m, dict) and m.get("code")]
                        qmaps = "|".join(codes)
                items_given = "|".join(str(x) for x in e["items_given"]) if e["items_given"] else ""
                items_taken = "|".join(str(x) for x in e["items_taken"]) if e["items_taken"] else ""
                parent_chain = ""
                if isinstance(qid, int):
                    chain_ids = build_parent_chain(qid, cff)
                    if chain_ids:
                        parts = []
                        for pid in chain_ids:
                            nm = resolve_quest_name(pid, cff, loc_map, qmeta)
                            parts.append(f"{pid} ({nm})" if nm else str(pid))
                        parent_chain = ">".join(parts)
                w.writerow([
                    pid, pname, flag, qid if qid is not None else "",
                    qname, qname_de, qdesc_de, qname_loc, qdesc_loc,
                    giver if giver is not None else "",
                    giver_name,
                    parent_qid, parent_chain, order_index,
                    qmaps,
                    e["xp"] if e["xp"] is not None else "",
                    e["gold"], e["silver"], e["copper"],
                    items_given, items_taken,
                ])


def write_md(sections: List[Section], reward2qid: Dict[str, int], qid2giver: Dict[int, Optional[int]], qmeta: Dict[int, dict], npc_map: Dict[int, str], cff: Dict[int, dict], loc_map: Dict[int, str], lang: str):
    lines: List[str] = []
    lines.append("# Quest Rewards by Platform/Map")
    lines.append("")
    lines.append("Generated from GdsQuestRewards.lua with integration from src/TirganachReloaded/data (quest IDs, names, maps). Items are marked as given; taken list populated where detected in scripts.")
    lines.append("")

    for sec in sorted(sections, key=lambda s: int(s["platform_id"])):
        pid = sec["platform_id"]
        pname = sec["platform_name"]
        lines.append(f"## {pname} (P{pid})")
        lines.append("")
        lang_label = lang.upper()
        lines.append(f"| Quest/Subquest Flag | Quest ID | Quest Name ({lang_label}) | Description ({lang_label}) | Quest Giver | Parent QID | Parent Chain | Order | Maps | XP | Gold | Silver | Copper | Items |")
        lines.append("|---|---:|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---|")
        for e in sec["entries"]:
            flag = e["flag"]
            qid = reward2qid.get(flag)
            giver = qid2giver.get(qid) if qid is not None else None
            giver_name = npc_map.get(giver, "") if giver is not None else ""
            qname_loc = ""
            qdesc_loc = ""
            parent_qid = ""
            parent_chain = ""
            order_index = ""
            qmaps = ""
            if qid is not None and qid in qmeta:
                meta = qmeta[qid]
                cff_rec = cff.get(qid) or {}
                name_id = cff_rec.get("name_id") or (cff_rec.get("attributes") or {}).get("name_id")
                if isinstance(name_id, int) and name_id in loc_map:
                    qname_loc = loc_map.get(name_id, "")
                desc_id = cff_rec.get("description_id") or (cff_rec.get("attributes") or {}).get("description_id")
                if isinstance(desc_id, int) and desc_id in loc_map:
                    qdesc_loc = loc_map.get(desc_id, "")
                if not qname_loc:
                    qname_loc = meta.get("name") or meta.get("quest_name") or ""
                attrs = cff_rec.get("attributes") or {}
                p1 = attrs.get("parent_quest_id")
                p2 = cff_rec.get("parent_id")
                oi = attrs.get("order_index")
                if isinstance(p1, int) and p1:
                    parent_qid = p1
                elif isinstance(p2, int) and p2:
                    parent_qid = p2
                # build parent chain
                if isinstance(qid, int):
                    chain_ids = build_parent_chain(qid, cff)
                    if chain_ids:
                        parts = []
                        for pid in chain_ids:
                            nm = resolve_quest_name(pid, cff, loc_map, qmeta)
                            parts.append(f"{pid} ({nm})" if nm else str(pid))
                        parent_chain = " > ".join(parts)
                if isinstance(oi, int):
                    order_index = oi
                maps = meta.get("maps") or []
                if isinstance(maps, list):
                    codes = [m.get("code") for m in maps if isinstance(m, dict) and m.get("code")]
                    qmaps = ", ".join(codes)
            parts: List[str] = []
            if e["items_given"]:
                parts.extend(f"{x} (given)" for x in e["items_given"]) 
            if e["items_taken"]:
                parts.extend(f"{x} (taken)" for x in e["items_taken"]) 
            items = ", ".join(parts)
            xp = e["xp"] if e["xp"] is not None else ""
            giver_cell = (
                f"{giver_name} ({giver})" if giver is not None and giver_name else (
                    str(giver) if giver is not None else ""
                )
            )
            lines.append(
                f"| {flag} | {qid if qid is not None else ''} | {qname_loc} | {qdesc_loc} | {giver_cell} | {parent_qid} | {parent_chain} | {order_index} | {qmaps} | {xp} | {e['gold']} | {e['silver']} | {e['copper']} | {items} |")
        lines.append("")

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args():
    ap = argparse.ArgumentParser(description="Generate quest rewards tables from Lua and CFF data")
    ap.add_argument("--lang", choices=["de", "en"], default="de", help="Localisation language for matching and display")
    return ap.parse_args()


def main():
    args = parse_args()
    text = read_text(REWARDS_LUA)
    sections = parse_rewards_file(text)

    reward2qid = collect_reward_to_questid()
    # Merge with event-block mappings (does not overwrite existing unless missing)
    evt_map = collect_reward_to_questid_from_events()
    for flg, qid in evt_map.items():
        reward2qid.setdefault(flg, qid)
    # detect taken items: prefer event-block mapping, then fallback to window-based
    flag2taken_evt = collect_taken_items_from_events()
    flag2taken_win = find_taken_items_for_flags()
    flag2taken = dict(flag2taken_evt)
    for k, v in flag2taken_win.items():
        flag2taken.setdefault(k, v)
    annotate_taken_items(sections, flag2taken)

    # Integrate external mappings and metadata
    ext_map = load_external_flag_to_qid_mappings()
    for flg, qid in ext_map.items():
        reward2qid.setdefault(flg, qid)
    complete = load_quest_rewards_complete()
    integrate_rewards_complete(sections, reward2qid, complete)
    qmeta = load_quest_maps_and_names()
    # Dynamic text-based matching to fill remaining flags (prefer selected localisation)
    cff = load_cff_quest_data()
    loc_map = load_cff_localisation(args.lang)
    augment_reward2qid_with_text_matching(sections, reward2qid, qmeta, cff, loc_map)
    qids = sorted(set(reward2qid.values()))
    qid2giver = guess_quest_giver_npc(qids)
    npc_map = load_cff_npc_map()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(sections, reward2qid, qid2giver, qmeta, npc_map, cff, loc_map, args.lang)
    write_md(sections, reward2qid, qid2giver, qmeta, npc_map, cff, loc_map, args.lang)

    print(f"Parsed sections: {len(sections)}")
    total_entries = sum(len(s['entries']) for s in sections)
    print(f"Total rewards: {total_entries}")
    print(f"Quest IDs mapped: {len(reward2qid)}")
    print(f"CSV: {CSV_PATH}")
    print(f"MD:  {MD_PATH}")


if __name__ == "__main__":
    main()
