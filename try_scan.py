from environment import Environment
from belief import Belief

env = Environment("configs/mission_01.json")
b = Belief(10, 10)
b.set_prior(6, 6, 2.5)
print("start  best guess:", b.best_guess(), "confidence:", round(b.confidence(), 3))

for spot in [(0, 0), (9, 0), (0, 9), (9, 9)]:
    env.position = spot
    obs = env.step({"type": "scan"})
    b.update_scan(spot, obs["strength"])
    print("scan at", spot, "strength", obs["strength"],
          "-> best guess:", b.best_guess(), "confidence:", round(b.confidence(), 3))

b.show()