import math
from belief import Belief

COMMIT = 0.75  # how sure I must be (0 to 1) before I go and inspect my best guess


class Agent:
    def __init__(self, briefing):
        # the briefing is everything the agent is allowed to know (never the hidden part)
        self.width = briefing["map"]["width"]
        self.height = briefing["map"]["height"]
        self.position = tuple(briefing["map"]["start"])
        self.battery = briefing["resources"]["battery"]
        self.time_left = briefing["resources"]["time"]

        signal = briefing["initial_signal"]
        self.belief = Belief(self.width, self.height)
        self.belief.set_prior(signal["x"], signal["y"], 2.5)

        self.scan_spots = []      # where I have scanned from
        self.pings = set()        # clue positions I heard about but have not inspected yet
        self.inspected = set()    # cells I have already inspected
        self.need_rescan = False  # set after an empty inspect
        self.found = False

    # ---------- learning from what happened ----------
    def observe(self, action, obs):
        self.position = tuple(obs["position"])
        self.battery = obs["battery"]
        self.time_left = obs["time_left"]

        if action["type"] == "scan":
            self.belief.update_scan(self.position, obs["strength"])
            self.scan_spots.append(self.position)
            for p in obs["pings"]:
                if tuple(p) not in self.inspected:
                    self.pings.add(tuple(p))
            self.need_rescan = False

        elif action["type"] == "inspect":
            self.inspected.add(self.position)
            self.pings.discard(self.position)
            if obs["eve_found"]:
                self.found = True
                # I can see her condition with my own eyes now, so no more guessing
                for state in self.belief.status:
                    self.belief.status[state] = 1.0 if state == obs["eve_status"] else 0.0
            elif obs["clue"] is not None:
                hx, hy = obs["clue"]["location_hint"]
                self.belief.update_clue(hx, hy)
                self.belief.update_status(obs["clue"]["status_hint"])
            else:
                self.belief.update_negative(self.position[0], self.position[1])
                self.need_rescan = True

    # ---------- choosing the next action ----------
    def decide(self):
        confidence = self.belief.confidence()
        guess = self.belief.best_guess()

        if self.need_rescan:
            return {"type": "scan"}, "My last inspect found nothing, so my belief was wrong. Scan again for fresh data."

        if not self.scanned_near_here():
            return {"type": "scan"}, "I am at a new spot with no scan nearby. Scan to gather evidence."

        if confidence < COMMIT and self.pings:
            target = self.nearest(self.pings)
            if self.position == target:
                return {"type": "inspect"}, f"A clue was pinged here {target}. Inspect it."
            return self.step_towards(target), f"I am unsure (confidence {confidence:.2f}) and heard a clue at {target}. Walk to it."

        if confidence >= COMMIT:
            if self.position == guess:
                return {"type": "inspect"}, f"Confident ({confidence:.2f}) and standing on my best guess {guess}. Inspect for EVE."
            return self.step_towards(guess), f"Confident ({confidence:.2f}) EVE is near {guess}. Walk there."

        target = self.pick_explore_target()
        return self.step_towards(target), f"Unsure (confidence {confidence:.2f}). Walk towards {target} for a new scan angle."

    # ---------- helpers ----------
    def scanned_near_here(self):
        for spot in self.scan_spots:
            if math.dist(spot, self.position) < 3:
                return True
        return False

    def nearest(self, cells):
        return min(cells, key=lambda c: math.dist(c, self.position))

    def pick_explore_target(self):
        best_cell = self.position
        best_score = -1
        for y in range(self.height):
            for x in range(self.width):
                # only consider places that are far from everywhere I already scanned
                if any(math.dist(s, (x, y)) < 3 for s in self.scan_spots):
                    continue
                mass = 0
                for yy in range(max(0, y - 2), min(self.height, y + 3)):
                    for xx in range(max(0, x - 2), min(self.width, x + 3)):
                        mass += self.belief.p[yy][xx]
                score = mass / (1 + 0.12 * math.dist(self.position, (x, y)))
                if score > best_score:
                    best_score = score
                    best_cell = (x, y)
        return best_cell

    def step_towards(self, target):
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        if dx != 0 and (abs(dx) >= abs(dy) or dy == 0):
            direction = "E" if dx > 0 else "W"
        else:
            direction = "S" if dy > 0 else "N"
        return {"type": "move", "dir": direction}