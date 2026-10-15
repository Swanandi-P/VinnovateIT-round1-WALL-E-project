# VinnovateIT-round1-WALL-E-project
# WALL-E and EVE's Signal: an autonomous search agent

An agent that explores a simulated grid world to find EVE. It gathers clues, manages a limited battery and time budget, and decides where EVE is and what condition she is in, then recommends WALL-E's next move.

The agent never sees EVE's position or the clue locations. It only receives noisy observations, and keeps a **probabilistic belief** that it updates after every one.

```
 +-------------+   action (move/scan/inspect/recharge/end)   +--------------------+
 |    Agent    | ------------------------------------------> |    Environment     |
 |  belief +   |                                             | hidden: EVE, clues |
 |  decide()   | <------------------------------------------ | costs, noise       |
 +-------------+              observation                    +--------------------+
```

## Run it

Only the Python standard library is needed. On Windows use `py` instead of `python`.

```
python report.py configs/mission_01.json outputs/mission_01
```

This runs the mission, prints the final report, and saves `trace.jsonl`, `report.md` and `report.json` in the output folder. To see just the step-by-step run and the trace, use `python run.py <config> <output folder>`.

## Project layout

| File | What it does |
|---|---|
| `environment.py` | The simulator: loads the config, owns the hidden truth, returns observations |
| `belief.py` | Probability grid over EVE's location, plus a belief over her status; Bayes updates |
| `agent.py` | Decision rules: recharge, turn back, follow clues, commit, rescan, explore |
| `run.py` | The agent/environment loop; writes the action trace |
| `report.py` | Builds the final mission report |
| `viz.py` | Draws the ASCII map of the path, scans, clues and the final estimate |
| `try_scan.py`, `try_clue.py`, `try_ping.py` | Small scripts I used to test each piece as I built it |
| `configs/` | Mission configs |
| `outputs/` | Trace and report for each sample mission |


## Environment design

The world is a 10x10 grid. WALL-E starts at (0, 0), where there is a charging station with a limited number of uses. Battery and time are both finite.

| Action | Battery | Time | What the agent gets back |
|---|---|---|---|
| `move` N/S/E/W | 1 | 1 | New position, or `bumped: true` at the edge of the map |
| `scan` | 3 | 2 | A noisy signal **strength**, plus **pings** for uncollected clues within 3 cells |
| `inspect` | 2 | 2 | A clue (a location hint and a status hint), or EVE herself, or nothing |
| `recharge` | 0 | 4 | +40 battery, up to the maximum. Only works on a station with uses left. A failed attempt is free |
| `end` | 0 | 0 | Ends the mission voluntarily |

How the world behaves:

- **Signal.** Strength is `1 / (1 + distance)` plus Gaussian noise. One scan gives roughly how *far* EVE is but not in which direction, so the agent needs scans from several different places to triangulate.
- **Clues are found only through interaction.** A scan pings clues within 3 cells. The agent must walk there and inspect. A genuine clue gives a noisy hint of EVE's position and her status (the status hint is right 80% of the time). A **decoy** gives a random position and status. The agent cannot tell which is which.
- **Contact** happens when the agent inspects EVE's exact cell. This ends the mission.
- The mission also ends on `battery_depleted`, `time_expired`, or the agent's own `end`.
- A single seed makes every run reproducible: the same config always gives the same mission.

## Config format (JSON)

See `configs/mission_01.json`.

| Key | Meaning |
|---|---|
| `name`, `seed` | Mission name; seed for the simulator's randomness |
| `map` | `width`, `height`, `start`, and `stations` (a list of `pos` and `uses`) |
| `initial_signal` | `x`, `y` (where EVE was last detected), `strength`, `timestamp`. Currently only `x` and `y` are used, to build the starting belief. Strength and timestamp are stored for completeness but not yet used by the agent |
| `resources` | `battery`, `time`, `recharge_amount`, and per-action `costs` (battery and time) |
| `sensors` | `scan_noise`, `clue_noise`, `clue_status_accuracy` |
| `hidden` | **Never shown to the agent.** `eve` (`x`, `y`, `status`: `active`, `low_power` or `damaged`) and `clues` (a list of `x`, `y`, `genuine`) |

`run.py` removes the `hidden` section before creating the agent, so the agent can only learn it by acting.

## How the agent thinks

**Belief.** A probability for every grid cell ("EVE is here"), starting as a bell curve around the initial signal. Every observation multiplies each cell by how likely that reading would be *if EVE were there*, then renormalises (Bayes' rule):

- A **scan** favours cells at the right distance from the scan spot.
- A **clue hint** is treated as a mixture: 75% "genuine, so EVE is near the hint" and 25% "decoy, so EVE could be anywhere". One bad clue therefore cannot wreck the belief.
- An **empty inspect** shrinks that one cell (to 2% of its old value, never to zero).
- A separate 3-state belief tracks EVE's status, updated by clue status hints (assumed 70% reliable).

**Decisions.** The first rule that applies wins, and the reason is written to the trace:

1. **Recharge** if on a station with uses left and battery below 60%.
2. **Turn back** if battery or time cannot cover the trip to the nearest safe point plus a margin of 6. Once turning back, it stays committed until it recharges (otherwise it would oscillate).
3. **Rescan** if the last inspect found nothing, because the belief was wrong.
4. **Scan** on arriving at a spot with no scan within 3 cells.
5. **Follow a pinged clue** if confidence is below 75%.
6. **Commit**: if confidence is at least 75%, walk to the best guess and inspect it.
7. **Explore**: walk to a place far from earlier scans where a lot of probability sits.

**Confidence** is the probability mass within 2 cells of the best guess.

## Outputs of a run

- `trace.jsonl`: one JSON line per action with the state before, the mode, the **reasoning**, the action, the observation, and the updated belief (best guess, confidence, entropy, status probabilities).
- `report.md` / `report.json`: outcome, inferred location, status and confidence, evidence found, a strategy timeline, a recommended next step, and an evaluation against the hidden truth.

## Sample missions

| Mission | Setup | Result |
|---|---|---|
| `mission_01` | battery 60, time 100 | **Found EVE** in 20 actions with 4 scans. Position and status correct |
| `mission_02` | battery 40 | **Found EVE** in 47 actions. Turned back, recharged once at the station, then went out again |
| `mission_03` | battery 30 | **Safe return** after 74 actions, EVE not confirmed. Used both recharges, then ended at the station. The final guess (7, 8) was correct at 72% confidence, but status stayed unknown |
| `mission_04_clues` | wrong initial hint, one genuine clue and one decoy | **Found EVE** in 22 actions. Inspected both clues. The decoy pointed far from the final estimate and was flagged in the report |

## Limitations

- EVE is stationary, and the map has no obstacles.
- A scan gives distance only (no bearing), so the agent needs several scans from different places.
- In `mission_03` the agent repeats the same out-and-back trip and wastes both recharges, because a round trip to EVE is physically impossible on that battery. A smarter agent would detect this up front.
- The agent is greedy: it picks the next action with no multi-step planning.
- A decoy is only recognised statistically, after the agent has already walked to it.
- The agent's assumed noise levels and clue reliabilities are fixed constants, not learned.
- The belief is a grid, so it does not scale to continuous space.
- A scan is a single action type: the agent chooses where and when to scan, not between different kinds of scan.
- Configs are JSON only (no YAML), and the map layout and clue positions are written out explicitly rather than generated from a seed.

## Bonus items

**Done:** noisy sensors, decoy clues, and an ASCII map of each run (included in every `report.md`).

**Not done:** multi-agent coordination, an LLM-versus-classical-planner comparison, a generalisation benchmark and physics simulation.
