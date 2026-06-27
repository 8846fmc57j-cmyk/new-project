# Task Plan

## Goal

Build the first MVP development assets for the idle treasure digging game:

- Keep the technical design document as the single source of truth.
- Add shared configuration tables for planning, Unity client work, and backend prototyping.
- Keep every meaningful update committed to the same GitHub repository.

## Phases

1. Create planning files.
2. Add project folders and CSV configuration templates.
3. Validate CSV formatting.
4. Commit and sync changes to GitHub.
5. Add CSV validation and JSON export tooling.
6. Generate runtime JSON configuration files.
7. Add MVP simulation tooling for drops, appraisal, and combat.
8. Define login, enter-game, main quest, and tutorial flow.
9. Add a local mock API server for MVP client/backend flow testing.

## Current Scope

Run the first playable MVP flow locally:

- Guest login
- Enter game and sync profile
- Main quest claim
- Tutorial step completion
- Idle reward claim
- Antique appraisal
- Battle start and finish

## Decisions

- MVP does not include ad SDK or ad rewards.
- Appraisal and combat are core MVP systems.
- Config IDs use stable English identifiers; display text should go through localization keys.
- CSV files are edited by planning/design; JSON files are generated runtime artifacts for client/server.
- Early simulation tools should be deterministic by default so balance changes are comparable.
- MVP starts with guest login and automatic profile creation; account binding can come later.
- Mock API is for local integration only; production backend can later replace it without changing config IDs.
