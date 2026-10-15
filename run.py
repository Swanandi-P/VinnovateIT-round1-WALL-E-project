import json
import os
import sys

from agent import Agent
from environment import Environment


def run_mission(config_path, max_steps=200):
    with open(config_path) as f:
        config = json.load(f)

    # the agent gets the config WITHOUT the hidden section
    briefing = {key: value for key, value in config.items() if key != "hidden"}

    env = Environment(config_path)
    agent = Agent(briefing)

    trace = []
    step = 0
    while not env.done and step < max_steps:
        step += 1
        before = {"position": agent.position, "battery": agent.battery, "time_left": agent.time_left}
        action, reason = agent.decide()
        obs = env.step(action)
        agent.observe(action, obs)
        trace.append({
            "step": step,
            "before": before,
            "mode": agent.mode,
            "reasoning": reason,
            "action": action,
            "observation": obs,
            "belief": agent.belief_summary(),
        })

    return {"config": config, "trace": trace, "agent": agent, "finish_reason": env.finish_reason}


def write_trace(trace, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "trace.jsonl"), "w") as f:
        for entry in trace:
            f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "configs/mission_01.json"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "outputs/mission_01"

    result = run_mission(path)
    write_trace(result["trace"], out_dir)

    for entry in result["trace"]:
        obs = entry["observation"]
        print(f"{entry['step']:>2} {entry['mode']:<11} {str(entry['action']):<26} battery={obs['battery']:>2} | {entry['reasoning']}")

    agent = result["agent"]
    print("finished:", result["finish_reason"], "| best guess:", agent.belief.best_guess(),
          "| confidence:", round(agent.belief.confidence(), 2), "| status:", agent.belief.status_estimate())
    print("trace saved to", os.path.join(out_dir, "trace.jsonl"))