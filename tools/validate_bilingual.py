#!/usr/bin/env python3
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path


FILES = ("weapons", "knives", "gloves", "agents", "categories", "music_kits")


def combine(chinese, english):
    en = (english or "").strip()
    zh = (chinese or en).strip()
    if zh.casefold() == en.casefold():
        return zh
    return f"{zh} / {en}" if en else zh


def strip_chinese_names(value):
    if isinstance(value, list):
        return [strip_chinese_names(item) for item in value]
    if isinstance(value, dict):
        return {key: strip_chinese_names(item) for key, item in value.items() if key != "displayNameZh"}
    return value


def load_ref(ref, name):
    path = f"{ref}:data/{name}.json"
    if subprocess.run(
        ["git", "cat-file", "-e", path], capture_output=True, check=False
    ).returncode != 0:
        return None
    raw = subprocess.check_output(["git", "show", path], text=True, encoding="utf-8")
    return json.loads(raw)


def validate_existing_entries_unchanged(current, baseline, name):
    identity_key = "entityName" if name == "weapons" else "id"
    current_by_id = {str(entry[identity_key]): entry for entry in current}
    baseline_by_id = {str(entry[identity_key]): entry for entry in baseline}
    missing = sorted(set(baseline_by_id) - set(current_by_id))
    if missing:
        raise ValueError(f"data/{name}.json removed baseline entries: {missing}")
    for entry_id, baseline_entry in baseline_by_id.items():
        if strip_chinese_names(current_by_id[entry_id]) != strip_chinese_names(baseline_entry):
            raise ValueError(f"data/{name}.json changed stable fields for {entry_id}")


def readme_structure(lines):
    result = []
    for line in lines:
        if not line:
            result.append("blank")
        elif line.startswith("#"):
            match = re.match(r"^(#+) (\S+)", line)
            result.append(("heading", match.group(1), match.group(2)) if match else ("heading", "invalid"))
        elif line.startswith("```"):
            result.append(("fence", line))
        elif line.startswith("| ---"):
            result.append(("table", line))
        elif line.startswith("> **["):
            result.append("language-link")
        else:
            result.append("content")
    return result


def validate_named_entry(entry, owner, seen):
    english = entry.get("displayName")
    chinese = entry.get("displayNameZh")
    if not isinstance(english, str) or not english.strip():
        raise ValueError(f"{owner}: displayName is required")
    if not isinstance(chinese, str) or not chinese.strip():
        raise ValueError(f"{owner}: displayNameZh is required")
    entry_id = entry.get("id") or entry.get("entityName")
    if not entry_id:
        raise ValueError(f"{owner}: stable id/entityName is required")
    if entry_id in seen:
        raise ValueError(f"{owner}: duplicate id {entry_id}")
    seen.add(entry_id)


