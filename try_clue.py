from environment import Environment
from belief import Belief

env = Environment("configs/mission_01.json")
b = Belief(10, 10)
b.set_prior(6, 6, 2.5)
print("start       guess:", b.best_guess(), "conf:", round(b.confidence(), 3), "status:", b.status_estimate())

for spot in [(5, 7), (8, 4)]:
    env.position = spot
    obs = env.step({"type": "inspect"})
    clue = obs["clue"]
    print("inspect at", spot, "->", clue)
    b.update_clue(clue["location_hint"][0], clue["location_hint"][1])
    b.update_status(clue["status_hint"])
    print("            guess:", b.best_guess(), "conf:", round(b.confidence(), 3), "status:", b.status_estimate())

env.position = (7, 7)
obs = env.step({"type": "inspect"})
print("inspect at (7, 7) -> found EVE?", obs["eve_found"])
b.update_negative(7, 7)
print("after empty inspect, belief at (7,7):", round(b.p[7][7], 4))
print("            guess:", b.best_guess(), "conf:", round(b.confidence(), 3))