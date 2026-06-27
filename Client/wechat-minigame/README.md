# WeChat Mini Game Client

This folder is the formal client direction for the project:

- Engine: Cocos Creator.
- Language: TypeScript.
- Platform target: WeChat Mini Game.
- Presentation: 2.5D vertical idle treasure digging.

The existing `Client/web-prototype/` remains the fast validation surface for
flow, API, and balance. This folder is where that validated loop will be ported
into the real game client.

## MVP Client Goal

The first Cocos playable build should reproduce the same loop already proven by
the Web prototype:

1. Guest login.
2. Enter the home scene.
3. Show current resources, main quest, and tutorial step.
4. Claim idle digging rewards.
5. Enter appraisal and value an antique.
6. Enter battle and clear the first monster stage.
7. Equip starter gear.
8. Break through to the next realm.

No ad SDK, paid shop, account binding, guild, leaderboard, or live operation
system should be added before this loop is stable.

## Directory Plan

```text
Client/wechat-minigame/
  assets/
    scenes/
      Boot.scene
      Home.scene
      Appraisal.scene
      Battle.scene
    scripts/
      api/
      config/
      state/
      ui/
      gameplay/
      utils/
    resources/
      config/
      sprites/
      spine/
      audio/
  docs/
```

The `.scene` files above are planned Cocos Creator assets. They are not created
manually in this scaffold; Cocos Creator should generate them when the project is
opened and scenes are created.

## Scene Responsibilities

| Scene | Purpose | MVP responsibility |
| --- | --- | --- |
| Boot | Startup and initialization | Load runtime config, initialize API client, guest login, then enter Home |
| Home | Main playable screen | Show digging area, resources, main quest, idle claim, and feature entries |
| Appraisal | Antique valuation | Show antique, estimate range, final appraisal result, and reward feedback |
| Battle | Monster combat | Show 2.5D combat lane, power comparison, result, and reward feedback |

## Script Module Plan

| Folder | Responsibility |
| --- | --- |
| `api/` | Wrap Mock API and future production backend calls |
| `config/` | Load JSON config and provide lookup helpers |
| `state/` | Store profile, resources, quests, tutorial, equipment, and battle state |
| `ui/` | Screen components, panels, buttons, red dots, and toast feedback |
| `gameplay/` | Appraisal, battle, idle rewards, quest, tutorial, and realm logic |
| `utils/` | Shared formatting, timers, event bus, and platform helpers |

## Porting Rule

When a flow works in `Client/web-prototype/`, port it into Cocos in this order:

1. API contract and state shape.
2. Cocos screen layout.
3. Button action and loading state.
4. Reward/result feedback.
5. 2.5D visual polish.

This keeps the Cocos build playable at every step instead of becoming a visual
mockup with disconnected data.

