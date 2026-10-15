# Mission report: mission_03_tight

## Outcome
SAFE RETURN: the agent turned back before running out of resources. EVE was NOT confirmed.

- Actions taken: 74
- Battery left: 4, time left: 18
- Recharges used: 2

## Inferred location and status
- **Location:** (7, 8)
- **Confidence:** 72% (probability within 2 cells of that spot)
- **Status:** unknown (no clue gathered, so every state is equally likely)
- Top three candidate cells: (7, 8) 7%, (8, 7) 7%, (6, 8) 6%

## Evidence found
- Signal scans: 3
  - scan at (0, 0): strength 0.083
  - scan at (3, 1): strength 0.107
  - scan at (4, 4): strength 0.164
- Clues inspected: 0
- Empty inspections: 0 

## Strategy timeline
- step 1: **scan** (confidence afterwards 68%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 2-5: **explore** (confidence afterwards 68%). Unsure (confidence 0.68). Walk towards (7, 6) for a new scan angle.
- step 6: **scan** (confidence afterwards 78%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 7-10: **commit** (confidence afterwards 78%). Confident (0.78) EVE is near (7, 7). Walk there.
- step 11: **scan** (confidence afterwards 72%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 12-19: **turn_back** (confidence afterwards 72%). Resources are low (battery 13, time 86). Turn back towards the safe point (0, 0).
- step 20: **recharge** (confidence afterwards 72%). I am on a station with 2 use(s) left and my battery is low (5). Recharge.
- steps 21-33: **explore** (confidence afterwards 72%). Unsure (confidence 0.72). Walk towards (7, 7) for a new scan angle.
- steps 34-46: **turn_back** (confidence afterwards 72%). Resources are low (battery 17, time 61). Turn back towards the safe point (0, 0).
- step 47: **recharge** (confidence afterwards 72%). I am on a station with 1 use(s) left and my battery is low (4). Recharge.
- steps 48-60: **explore** (confidence afterwards 72%). Unsure (confidence 0.72). Walk towards (7, 7) for a new scan angle.
- steps 61-73: **turn_back** (confidence afterwards 72%). Resources are low (battery 17, time 31). Turn back towards the safe point (0, 0).
- step 74: **end** (confidence afterwards 72%). I am at the safe point (0, 0), resources are low and nothing more to recharge. End the mission safely.

## Map
```
    0123456789
 0 |@++.......|
 1 |+++s......|
 2 |.+++......|
 3 |..+++.....|
 4 |...+s+..?.|
 5 |....+++...|
 6 |.....+++..|
 7 |.....?....|
 8 |.......X..|
 9 |..........|
```
Legend: S station, + path, s scan spot, c genuine clue found, d decoy found, ? clue never found, M agent's final estimate, E EVE's true position, X estimate exactly on EVE, @ final position

## Recommended next step
Refuel, then go straight to (7, 8) and inspect it. EVE is probably there (72% sure), but she was not confirmed.

## Evaluation (uses the hidden truth, never seen by the agent)
- True position: (7, 8), agent's estimate: (7, 8), error: 0.0 cells
- True status: low_power, agent's estimate: active
