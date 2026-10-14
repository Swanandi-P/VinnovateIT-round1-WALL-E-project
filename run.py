import json
import sys

from agent import Agent
from environment import Environment

path = sys.argv[1] if len(sys.argv) > 1 else "configs/mission_01.json"
with open(path) as f:
    config = json.load(f)

# the agent gets the config WITHOUT the hidden section
briefing = {key: value for key, value in config.items() if key != "hidden"}

env = Environment(path)
agent = Agent(briefing)

step = 0
while not env.done and step < 200:
    step += 1
    action, reason = agent.decide()
    obs = env.step(action)
    agent.observe(action, obs)
    print(f"{step:>2} {str(action):<26} pos={obs['position']} battery={obs['battery']:>2} time={obs['time_left']:>3} | {reason}")

print("finished:", env.finish_reason, "| best guess:", agent.belief.best_guess(),
      "| confidence:", round(agent.belief.confidence(), 2), "| status:", agent.belief.status_estimate())