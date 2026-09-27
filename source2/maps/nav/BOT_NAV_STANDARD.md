# Bot / Navigation Standard — 135er Spandau Defeat

Every map is bot-ready by definition. A map is not considered playable until CS2 bots can traverse the full intended combat space.

## Mandatory requirements
- CT/Allies and T/Axis spawn groups each have at least two independent exits.
- A, B and C are reachable from both teams without jumps, boosts or destructible-only paths.
- Primary combat lanes have navigation width sufficient for two bots to pass where intended.
- Doorways, stairs, ramps, bridges and narrow alleys must be validated against CS2 bot pathing.
- No objective route may depend on ladders unless an alternate ground route exists.
- Water edges and steep terrain need blocking/clip treatment so bots do not stall or drown.
- Drop-downs must have a return path or be explicitly blocked from bot navigation.
- Cover props must not create one-way nav traps.
- Each map needs at least one left, center and right strategic route between team halves.
- A/B/C capture spaces require multiple approach vectors and defendable fallback positions.
- Long sightlines need intermediate cover nodes to prevent bots from clustering at spawn.
- Nav validation includes 5v5, 10v10 and 15-bot fill tests.

## Bot validation pass
1. Start with bot_quota 10, bot_quota_mode fill, bot_join_after_player 0.
2. Run at least three full rounds with no human intervention.
3. Repeat with bot_quota 15.
4. Observe stuck locations, repeated route loops, failed objective approaches and spawn blocking.
5. Fix geometry/nav blockers and repeat until bots reach all three objectives from both teams.

## Map acceptance
A map passes bot acceptance only when bots can:
- leave both spawns reliably;
- reach A, B and C;
- rotate between A/B/C;
- use at least three strategic lanes;
- recover from common combat detours;
- complete multiple rounds without persistent stuck clusters.
