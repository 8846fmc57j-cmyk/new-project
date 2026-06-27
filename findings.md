# Findings

## 2026-06-27

- Repository is synced with GitHub at `8846fmc57j-cmyk/new-project`.
- Current technical document is `docs/idle-treasure-game-tech-design.md`.
- `error.log` is a local untracked log file and should not be committed.
- MVP priority is now configuration templates and first demo data.
- Runtime config export command is `python3 Tools/export_config.py`.
- Generated JSON files are committed because they are useful for early client/server prototyping.
- MVP simulation command is `python3 Tools/simulate_mvp.py --iterations 1000 --seed 20260627`.
- Battle power ratios from the first simulation are intentionally slightly forgiving in early maps.
