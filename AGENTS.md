# AstraSkins Repository Instructions

- All player-visible text and cosmetic names use the fixed `中文 / English` order and ASCII ` / ` separator; do not follow `css_lang`.
- Keep `displayName` as the stable English compatibility and sort field. Put Chinese in `displayNameZh` without changing IDs, paint kits, entity names, model paths, or persisted selection keys.
- Prefer Valve Simplified Chinese tokens, then established community names, then a concise semantic translation. Fall back to English when Chinese is unavailable and show identical names only once.
- Search must index both `displayNameZh` and `displayName`, while results always display Chinese first.
- After definition updates, run `python tools/validate_bilingual.py`; when merging names into an existing catalog, also pass `--baseline-ref HEAD` to prove stable fields did not change.
