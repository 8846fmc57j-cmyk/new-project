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
- Login/mainline flow is documented in `docs/mvp-login-mainline-flow.md`.
- Tutorial configuration is stored in `Config/csv/tutorial_steps.csv` and exported to `Config/json/tutorial_steps.json`.
- Mock API should use only Python standard library so the repository stays easy to run on a clean machine.
- Mock API uses in-memory state and resets on restart, which is acceptable for local MVP client integration.
- Mock API smoke test command is `python3 Tools/test_mock_api.py`.
- Client MVP needs a direct playable home screen with current goal, idle rewards, appraisal entry, and battle entry visible immediately.
- Appraisal and battle screens are P0 because they prove whether the core loop has enough feedback before adding ads or deeper monetization.
- The next implementation phase should build UI against the Mock API instead of using disconnected fake UI data.
- Equipment equip and realm breakthrough can stay P1 until the login-home-appraisal-battle loop feels complete.
