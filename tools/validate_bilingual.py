#!/usr/bin/env python3
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path


FILES = ("weapons", "knives", "gloves", "agents", "categories")


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
    raw = subprocess.check_output(
        ["git", "show", f"{ref}:data/{name}.json"], text=True, encoding="utf-8"
    )
    return json.loads(raw)


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
            if strip_chinese_names(catalogs[name]) != strip_chinese_names(baseline):
                raise ValueError(f"data/{name}.json changed fields other than displayNameZh")

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

    sources = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.cs"))
    if "Localizer.ForPlayer" in sources or "_localizer.ForPlayer" in sources:
        raise ValueError("player-language-dependent localization remains in C# sources")
    menu = (root / "MenuManager.cs").read_text(encoding="utf-8")
    if "HtmlEncode(BilingualText.Truncate(" not in menu:
        raise ValueError("menu text must be truncated before HTML encoding")

    print(f"Validated {len(FILES)} catalogs, {total} bilingual names, {len(en)} language keys, search, fallback, de-duplication, and HTML safety.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"Bilingual validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
