#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen

ITEMS_GAME_URL = "https://raw.githubusercontent.com/SteamDatabase/GameTracking-CS2/master/game/csgo/pak01_dir/scripts/items/items_game.txt"
CSGO_ENGLISH_URL = "https://raw.githubusercontent.com/SteamDatabase/GameTracking-CS2/master/game/csgo/pak01_dir/resource/csgo_english.txt"
SKINS_API_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/skins.json"
AGENTS_API_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/agents.json"
SKINS_API_ZH_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/skins.json"
AGENTS_API_ZH_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/agents.json"
MUSIC_KITS_API_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/music_kits.json"
MUSIC_KITS_ZH_API_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/music_kits.json"

WEAPON_DISPLAY = {
    "weapon_ak47": ("rifles", "AK-47"),
    "weapon_aug": ("rifles", "AUG"),
    "weapon_awp": ("rifles", "AWP"),
    "weapon_famas": ("rifles", "FAMAS"),
    "weapon_g3sg1": ("rifles", "G3SG1"),
    "weapon_galilar": ("rifles", "Galil AR"),
    "weapon_m4a1": ("rifles", "M4A4"),
    "weapon_m4a1_silencer": ("rifles", "M4A1-S"),
    "weapon_scar20": ("rifles", "SCAR-20"),
    "weapon_sg556": ("rifles", "SG 553"),
    "weapon_ssg08": ("rifles", "SSG 08"),
    "weapon_bizon": ("smgs", "PP-Bizon"),
    "weapon_mac10": ("smgs", "MAC-10"),
    "weapon_mp5sd": ("smgs", "MP5-SD"),
    "weapon_mp7": ("smgs", "MP7"),
    "weapon_mp9": ("smgs", "MP9"),
    "weapon_p90": ("smgs", "P90"),
    "weapon_ump45": ("smgs", "UMP-45"),
    "weapon_mag7": ("heavy", "MAG-7"),
    "weapon_m249": ("heavy", "M249"),
    "weapon_negev": ("heavy", "Negev"),
    "weapon_nova": ("heavy", "Nova"),
    "weapon_sawedoff": ("heavy", "Sawed-Off"),
    "weapon_xm1014": ("heavy", "XM1014"),
    "weapon_deagle": ("pistols", "Desert Eagle"),
    "weapon_elite": ("pistols", "Dual Berettas"),
    "weapon_fiveseven": ("pistols", "Five-SeveN"),
    "weapon_glock": ("pistols", "Glock-18"),
    "weapon_hkp2000": ("pistols", "P2000"),
    "weapon_usp_silencer": ("pistols", "USP-S"),
    "weapon_p250": ("pistols", "P250"),
    "weapon_cz75a": ("pistols", "CZ75-Auto"),
    "weapon_revolver": ("pistols", "R8 Revolver"),
    "weapon_tec9": ("pistols", "Tec-9"),
    "weapon_taser": ("taser", "Zeus x27"),
}

WEAPON_DISPLAY_ZH = {
    "weapon_taser": "宙斯x27电击枪",
}

CATEGORIES = [
    {"id": "pistols", "displayName": "Pistols", "displayNameZh": "手枪", "order": 10, "enabled": True},
    {"id": "smgs", "displayName": "SMGs", "displayNameZh": "冲锋枪", "order": 20, "enabled": True},
    {"id": "rifles", "displayName": "Rifles", "displayNameZh": "步枪", "order": 30, "enabled": True},
    {"id": "heavy", "displayName": "Heavy", "displayNameZh": "重型武器", "order": 40, "enabled": True},
    {"id": "taser", "displayName": "Zeus x27", "displayNameZh": "电击枪", "order": 50, "enabled": True},
]