def main():
    parser = argparse.ArgumentParser(description="Validate AstraSkins bilingual definitions and UI wiring.")
    parser.add_argument("--data", default="data")
    parser.add_argument("--baseline-ref", help="Git ref whose stable JSON fields must remain unchanged.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data_dir = root / args.data

    catalogs = {}
    total = 0
    for name in FILES:
        path = data_dir / f"{name}.json"
        catalogs[name] = json.loads(path.read_text(encoding="utf-8"))
        seen = set()
        for index, entry in enumerate(catalogs[name]):
            validate_named_entry(entry, f"{name}[{index}]", seen)
            skin_seen = set()
            for skin_index, skin in enumerate(entry.get("skins", [])):
                validate_named_entry(skin, f"{name}[{index}].skins[{skin_index}]", skin_seen)
                total += 1
            total += 1
        if args.baseline_ref:
            baseline = load_ref(args.baseline_ref, name)
            if baseline is not None:
                validate_existing_entries_unchanged(catalogs[name], baseline, name)

    weapons = catalogs["weapons"]
    if len(weapons) != 35:
        raise ValueError(f"expected 35 weapons, found {len(weapons)}")
    weapon_skin_count = sum(len(weapon.get("skins", [])) for weapon in weapons)
    if weapon_skin_count != 1456:
        raise ValueError(f"expected 1456 weapon skins, found {weapon_skin_count}")

    categories = {entry["id"]: entry for entry in catalogs["categories"]}
    taser_category = categories.get("taser")
    if taser_category is None or combine(taser_category.get("displayNameZh"), taser_category.get("displayName")) != "电击枪 / Zeus x27":
        raise ValueError("Zeus x27 category is missing or not bilingual")

    taser = next((weapon for weapon in weapons if weapon["entityName"] == "weapon_taser"), None)
    if taser is None or taser.get("category") != "taser":
        raise ValueError("weapon_taser is missing or linked to the wrong category")
    if combine(taser.get("displayNameZh"), taser.get("displayName")) != "宙斯x27电击枪 / Zeus x27":
        raise ValueError("weapon_taser name is missing or not bilingual")

    expected_taser_skins = {
        1205: ("充电宝", "Charged Up"),
        292: ("鼾龙传说", "Dragon Snore"),
        1382: ("大地曼陀罗", "Earth Mandala"),
        1268: ("电光幽蓝", "Electric Blue"),
        1172: ("奥林匹斯", "Olympus"),
        1297: ("沼泽DDPAT", "Swamp DDPAT"),
        1183: ("当岁鱼", "Tosai"),
    }
    taser_skins = {skin.get("paintKit"): skin for skin in taser.get("skins", [])}
    if set(taser_skins) != set(expected_taser_skins):
        raise ValueError(f"unexpected Zeus x27 paint kits: {sorted(taser_skins)}")
    for paint_kit, (chinese, english) in expected_taser_skins.items():
        skin = taser_skins[paint_kit]
        if (skin.get("displayNameZh"), skin.get("displayName")) != (chinese, english):
            raise ValueError(f"Zeus x27 paint kit {paint_kit} has an unexpected name")
        if skin.get("seed") != 0 or skin.get("wear") != 0.0001 or skin.get("legacyModel") is not False:
            raise ValueError(f"Zeus x27 paint kit {paint_kit} has unexpected defaults")

    music_kits = catalogs["music_kits"]
    if len(music_kits) != 92:
        raise ValueError(f"expected 92 music kits, found {len(music_kits)}")
    if any(not isinstance(kit.get("musicKit"), int) or kit["musicKit"] <= 0 for kit in music_kits):
        raise ValueError("music kits must have a positive integer musicKit value")
    if len({kit["musicKit"] for kit in music_kits}) != len(music_kits):
        raise ValueError("musicKit values must be unique")

    en = json.loads((root / "lang" / "en.json").read_text(encoding="utf-8"))
    zh = json.loads((root / "lang" / "zh.json").read_text(encoding="utf-8"))
    if set(en) != set(zh):
        raise ValueError(f"en/zh language key mismatch: {sorted(set(en) ^ set(zh))}")

    if combine("AWP", "AWP") != "AWP" or combine("", "Fallback") != "Fallback":
        raise ValueError("bilingual same-name de-duplication or fallback is broken")
    if combine("二西莫夫", "Asiimov") != "二西莫夫 / Asiimov":
        raise ValueError("bilingual ordering or separator is broken")
    if html.escape("<font>测试 & test</font>") != "&lt;font&gt;测试 &amp; test&lt;/font&gt;":
        raise ValueError("HTML escaping smoke test failed")

    searchable = [
        f"{entry['displayNameZh']} {entry['displayName']} {skin['displayNameZh']} {skin['displayName']}".casefold()
        for entry in catalogs["weapons"]
        for skin in entry.get("skins", [])
    ]
    if not any("秋叶原" in value for value in searchable) or not any("akihabara" in value for value in searchable):
        raise ValueError("Chinese/English search index smoke test failed")
    taser_searchable = [value for value in searchable if "zeus x27" in value or "宙斯x27电击枪" in value]
    if not any("olympus" in value for value in taser_searchable) or not any("奥林匹斯" in value for value in taser_searchable):
        raise ValueError("Zeus x27 Chinese/English search index smoke test failed")

    source_dir = root / "src" / "AstraSkins"
    sources = "\n".join(path.read_text(encoding="utf-8") for path in source_dir.rglob("*.cs"))
    if "Localizer.ForPlayer" in sources or "_localizer.ForPlayer" in sources:
        raise ValueError("player-language-dependent localization remains in C# sources")
    menu = (source_dir / "MenuManager.cs").read_text(encoding="utf-8")
    if "HtmlEncode(BilingualText.Truncate(" not in menu:
        raise ValueError("menu text must be truncated before HTML encoding")
    if "BilingualText.DisplayWidth(prefix)" not in menu or "TextElementWidth" not in sources:
        raise ValueError("wide-character-aware menu truncation is not wired")
    if "音乐盒 music music kit" not in menu or "SetMusicKit(current, kitId)" not in menu:
        raise ValueError("music kit Chinese/English search is not wired")
    if ".Where(weapon => !weapon.EntityName.Equals(TaserEntity" not in menu:
        raise ValueError("owned Zeus x27 must not duplicate the fixed main-menu entry")
    if "WeaponsByEntity.TryGetValue(TaserEntity" not in menu:
        raise ValueError("fixed Zeus x27 main-menu entry is not wired")
    skin_manager = (source_dir / "SkinManager.cs").read_text(encoding="utf-8")
    if 'return "slot11";' not in skin_manager:
        raise ValueError("Zeus x27 must refresh through slot11")
    taser_refresh_requirements = [
        'RefreshOwnedTaserWithSelection(player, oldWeapon, skin, wasActive, logFailures)',
        "pawn.RemovePlayerItem(oldWeapon);",
        "oldWeapon.Remove();",
        'GiveNamedItem<CWeaponTaser>("weapon_taser")',
        "oldTaser.FireTime,",
        "oldTaser.LastAttackTick,",
        "oldTaser.NextPrimaryAttackTick,",
        "NextTaserRefreshGeneration(steamId)",
        "RestoreTaserState(newTaser, state);",
    ]
    missing_taser_refresh = [value for value in taser_refresh_requirements if value not in skin_manager]
    if missing_taser_refresh:
        raise ValueError(f"Zeus x27 entity rebuild/state restoration is incomplete: {missing_taser_refresh}")
    plugin = (source_dir / "AstraSkinsPlugin.cs").read_text(encoding="utf-8")
    if 'ModuleVersion => "1.2.1"' not in plugin:
        raise ValueError("ModuleVersion must be 1.2.1")

    readme_zh = (root / "README.md").read_text(encoding="utf-8").splitlines()
    readme_en = (root / "README.en-us.md").read_text(encoding="utf-8").splitlines()
    if len(readme_zh) != len(readme_en):
        raise ValueError(f"README line count mismatch: zh={len(readme_zh)}, en={len(readme_en)}")
    if readme_structure(readme_zh) != readme_structure(readme_en):
        raise ValueError("README heading, fence, table, blank-line, or language-link structure mismatch")

    attributes = (root / ".gitattributes").read_text(encoding="utf-8")
    if "*.md linguist-language=Markdown linguist-detectable=true linguist-documentation=false" not in attributes or "README*.md linguist-language=Markdown" not in attributes:
        raise ValueError("both READMEs must be included in GitHub language statistics")
    if "*.json linguist-detectable=false" not in attributes:
        raise ValueError("JSON data files must be excluded from GitHub language statistics")

    print(f"Validated {len(FILES)} catalogs, {total} bilingual names, {len(en)} language keys, search, truncation, README parity, fallback, de-duplication, and HTML safety.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"Bilingual validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
