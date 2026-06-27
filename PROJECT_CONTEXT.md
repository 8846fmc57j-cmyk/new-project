# Project Context

This file is the long-term project memory for Codex work in this repository.
Read this first when the chat context is compressed or when continuing a later
session.

## Project Identity

- Project type: commercial idle treasure digging game.
- Product direction: 2.5D vertical WeChat Mini Game.
- Formal client direction: Cocos Creator + TypeScript + WeChat Mini Game.
- Current validation surface: browser Web prototype connected to the local Mock API.
- Reference inspiration: "道友来挖宝" style idle digging, appraisal, and combat loop.
- Current monetization rule: do not add ads yet. MVP focuses on core fun and flow.

## Core Gameplay Priority

The first playable version should prove this loop:

1. Guest login.
2. Enter game.
3. See main quest and guided next action.
4. Claim idle digging rewards.
5. Appraise antiques and see estimated value changes.
6. Fight monsters and receive rewards.
7. Equip simple gear.
8. Break through to the next realm.
9. Continue into the next main quest target.

The most important MVP screens are:

- Login / enter game.
- Main home screen.
- Main quest and tutorial guidance.
- Idle digging reward claim.
- Antique appraisal / valuation screen.
- Monster battle screen.
- Equipment and realm progression entry points.

## Technical Direction

- Keep CSV files in `Config/csv/` as editable design data.
- Generate runtime JSON files in `Config/json/` with `python3 Tools/export_config.py`.
- Use `Server/mock_api.py` as the temporary local backend for MVP integration.
- Keep the Web prototype as a fast flow and API test surface.
- Move toward a Cocos Creator WeChat Mini Game project under `Client/wechat-minigame/`.
- Do not commit `error.log`; it is local runtime noise.

## Important Files

- `README.md`: project entry and run commands.
- `docs/idle-treasure-game-tech-design.md`: main technical design.
- `docs/wechat-minigame-2.5d-tech-plan.md`: formal 2.5D WeChat Mini Game plan.
- `docs/mvp-login-mainline-flow.md`: login, enter-game, quest, and tutorial flow.
- `docs/mvp-client-screen-flow.md`: MVP client screens and API behavior.
- `docs/mvp-development-backlog.md`: executable development backlog.
- `Config/csv/`: source configuration tables.
- `Config/json/`: generated runtime configuration.
- `Server/mock_api.py`: local MVP Mock API.
- `Client/web-prototype/`: browser prototype.
- `Tools/run_mvp_demo.py`: one-command local demo launcher.
- `task_plan.md`, `progress.md`, `findings.md`: working memory and session log.

## Current Git State Rule

All updates should modify this same repository, not create separate copies.
After each meaningful document or code update:

1. Run relevant validation commands.
2. Commit the changes to the current repository.
3. Push or ask the user to push through GitHub Desktop if command-line auth fails.

## Current Validation Commands

Use these before claiming a development step is complete:

```bash
python3 Tools/export_config.py
python3 Tools/test_mock_api.py
python3 Tools/test_web_prototype.py
python3 Tools/simulate_mvp.py --iterations 100 --seed 123 > /tmp/mvp_check.json
python3 -m json.tool /tmp/mvp_check.json >/dev/null
git diff --check
```

For docs-only changes, `git diff --check` is usually enough.

## Next Recommended Step

Start the formal Cocos/WeChat Mini Game scaffold:

1. Create `Client/wechat-minigame/`.
2. Add README and directory structure for scenes, scripts, config, state, UI,
   gameplay, resources, sprites, Spine animations, and audio.
3. Map the existing Mock API endpoints to future Cocos services.
4. Keep the Web prototype as the comparison baseline until the Cocos version can
   run the same MVP loop.

## Decisions To Preserve

- Use Cocos Creator, not Unity, for the formal WeChat Mini Game client.
- The game should feel 2.5D, not flat 2D.
- The first screen after login should be playable, not a marketing page.
- Appraisal and combat are core MVP systems.
- Ads are intentionally postponed.
- Server should own quest claimability and rewards.
- Local prototype reset is acceptable only for MVP testing.
