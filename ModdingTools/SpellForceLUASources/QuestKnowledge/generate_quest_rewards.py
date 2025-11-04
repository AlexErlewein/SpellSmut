#!/usr/bin/env python3
from __future__ import annotations
import re
import os
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "script"
REWARDS_LUA = SCRIPT_DIR / "GdsQuestRewards.lua"
OUT_DIR = ROOT / "QuestKnowledge"
CSV_PATH = OUT_DIR / "QuestRewards.csv"
MD_PATH = OUT_DIR / "QuestRewards.md"

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

def write_csv(sections: List[Section], reward2qid: Dict[str, int], qid2giver: Dict[int, Optional[int]]):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "platform_id", "platform_name", "quest_flag", "quest_id", "quest_giver_npc_id",
            "xp", "gold", "silver", "copper", "items_given", "items_taken",
        ])
        for sec in sorted(sections, key=lambda s: int(s["platform_id"])):
            pid = sec["platform_id"]
            pname = sec["platform_name"]
            for e in sec["entries"]:
                flag = e["flag"]
                qid = reward2qid.get(flag)
                giver = qid2giver.get(qid) if qid is not None else None
                items_given = "|".join(str(x) for x in e["items_given"]) if e["items_given"] else ""
                items_taken = "|".join(str(x) for x in e["items_taken"]) if e["items_taken"] else ""
                w.writerow([
                    pid, pname, flag, qid if qid is not None else "",
                    giver if giver is not None else "",
                    e["xp"] if e["xp"] is not None else "",
                    e["gold"], e["silver"], e["copper"],
                    items_given, items_taken,
                ])


def write_md(sections: List[Section], reward2qid: Dict[str, int], qid2giver: Dict[int, Optional[int]]):
    lines: List[str] = []
    lines.append("# Quest Rewards by Platform/Map")
    lines.append("")
    lines.append("Generated from GdsQuestRewards.lua. Items are marked as given; taken list will be populated if found in future passes.")
    lines.append("")

    for sec in sorted(sections, key=lambda s: int(s["platform_id"])):
        pid = sec["platform_id"]
        pname = sec["platform_name"]
        lines.append(f"## {pname} (P{pid})")
        lines.append("")
        lines.append("| Quest/Subquest Flag | Quest ID | Quest Giver NPC | XP | Gold | Silver | Copper | Items |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
        for e in sec["entries"]:
            flag = e["flag"]
            qid = reward2qid.get(flag)
            giver = qid2giver.get(qid) if qid is not None else None
            parts: List[str] = []
            if e["items_given"]:
                parts.extend(f"{x} (given)" for x in e["items_given"]) 
            if e["items_taken"]:
                parts.extend(f"{x} (taken)" for x in e["items_taken"]) 
            items = ", ".join(parts)
            xp = e["xp"] if e["xp"] is not None else ""
            lines.append(
                f"| {flag} | {qid if qid is not None else ''} | {giver if giver is not None else ''} | {xp} | {e['gold']} | {e['silver']} | {e['copper']} | {items} |")
        lines.append("")

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
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
    qids = sorted(set(reward2qid.values()))
    qid2giver = guess_quest_giver_npc(qids)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(sections, reward2qid, qid2giver)
    write_md(sections, reward2qid, qid2giver)

    print(f"Parsed sections: {len(sections)}")
    total_entries = sum(len(s['entries']) for s in sections)
    print(f"Total rewards: {total_entries}")
    print(f"Quest IDs mapped: {len(reward2qid)}")
    print(f"CSV: {CSV_PATH}")
    print(f"MD:  {MD_PATH}")


if __name__ == "__main__":
    main()
