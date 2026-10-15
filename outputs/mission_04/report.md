# Mission report: mission_04

## Outcome
SUCCESS: EVE was located and confirmed by inspection.

- Actions taken: 22
- Battery left: 27, time left: 71
- Recharges used: 0

## Inferred location and status
- **Location:** (7, 8)
- **Confidence:** 92% (probability within 2 cells of that spot)
- **Status:** low_power (confirmed by direct inspection)
- Top three candidate cells: (7, 8) 50%, (6, 8) 16%, (8, 8) 11%

## Evidence found
- Signal scans: 4
  - scan at (0, 0): strength 0.129
  - scan at (3, 2): strength 0.1
  - scan at (4, 5): strength 0.169
  - scan at (7, 6): strength 0.345
- Clues inspected: 2
  - clue at (4, 4): says EVE is near (7, 8) and low_power (consistent with the final estimate)
  - clue at (6, 6): says EVE is near (2, 3) and low_power (far from the final estimate, probably a decoy)
- Empty inspections: 0 

## Strategy timeline
- step 1: **scan** (confidence afterwards 61%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 2-6: **explore** (confidence afterwards 61%). Unsure (confidence 0.61). Walk towards (4, 4) for a new scan angle.
- step 7: **scan** (confidence afterwards 49%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 8-11: **follow_clue** (confidence afterwards 73%). I am unsure (confidence 0.49) and heard a clue at (4, 4). Walk to it.
- step 12: **explore** (confidence afterwards 73%). Unsure (confidence 0.73). Walk towards (6, 7) for a new scan angle.
- step 13: **scan** (confidence afterwards 54%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 14-17: **follow_clue** (confidence afterwards 51%). I am unsure (confidence 0.54) and heard a clue at (6, 6). Walk to it.
- step 18: **explore** (confidence afterwards 51%). Unsure (confidence 0.51). Walk towards (7, 7) for a new scan angle.
- step 19: **scan** (confidence afterwards 92%). I am at a new spot with no scan nearby. Scan to gather evidence.
- steps 20-22: **commit** (confidence afterwards 92%). Confident (0.92) EVE is near (7, 8). Walk there.

## Recommended next step
EVE is low on power. Bring a charger to her, or carry her to the charging station.

## Evaluation (uses the hidden truth, never seen by the agent)
- True position: (7, 8), agent's estimate: (7, 8), error: 0.0 cells
- True status: low_power, agent's estimate: low_power