class VdfParser:
    def __init__(self, text):
        self.tokens = re.findall(r'"(?:\\.|[^"])*"|[{}]', self._strip_comments(text))
        self.index = 0

    def parse(self):
        result = {}
        while self.index < len(self.tokens):
            key = self._read_string()
            if key is None:
                break
            value = self._read_value()
            result[key] = self._merge(result.get(key), value)
        return result

    def _read_value(self):
        if self.index < len(self.tokens) and self.tokens[self.index] == "{":
            self.index += 1
            obj = {}
            while self.index < len(self.tokens) and self.tokens[self.index] != "}":
                key = self._read_string()
                if key is None:
                    break
                value = self._read_value()
                obj[key] = self._merge(obj.get(key), value)
            if self.index < len(self.tokens) and self.tokens[self.index] == "}":
                self.index += 1
            return obj
        return self._read_string() or ""

    def _read_string(self):
        if self.index >= len(self.tokens):
            return None
        token = self.tokens[self.index]
        self.index += 1
        if token in "{}":
            return None
        escapes = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}
        return re.sub(r"\\(.)", lambda match: escapes.get(match.group(1), match.group(1)), token[1:-1])

    @staticmethod
    def _merge(previous, value):
        if previous is None:
            return value
        if isinstance(previous, list):
            previous.append(value)
            return previous
        return [previous, value]

    @staticmethod
    def _strip_comments(text):
        return re.sub(r"//.*", "", text)


def load_text(path_or_url):
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        with urlopen(path_or_url, timeout=60) as response:
            return response.read().decode("utf-8", errors="replace")
    return Path(path_or_url).read_text(encoding="utf-8", errors="replace")


def localize(token, translations):
    if not token:
        return ""
    key = token[1:].lower() if token.startswith("#") else token.lower()
    return translations.get(key, token.lstrip("#"))


def parse_translations(text):
    parsed = VdfParser(text).parse()
    language = parsed.get("lang", {}).get("Tokens", {})
    return {k.lower(): v for k, v in language.items()} if isinstance(language, dict) else {}


def find_items_root(parsed):
    return parsed.get("items_game", parsed)


