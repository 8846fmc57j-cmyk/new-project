# Cocos Client API Mapping

This document maps the current local Mock API to the future Cocos Creator client
service layer. It is the bridge between the working Web prototype and the formal
WeChat Mini Game client.

## Base Rules

- Local MVP base URL: `http://127.0.0.1:8787`.
- Production base URL should be injected by build/environment config later.
- Server responses own rewards, quest claimability, tutorial completion, and
  progression state.
- Client UI may preview possible outcomes, but cannot grant rewards locally.
- Every request should have loading, success, error, and retry-safe UI behavior.

## Endpoint Mapping

| Endpoint | Cocos service | Used by scene | Purpose |
| --- | --- | --- | --- |
| `GET /health` | `HealthApi.check()` | Boot | Verify local API availability during development |
| `GET /config/latest` | `ConfigApi.fetchLatest()` | Boot | Load runtime JSON config snapshot |
| `POST /auth/guest-login` | `AuthApi.guestLogin()` | Boot | Create or resume local MVP profile |
| `GET /game/sync` | `GameApi.sync()` | Boot, Home | Fetch full player state for UI rendering |
| `POST /idle/claim` | `IdleApi.claim()` | Home | Claim accumulated digging rewards |
| `POST /antique/appraise` | `AppraisalApi.appraise()` | Appraisal | Appraise an antique and update value state |
| `POST /battle/start` | `BattleApi.start()` | Battle | Start a battle stage and receive battle preview |
| `POST /battle/finish` | `BattleApi.finish()` | Battle | Finish battle and receive rewards |
| `POST /equipment/equip` | `EquipmentApi.equip()` | Home | Equip starter gear and refresh combat power |
| `POST /realm/breakthrough` | `RealmApi.breakthrough()` | Home | Spend resources to reach next realm |
| `POST /quest/claim` | `QuestApi.claim()` | Home | Claim server-approved main quest reward |
| `POST /tutorial/complete` | `TutorialApi.complete()` | Home | Mark a tutorial step completed |
| `POST /dev/reset` | `DevApi.reset()` | Boot, Home | Local-only reset for repeated MVP testing |

## State Shape Needed By Cocos

The Cocos client should normalize `/game/sync` into these state modules:

| State module | Data |
| --- | --- |
| `PlayerState` | player id, nickname, realm id, combat power |
| `ResourceState` | copper coins, spirit stones, jade, idle reward status |
| `QuestState` | active quest, completed quests, claimable state |
| `TutorialState` | current tutorial step and completed tutorial ids |
| `InventoryState` | items, antiques, equipment, equipped slots |
| `BattleState` | unlocked stages, cleared stages, latest result |
| `ConfigState` | maps, drops, antiques, monsters, stages, equipment, quests |

## MVP Error Handling

| Case | Client behavior |
| --- | --- |
| API unavailable | Stay on Boot and show a retry button |
| Session missing | Run guest login again, then sync |
| Quest not claimable | Disable claim button and show next required action |
| Not enough resources | Keep button disabled and show requirement text |
| Battle power too low | Allow preview, but show danger state before finish |
| Request timeout | Re-enable button and show retry feedback |

## Cocos Port Order

1. `Boot.scene`: config load, guest login, sync, enter Home.
2. `Home.scene`: player resources, active quest, tutorial, idle claim.
3. `Appraisal.scene`: antique appraisal request and result feedback.
4. `Battle.scene`: battle start, result, reward, cleared stage update.
5. Equipment and realm panels inside Home.
6. First 2.5D art pass for digging area, appraisal table, and combat lane.

