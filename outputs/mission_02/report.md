# Mission report: mission_02_recharge

## Outcome
SUCCESS: EVE was located and confirmed by inspection.

- Actions taken: 47
- Battery left: 20, time left: 45
- Recharges used: 1

## Inferred location and status
- **Location:** (7, 8)
- **Confidence:** 88% (probability within 2 cells of that spot)
- **Status:** low_power (confirmed by direct inspection)
- Top three candidate cells: (7, 8) 30%, (9, 6) 21%, (6, 8) 13%

## Evidence found
- Signal scans: 4
  - scan at (0, 0): strength 0.083
  - scan at (3, 1): strength 0.107
  - scan at (4, 4): strength 0.164
  - scan at (7, 6): strength 0.347
- Clues inspected: 0
- Empty inspections: 0 

## Strategy timeline
- step 1: **scan** (confidence afterwards 68%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 2-5: **explore** (confidence afterwards 68%). Unsure (confidence 0.68). Walk towards (7, 6) for a new scan angle.
- step 6: **scan** (confidence afterwards 78%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 7-10: **commit** (confidence afterwards 78%). Confident (0.78) EVE is near (7, 7). Walk there.
- step 11: **scan** (confidence afterwards 72%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 12-16: **explore** (confidence afterwards 72%). Unsure (confidence 0.72). Walk towards (7, 7) for a new scan angle.
- steps 17-29: **turn_back** (confidence afterwards 72%). Resources are low (battery 18, time 81). Turn back towards the safe point (0, 0).
- step 30: **recharge** (confidence afterwards 72%). I am on a station with 2 use(s) left and my battery is low (5). Recharge.
- steps 31-43: **explore** (confidence afterwards 72%). Unsure (confidence 0.72). Walk towards (7, 7) for a new scan angle.
- step 44: **scan** (confidence afterwards 88%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 45-47: **commit** (confidence afterwards 88%). Confident (0.88) EVE is near (7, 8). Walk there.

## Recommended next step
EVE is low on power. Bring a charger to her, or carry her to the charging station.

## Evaluation (uses the hidden truth, never seen by the agent)
- True position: (7, 8), agent's estimate: (7, 8), error: 0.0 cells
- True status: low_power, agent's estimate: low_power