def as_dict(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        merged = {}
        for entry in value:
            if isinstance(entry, dict):
                merged.update(entry)
        return merged
    return {}


def collect_weapon_paint_links(root):
    links = {weapon: set() for weapon in WEAPON_DISPLAY}
    item_sets = as_dict(root.get("item_sets", {}))

    for item_set in item_sets.values():
        if not isinstance(item_set, dict):
            continue
        items = item_set.get("items", {})
        if not isinstance(items, dict):
            continue
        for key in items.keys():
            match = re.match(r"\[([^\]]+)\](weapon_[a-z0-9_]+)$", key)
            if not match:
                continue
            paint_name, weapon = match.group(1), match.group(2)
            if weapon in links:
                links[weapon].add(paint_name)
    return links


def build_weapons(root, translations, api_skins=None):
    if api_skins:
        return build_weapons_from_api(api_skins)

    paint_kits = as_dict(root.get("paint_kits", {}))
    rarities = as_dict(root.get("paint_kits_rarity", {}))
    links = collect_weapon_paint_links(root)
    paint_by_name = {}
    for paint_id, paint in paint_kits.items():
        if isinstance(paint, dict) and paint_id.isdigit():
            name = paint.get("name")
            if name:
                paint_by_name[name] = (int(paint_id), paint)

    weapons = []
    for entity, (category, display) in WEAPON_DISPLAY.items():
        skins = []
        for paint_name in sorted(links.get(entity, [])):
            found = paint_by_name.get(paint_name)
            if not found:
                continue
            paint_id, paint = found
            skin_name = localize(paint.get("description_tag", paint_name), translations)
            cosmetic_id = f"{entity}:{paint_id}"
            skins.append({
                "id": cosmetic_id,
                "displayName": skin_name,
                "paintKit": paint_id,
                "seed": 0,
                "wear": 0.0001,
                "enabled": True,
                "rarity": rarities.get(paint_name),
            })
        weapons.append({
            "entityName": entity,
            "displayName": display,
            "category": category,
            "enabled": True,
            "skins": skins,
        })
    return weapons


def build_weapons_from_api(api_skins):
    grouped = {entity: [] for entity in WEAPON_DISPLAY}
    for skin in api_skins:
        weapon = skin.get("weapon", {})
        entity = weapon.get("id")
        paint_index = skin.get("paint_index")
        if entity not in grouped or paint_index is None:
            continue
        category = skin.get("category", {})
        pattern = skin.get("pattern", {})
        rarity = skin.get("rarity", {})
        grouped[entity].append({
            "id": f"{entity}:{paint_index}",
            "displayName": pattern.get("name") or skin.get("name", "").split("|")[-1].strip(),
            "paintKit": int(paint_index),
            "seed": 0,
            "wear": float(skin.get("min_float") or 0.0001),
            "legacyModel": bool(skin.get("legacy_model", False)),
            "enabled": True,
            "rarity": rarity.get("id") or category.get("id"),
        })

    weapons = []
    for entity, (category, display) in WEAPON_DISPLAY.items():
        skins = sorted(unique_by_id(grouped[entity]), key=lambda x: x["displayName"])
        weapons.append({
            "entityName": entity,
            "displayName": display,
            "category": category,
            "enabled": True,
            "skins": skins,
        })
    return weapons


def collect_items(root):
    return as_dict(root.get("items", {}))


def build_knives(root, translations, api_skins=None):
    if api_skins:
        return build_knives_from_api(root, translations, api_skins)

    paint_kits = as_dict(root.get("paint_kits", {}))
    knives = []
    for item_id, item in collect_items(root).items():
        if not item_id.isdigit() or not isinstance(item, dict):
            continue
        name = item.get("name", "")
        prefab = item.get("prefab", "")
        if "knife" not in name and "melee" not in prefab:
            continue
        if name == "weapon_knife":
            continue
        display = localize(item.get("item_name", name), translations)
        skins = []
        for paint_id, paint in paint_kits.items():
            if paint_id.isdigit() and isinstance(paint, dict):
                paint_name = localize(paint.get("description_tag", paint.get("name", paint_id)), translations)
                skins.append({
                    "id": f"{name}:{paint_id}",
                    "displayName": paint_name,
                    "paintKit": int(paint_id),
                    "seed": 0,
                    "wear": 0.0001,
                    "itemDefinitionIndex": int(item_id),
                    "enabled": True,
                })
        knives.append({
            "id": name,
            "displayName": display,
            "entityName": name,
            "itemDefinitionIndex": int(item_id),
            "enabled": True,
            "skins": skins,
        })
    return sorted(knives, key=lambda x: x["displayName"])


def build_knives_from_api(root, translations, api_skins):
    items = collect_items(root)
    api_knife_weapon_ids = {
        skin.get("weapon", {}).get("weapon_id")
        for skin in api_skins
        if skin.get("paint_index") is not None
        and (
            str(skin.get("weapon", {}).get("id", "")).startswith("weapon_knife")
            or str(skin.get("weapon", {}).get("id", "")) == "weapon_bayonet"
        )
    }
    knife_items = {
        int(item_id): item
        for item_id, item in items.items()
        if item_id.isdigit()
        and isinstance(item, dict)
        and int(item_id) in api_knife_weapon_ids
        and item.get("name") != "weapon_knife"
    }
    grouped = {item_id: [] for item_id in knife_items}
    for skin in api_skins:
        weapon = skin.get("weapon", {})
        weapon_id = weapon.get("weapon_id")
        paint_index = skin.get("paint_index")
        if weapon_id not in grouped or paint_index is None:
            continue
        pattern = skin.get("pattern", {})
        rarity = skin.get("rarity", {})
        entity = knife_items[weapon_id].get("name")
        grouped[weapon_id].append({
            "id": f"{entity}:{paint_index}",
            "displayName": pattern.get("name") or skin.get("name", "").split("|")[-1].strip(),
            "paintKit": int(paint_index),
            "seed": 0,
            "wear": float(skin.get("min_float") or 0.0001),
            "itemDefinitionIndex": int(weapon_id),
            "legacyModel": bool(skin.get("legacy_model", False)),
            "enabled": True,
            "rarity": rarity.get("id"),
        })

    knives = []
    for item_id, item in knife_items.items():
        name = item.get("name", "")
        display = localize(item.get("item_name", name), translations)
        skins = [{
            "id": f"{name}:0",
            "displayName": "Vanilla",
            "paintKit": 0,
            "seed": 0,
            "wear": 0.0001,
            "itemDefinitionIndex": int(item_id),
            "legacyModel": False,
            "enabled": True,
        }]
        skins.extend(sorted(unique_by_id(grouped.get(item_id, [])), key=lambda x: (x["displayName"], x["paintKit"])))
        knives.append({
            "id": name,
            "displayName": display,
            "entityName": name,
            "itemDefinitionIndex": int(item_id),
            "enabled": True,
            "skins": skins,
        })
    return sorted(knives, key=lambda x: x["displayName"])


def build_gloves(root, translations, api_skins=None):
    if api_skins:
        return build_gloves_from_api(root, translations, api_skins)

    paint_kits = as_dict(root.get("paint_kits", {}))
    gloves = []
    for item_id, item in collect_items(root).items():
        if not item_id.isdigit() or not isinstance(item, dict):
            continue
        name = item.get("name", "")
        prefab = item.get("prefab", "")
        if "glove" not in name and "hands" not in prefab:
            continue
        display = localize(item.get("item_name", name), translations)
        skins = []
        if item.get("prefab") != "hands_paintable":
            continue
        family = glove_family_for_item(name)
        if not family:
            continue
        for paint_id, paint in paint_kits.items():
            if not paint_id.isdigit() or not isinstance(paint, dict):
                continue
            if glove_family_for_paint(paint) != family:
                continue
            paint_name = localize(paint.get("description_tag", paint.get("name", paint_id)), translations)
            skins.append({
                "id": f"{name}:{paint_id}",
                "displayName": paint_name,
                "paintKit": int(paint_id),
                "seed": 0,
                "wear": 0.0001,
                "itemDefinitionIndex": int(item_id),
                "enabled": True,
            })
        gloves.append({
            "id": name,
            "displayName": display,
            "itemDefinitionIndex": int(item_id),
            "enabled": True,
            "skins": skins,
        })
    return sorted(gloves, key=lambda x: x["displayName"])


def build_gloves_from_api(root, translations, api_skins):
    items = collect_items(root)
    glove_items = {
        int(item_id): item
        for item_id, item in items.items()
        if item_id.isdigit()
        and isinstance(item, dict)
        and item.get("prefab") == "hands_paintable"
    }
    grouped = {item_id: [] for item_id in glove_items}
    for skin in api_skins:
        weapon = skin.get("weapon", {})
        weapon_id = weapon.get("weapon_id")
        paint_index = skin.get("paint_index")
        if weapon_id not in grouped or paint_index is None:
            continue
        pattern = skin.get("pattern", {})
        rarity = skin.get("rarity", {})
        entity = glove_items[weapon_id].get("name")
        grouped[weapon_id].append({
            "id": f"{entity}:{paint_index}",
            "displayName": pattern.get("name") or skin.get("name", "").split("|")[-1].strip(),
            "paintKit": int(paint_index),
            "seed": 0,
            "wear": float(skin.get("min_float") or 0.0001),
            "itemDefinitionIndex": int(weapon_id),
            "legacyModel": bool(skin.get("legacy_model", False)),
            "enabled": True,
            "rarity": rarity.get("id"),
        })

    gloves = []
    for item_id, item in glove_items.items():
        name = item.get("name", "")
        skins = sorted(unique_by_id(grouped.get(item_id, [])), key=lambda x: (x["displayName"], x["paintKit"]))
        if not skins:
            continue
        gloves.append({
            "id": name,
            "displayName": localize(item.get("item_name", name), translations),
            "itemDefinitionIndex": int(item_id),
            "enabled": True,
            "skins": skins,
        })
    return sorted(gloves, key=lambda x: x["displayName"])


def build_agents(api_agents, root):
    schema_metadata = build_agent_schema_metadata(root)
    agents = []
    for agent in api_agents or []:
        agent_id = agent.get("id")
        name = agent.get("name")
        model = agent.get("model_player")
        team = normalize_agent_team(agent.get("team", {}).get("id"))
        def_index = agent.get("def_index")
        rarity = agent.get("rarity", {})
        collections = agent.get("collections") or []
        group = collections[0].get("name") if collections and isinstance(collections[0], dict) else None
        metadata = schema_metadata.get(str(def_index), {})
        voice_prefix = metadata.get("voicePrefix")
        if not agent_id or not name or not model or not team:
            continue
        display_name = str(name).split("|", 1)[0].strip()
        agents.append({
            "id": str(agent_id),
            "displayName": display_name,
            "team": team,
            "model": str(model),
            "itemDefinitionIndex": int(def_index) if str(def_index).isdigit() else None,
            "voicePrefix": voice_prefix,
            "hasFemaleVoice": bool(metadata.get("hasFemaleVoice", False)),
            "enabled": True,
            "rarity": rarity.get("id") if isinstance(rarity, dict) else None,
            "group": group,
        })
    return sorted(unique_by_id(agents), key=lambda x: (x["team"], x["displayName"]))


def build_agent_schema_metadata(root):
    metadata = {}
    for item_id, item in collect_items(root).items():
        if not item_id.isdigit() or not isinstance(item, dict):
            continue
        if not item.get("model_player") or "customplayer" not in str(item.get("prefab", "")):
            continue
        voice_prefix = item.get("vo_prefix")
        if not voice_prefix:
            continue
        text = " ".join(str(item.get(key, "")) for key in ("default_cheer", "default_defeat", "vo_prefix"))
        inventory_data = item.get("inventory_image_data", {})
        if isinstance(inventory_data, dict):
            text = f"{text} {inventory_data.get('pose_sequence', '')}"
        metadata[str(item_id)] = {
            "voicePrefix": str(voice_prefix),
            "hasFemaleVoice": "fem" in text.lower() or "female" in text.lower(),
        }
    return metadata


def normalize_agent_team(team):
    if not team:
        return None
    value = str(team).strip().lower()
    if value in {"terrorist", "terrorists", "t"}:
        return "t"
    if value in {"counter-terrorist", "counter-terrorists", "counterterrorist", "counterterrorists", "ct"}:
        return "ct"
    return None


def glove_family_for_item(item_name):
    if item_name == "studded_bloodhound_gloves":
        return "bloodhound"
    if item_name == "studded_hydra_gloves":
        return "hydra"
    if item_name == "studded_brokenfang_gloves":
        return "brokenfang"
    if item_name == "slick_gloves":
        return "driver"
    if item_name == "sporty_gloves":
        return "sport"
    if item_name == "leather_handwraps":
        return "handwrap"
    if item_name == "motorcycle_gloves":
        return "motorcycle"
    if item_name == "specialist_gloves":
        return "specialist"
    return None


def glove_family_for_paint(paint):
    name = paint.get("name", "")
    path = paint.get("vmt_path", "")
    if not name and "paints_gloves" not in path:
        return None
    if name.startswith("bloodhound_hydra_"):
        return "hydra"
    if name.startswith("bloodhound_"):
        return "bloodhound"
    if name.startswith("operation10_"):
        return "brokenfang"
    if name.startswith("slick_") or name.startswith("glove_driver_"):
        return "driver"
    if name.startswith("sporty_") or name.startswith("glove_sport_"):
        return "sport"
    if name.startswith("handwrap_"):
        return "handwrap"
    if name.startswith("motorcycle_"):
        return "motorcycle"
    if name.startswith("specialist_") or name.startswith("glove_specialist_"):
        return "specialist"
    return None


def with_display_name_zh(entry, display_name_zh):
    """Insert the Chinese name next to displayName while retaining every other field."""
    result = {}
    chinese = str(display_name_zh or entry.get("displayName") or "").strip()
    for key, value in entry.items():
        if key == "displayNameZh":
            continue
        result[key] = value
        if key == "displayName":
            result["displayNameZh"] = chinese
    if "displayNameZh" not in result:
        result["displayNameZh"] = chinese
    return result


def schema_chinese_names(root, translations_zh):
    item_names = {}
    for item in collect_items(root).values():
        if not isinstance(item, dict) or not item.get("name"):
            continue
        item_names[str(item["name"])] = localize(item.get("item_name", item["name"]), translations_zh)

    paint_names = {}
    for paint_id, paint in as_dict(root.get("paint_kits", {})).items():
        if paint_id.isdigit() and isinstance(paint, dict):
            paint_names[int(paint_id)] = localize(
                paint.get("description_tag", paint.get("name", paint_id)), translations_zh
            )
    return item_names, paint_names


def enrich_bilingual(weapons, knives, gloves, agents, api_skins_zh, api_agents_zh, root=None, translations_zh=None):
    skin_names = {}
    item_names = {}
    for skin in api_skins_zh or []:
        weapon = skin.get("weapon", {})
        entity = weapon.get("id")
        paint_index = skin.get("paint_index")
        if not entity or paint_index is None:
            continue
        pattern = skin.get("pattern", {})
        display = pattern.get("name") or str(skin.get("name", "")).split("|")[-1].strip()
        if display:
            skin_names[(str(entity), int(paint_index))] = str(display)
        if weapon.get("name"):
            item_names[str(entity)] = str(weapon["name"])

    schema_items, schema_paints = ({}, {})
    if root is not None and translations_zh:
        schema_items, schema_paints = schema_chinese_names(root, translations_zh)

    def enrich_containers(containers, identity_key):
        for index, container in enumerate(containers):
            identity = str(container.get(identity_key, ""))
            chinese = WEAPON_DISPLAY_ZH.get(identity) or item_names.get(identity) or schema_items.get(identity) or container.get("displayName")
            enriched = with_display_name_zh(container, chinese)
            enriched["skins"] = [
                with_display_name_zh(
                    skin,
                    "原版" if int(skin.get("paintKit", -1)) == 0 and skin.get("displayName") == "Vanilla"
                    else skin_names.get((identity, int(skin.get("paintKit", -1))))
                    or schema_paints.get(int(skin.get("paintKit", -1)))
                    or skin.get("displayName"),
                )
                for skin in container.get("skins", [])
            ]
            containers[index] = enriched

    enrich_containers(weapons, "entityName")
    enrich_containers(knives, "id")
    enrich_containers(gloves, "id")

    agent_names = {
        str(agent.get("id")): str(agent.get("name", "")).split("|", 1)[0].strip()
        for agent in api_agents_zh or []
        if agent.get("id") and agent.get("name")
    }
    for index, agent in enumerate(agents):
        agents[index] = with_display_name_zh(
            agent, agent_names.get(str(agent.get("id"))) or agent.get("displayName")
        )


def load_existing_definitions(output):
    names = ("weapons", "knives", "gloves", "agents")
    result = []
    for name in names:
        path = output / f"{name}.json"
        result.append(json.loads(path.read_text(encoding="utf-8")))
    return result


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" keeps the output byte-identical across platforms; without it
    # Python rewrites every "\n" as CRLF on Windows.
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def strip_music_kit_prefix(name):
    # "Music Kit | Feed Me, High Noon" / "\u97f3\u4e50\u76d2 | ..." -> keep only the kit name.
    if name and " | " in name:
        return name.split(" | ", 1)[1].strip()
    return (name or "").strip()


def build_music_kits(api_music_kits, api_music_kits_zh):
    zh_names = {}
    for entry in api_music_kits_zh or []:
        zh_names[entry.get("id")] = strip_music_kit_prefix(entry.get("name"))

    kits = []
    for entry in api_music_kits or []:
        kit_id = entry.get("id") or ""
        match = re.fullmatch(r"music_kit-(\d+)", kit_id)
        if not match:
            continue  # skips the "_st" StatTrak variants
        number = int(match.group(1))
        if number <= 2:
            continue  # engine default kits, not selectable cosmetics
        name = strip_music_kit_prefix(entry.get("name"))
        if not name:
            continue
        kit = {"id": str(number), "musicKit": number, "displayName": name}
        zh = zh_names.get(kit_id)
        if zh:
            kit["displayNameZh"] = zh
        kits.append(kit)

    kits.sort(key=lambda k: k["musicKit"])
    return kits


def enrich_music_kits(music_kits, api_music_kits_zh):
    zh_names = {
        entry.get("id"): strip_music_kit_prefix(entry.get("name"))
        for entry in api_music_kits_zh or []
    }
    for kit in music_kits:
        zh = zh_names.get(f"music_kit-{kit.get('musicKit')}")
        if zh:
            kit["displayNameZh"] = zh


def unique_by_id(entries):
    result = []
    seen = set()
    for entry in entries:
        if entry["id"] in seen:
            continue
        seen.add(entry["id"])
        result.append(entry)
    return result


def main():
    parser = argparse.ArgumentParser(description="Generate WeaponSkins JSON definitions from CS2 item schema data.")
    parser.add_argument("--items-game", default=ITEMS_GAME_URL)
    parser.add_argument("--language", default=CSGO_ENGLISH_URL)
    parser.add_argument(
        "--language-zh",
        default="",
        help="Optional local Valve csgo_schinese.txt used as a fallback for zh-CN API names.",
    )
    parser.add_argument("--skins-api", default=SKINS_API_URL)
    parser.add_argument("--agents-api", default=AGENTS_API_URL)
    parser.add_argument("--skins-api-zh", default=SKINS_API_ZH_URL)
    parser.add_argument("--agents-api-zh", default=AGENTS_API_ZH_URL)
    parser.add_argument("--music-kits-api", default=MUSIC_KITS_API_URL)
    parser.add_argument("--music-kits-zh-api", default=MUSIC_KITS_ZH_API_URL)
    parser.add_argument("--output", default="data")
    parser.add_argument(
        "--merge-existing",
        action="store_true",
        help="Only merge displayNameZh into current JSON; preserve all stable English data and identifiers.",
    )
    args = parser.parse_args()

    output = Path(args.output)
    api_skins_zh = json.loads(load_text(args.skins_api_zh)) if args.skins_api_zh else None
    api_agents_zh = json.loads(load_text(args.agents_api_zh)) if args.agents_api_zh else None
    api_music_kits_zh = json.loads(load_text(args.music_kits_zh_api)) if args.music_kits_zh_api else None

    if args.merge_existing:
        weapons, knives, gloves, agents = load_existing_definitions(output)
        music_kits = json.loads((output / "music_kits.json").read_text(encoding="utf-8"))
        enrich_bilingual(weapons, knives, gloves, agents, api_skins_zh, api_agents_zh)
        enrich_music_kits(music_kits, api_music_kits_zh)
        write_json(output / "weapons.json", weapons)
        write_json(output / "knives.json", knives)
        write_json(output / "gloves.json", gloves)
        write_json(output / "agents.json", agents)
        write_json(output / "music_kits.json", music_kits)
        write_json(output / "categories.json", CATEGORIES)
        print(
            f"Merged Chinese names into {len(weapons)} weapons, {len(knives)} knives, "
            f"{len(gloves)} gloves, {len(agents)} agents, and {len(music_kits)} music kits in {output}"
        )
        return 0

    root = find_items_root(VdfParser(load_text(args.items_game)).parse())
    translations = parse_translations(load_text(args.language))
    translations_zh = parse_translations(load_text(args.language_zh)) if args.language_zh else {}
    api_skins = json.loads(load_text(args.skins_api)) if args.skins_api else None
    api_agents = json.loads(load_text(args.agents_api)) if args.agents_api else None
    api_music_kits = json.loads(load_text(args.music_kits_api)) if args.music_kits_api else None

    weapons = build_weapons(root, translations, api_skins)
    knives = build_knives(root, translations, api_skins)
    gloves = build_gloves(root, translations, api_skins)
    agents = build_agents(api_agents, root)
    enrich_bilingual(
        weapons,
        knives,
        gloves,
        agents,
        api_skins_zh,
        api_agents_zh,
        root,
        translations_zh,
    )
    music_kits = build_music_kits(api_music_kits, api_music_kits_zh)

    if not any(w["skins"] for w in weapons):
        print("No weapon skins were generated; check item_sets and paint_kits in the input schema.", file=sys.stderr)
        return 2

    write_json(output / "weapons.json", weapons)
    write_json(output / "knives.json", knives)
    write_json(output / "gloves.json", gloves)
    write_json(output / "agents.json", agents)
    write_json(output / "music_kits.json", music_kits)
    write_json(output / "categories.json", CATEGORIES)
    print(f"Generated {sum(len(w['skins']) for w in weapons)} weapon skins, {sum(len(k['skins']) for k in knives)} knife skins, {sum(len(g['skins']) for g in gloves)} glove skins, and {len(agents)} agents and {len(music_kits)} music kits into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
