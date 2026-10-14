from environment import Environment

env = Environment("configs/mission_01.json")
for spot in [(0, 0), (6, 6), (8, 2)]:
    env.position = spot
    obs = env.step({"type": "scan"})
    print("scan at", spot, "-> pings:", obs["pings"])
env.position = (5, 7)
env.step({"type": "inspect"})
env.position = (6, 6)
obs = env.step({"type": "scan"})
print("after collecting the clue at (5, 7), scan at (6, 6) -> pings:", obs["pings"])