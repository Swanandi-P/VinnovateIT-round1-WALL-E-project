import json
import math
import os
import sys

from run import run_mission, write_trace


def top_cells(belief, n=3):
    cells = []
    for y in range(belief.height):
        for x in range(belief.width):
            cells.append((belief.p[y][x], (x, y)))
    cells.sort(reverse=True)
    return cells[:n]


def phases(trace):
    # merge runs of steps that used the same mode into one line of the timeline
    result = []
    for entry in trace:
        if result and result[-1]["mode"] == entry["mode"]:
            result[-1]["last"] = entry["step"]
            result[-1]["confidence"] = entry["belief"]["confidence"]
        else:
            result.append({
                "mode": entry["mode"],
                "first": entry["step"],
                "last": entry["step"],
                "reason": entry["reasoning"],
                "confidence": entry["belief"]["confidence"],
            })
    return result


def collect_evidence(trace):
    scans, clues, empties, recharges = [], [], [], 0
    for entry in trace:
        obs = entry["observation"]
        kind = entry["action"]["type"]
        if kind == "scan":
            scans.append((tuple(obs["position"]), obs["strength"]))
        elif kind == "inspect":
            if obs["clue"] is not None:
                clues.append((tuple(obs["position"]), obs["clue"]))
            elif not obs["eve_found"]:
                empties.append(tuple(obs["position"]))
        elif kind == "recharge" and obs["ok"]:
            recharges += 1
    return scans, clues, empties, recharges


def recommend(found, guess, confidence, status, status_p):
    if found:
        advice = {
            "active": "EVE is active and can move on her own. Guide her back to base.",
            "low_power": "EVE is low on power. Bring a charger to her, or carry her to the charging station.",
            "damaged": "EVE is damaged. Send a repair team to her position.",
        }
        return advice[status]
    if confidence >= 0.6:
        return (f"Refuel, then go straight to {guess} and inspect it. "
                f"EVE is probably there ({confidence:.0%} sure), but she was not confirmed.")
    return "Not sure enough yet. Scan from several new places before committing to a spot."


def build_report(result):
    config = result["config"]
    trace = result["trace"]
    agent = result["agent"]
    reason = result["finish_reason"]
    found = agent.found

    guess = agent.belief.best_guess()
    confidence = agent.belief.confidence()
    status, status_p = agent.belief.status_estimate()
    scans, clues, empties, recharges = collect_evidence(trace)

    outcomes = {
        "eve_found": "SUCCESS: EVE was located and confirmed by inspection.",
        "agent_ended": "SAFE RETURN: the agent turned back before running out of resources. EVE was NOT confirmed.",
        "battery_depleted": "FAILURE: the battery ran out in the field.",
        "time_expired": "FAILURE: time ran out.",
    }
    outcome = outcomes.get(reason, reason)

    if found:
        status_text = f"{status} (confirmed by direct inspection)"
    elif status_p > 0.5:
        status_text = f"{status} ({status_p:.0%} sure, based on clue hints)"
    else:
        status_text = "unknown (no clue gathered, so every state is equally likely)"

    next_step = recommend(found, guess, confidence, status, status_p)

    L = []
    L.append(f"# Mission report: {config['name']}\n")
    L.append("## Outcome")
    L.append(f"{outcome}\n")
    L.append(f"- Actions taken: {len(trace)}")
    last = trace[-1]["observation"]
    L.append(f"- Battery left: {last['battery']}, time left: {last['time_left']}")
    L.append(f"- Recharges used: {recharges}\n")

    L.append("## Inferred location and status")
    L.append(f"- **Location:** {guess}")
    L.append(f"- **Confidence:** {confidence:.0%} (probability within 2 cells of that spot)")
    L.append(f"- **Status:** {status_text}")
    L.append("- Top three candidate cells: " + ", ".join(f"{c} {p:.0%}" for p, c in top_cells(agent.belief)) + "\n")

    L.append("## Evidence found")
    L.append(f"- Signal scans: {len(scans)}")
    for pos, strength in scans:
        L.append(f"  - scan at {pos}: strength {strength}")
    L.append(f"- Clues inspected: {len(clues)}")
    for pos, clue in clues:
        hint = tuple(clue["location_hint"])
        gap = math.dist(hint, guess)
        verdict = "consistent with the final estimate" if gap <= 3 else "far from the final estimate, probably a decoy"
        L.append(f"  - clue at {pos}: says EVE is near {hint} and {clue['status_hint']} ({verdict})")
    L.append(f"- Empty inspections: {len(empties)} {empties if empties else ''}\n")

    L.append("## Strategy timeline")
    for ph in phases(trace):
        span = f"step {ph['first']}" if ph["first"] == ph["last"] else f"steps {ph['first']}-{ph['last']}"
        L.append(f"- {span}: **{ph['mode']}** (confidence afterwards {ph['confidence']:.0%}). {ph['reason']}")
    L.append("")

    L.append("## Recommended next step")
    L.append(f"{next_step}\n")

    hidden = config.get("hidden")
    if hidden:
        truth = (hidden["eve"]["x"], hidden["eve"]["y"])
        L.append("## Evaluation (uses the hidden truth, never seen by the agent)")
        L.append(f"- True position: {truth}, agent's estimate: {guess}, error: {math.dist(truth, guess):.1f} cells")
        L.append(f"- True status: {hidden['eve']['status']}, agent's estimate: {status}")
        L.append("")

    data = {
        "mission": config["name"],
        "outcome": reason,
        "actions": len(trace),
        "inferred_location": list(guess),
        "confidence": round(confidence, 3),
        "inferred_status": status if (found or status_p > 0.5) else "unknown",
        "status_confirmed": found,
        "scans": len(scans),
        "clues_inspected": len(clues),
        "empty_inspections": len(empties),
        "recharges": recharges,
        "recommended_next_step": next_step,
    }
    return "\n".join(L), data


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "configs/mission_01.json"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "outputs/mission_01"

    result = run_mission(path)
    write_trace(result["trace"], out_dir)
    markdown, data = build_report(result)

    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write(markdown)
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(markdown)
    print(f"Saved trace.jsonl, report.md and report.json in {out_dir}")