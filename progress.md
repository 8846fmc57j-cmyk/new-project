# Progress

## 2026-06-27

- Started first configuration pass for the MVP.
- Planned to add CSV templates and sample data for core gameplay systems.
- Added first CSV templates for items, maps, drops, antiques, monsters, battle stages, equipment, and quests.
- CSV validation found missing boss stage references for later maps; added placeholder boss stages and monsters through map 05.
- CSV validation now passes across IDs, drop groups, monster rewards, map boss stages, and basic malformed-row checks.
- Continuing with a small export tool that validates CSV files and generates JSON files plus a manifest.
- Added `Tools/export_config.py`.
- Generated JSON runtime configs under `Config/json/`.
- Manifest contains row counts and SHA-256 hashes for each generated JSON file.
- Starting MVP simulation tooling for validating drop rewards, appraisal price spread, and battle power gates.
- Added first version of `Tools/simulate_mvp.py`.
- Simulation ran successfully with deterministic JSON output.
- Error: attempted to pipe simulator JSON into an inline Python script that also used a heredoc, so stdin was consumed by the script body instead of the JSON. Fix is to write the simulation output to a temp file before parsing it.
- Re-ran simulation through temp files successfully.
- Current battle estimated/recommended power ratios are mostly between 0.8 and 1.0, acceptable for early MVP tuning.
- Current appraisal median prices show a large spread between common, rare, epic, legendary, and mythic antiques, which supports the intended jackpot feeling.
- Starting login, enter-game, main quest, and tutorial flow definition.
- Added login/mainline flow document.
- Expanded main quest chain through the first daily-task handoff.
- Added `tutorial_steps.csv` for the first 12 guided steps.
- Starting local Mock API server for guest login, game sync, quest, tutorial, appraisal, and battle smoke testing.
- Added `Server/mock_api.py`, `Server/README.md`, and `Tools/test_mock_api.py`.
- Mock API smoke test passes for guest login, game sync, quest claim, tutorial completion, antique appraisal, battle start, battle finish, and idle claim.
- Starting MVP client screen and API integration specification.
- Added `docs/mvp-client-screen-flow.md` for startup/login, home, main quest, tutorial, appraisal, battle, and API mapping.
- Starting MVP development backlog so the next build step is executable.
- Added `docs/mvp-development-backlog.md` with milestones, client tasks, Mock API tasks, config tasks, and validation criteria.
- Starting runnable MVP Web prototype for fast client-flow validation.
- Added `Client/web-prototype` with login, home, idle claim, appraisal, and battle panels.
- Added CORS support to `Server/mock_api.py` so the browser prototype can call the local API.
- Verified the Web prototype through Playwright: page loads, guest login succeeds, appraisal updates antique state, and battle finish grants spirit stones.
- Playwright screenshot command was invoked with the wrong output argument format; no screenshot artifact is required for this commit.
- Error: `Tools/test_mock_api.py` failed while the preview Mock API was already running on port 8787 because it connected to the existing mutated in-memory state. Fix: allow `MOCK_API_PORT` and run the smoke test on isolated port 18787.
- Starting quest and tutorial progression in the Web prototype.
- Added tutorial display, tutorial completion action, activity log, and extra sync fields for completed quests, completed tutorials, and cleared stages.
