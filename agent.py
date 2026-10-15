import math
from belief import Belief

COMMIT = 0.75        # how sure I must be (0 to 1) before I go and inspect my best guess
LOW_BATTERY = 0.6    # recharge when below this fraction of a full battery (if on a station)
SAFETY_MARGIN = 6    # spare battery and time I always keep when planning the trip home


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

        self.max_battery = self.battery
        self.start = self.position
        self.move_cost = briefing["resources"]["costs"]["move"]
        self.stations = {}  # station position -> uses I believe are left
        for station in briefing["map"]["stations"]:
            self.stations[tuple(station["pos"])] = station["uses"]
        self.returning = False  # True while I am heading back to safety
        self.mode = "start"     # a short label for what I am doing (used in the trace)

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

        elif action["type"] == "recharge":
            if obs["ok"]:
                self.stations[self.position] -= 1
                self.returning = False  # topped up, so I can go exploring again

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

        # --- survival rules come first ---
        uses_here = self.stations.get(self.position, 0)
        if uses_here > 0 and self.battery < LOW_BATTERY * self.max_battery:
            self.mode = "recharge"
            return {"type": "recharge"}, f"I am on a station with {uses_here} use(s) left and my battery is low ({self.battery}). Recharge."

        safe_point = self.nearest_safe_point()
        moves_home = abs(safe_point[0] - self.position[0]) + abs(safe_point[1] - self.position[1])
        battery_needed = moves_home * self.move_cost["battery"] + SAFETY_MARGIN
        time_needed = moves_home * self.move_cost["time"] + SAFETY_MARGIN
        if not self.returning and (self.battery < battery_needed or self.time_left < time_needed):
            self.returning = True
        if self.returning:
            if self.position == safe_point:
                self.mode = "end"
                return {"type": "end"}, f"I am at the safe point {safe_point}, resources are low and nothing more to recharge. End the mission safely."
            self.mode = "turn_back"
            return self.step_towards(safe_point), f"Resources are low (battery {self.battery}, time {self.time_left}). Turn back towards the safe point {safe_point}."

        if self.need_rescan:
            self.mode = "rescan"
            return {"type": "scan"}, "My last inspect found nothing, so my belief was wrong. Scan again for fresh data."

        if not self.scanned_near_here():
            self.mode = "scan"
            return {"type": "scan"}, "I am at a new spot with no scan nearby. Scan to gather evidence."

        if confidence < COMMIT and self.pings:
            target = self.nearest(self.pings)
            self.mode = "follow_clue"
            if self.position == target:
                return {"type": "inspect"}, f"A clue was pinged here {target}. Inspect it."
            return self.step_towards(target), f"I am unsure (confidence {confidence:.2f}) and heard a clue at {target}. Walk to it."

        if confidence >= COMMIT:
            self.mode = "commit"
            if self.position == guess:
                return {"type": "inspect"}, f"Confident ({confidence:.2f}) and standing on my best guess {guess}. Inspect for EVE."
            return self.step_towards(guess), f"Confident ({confidence:.2f}) EVE is near {guess}. Walk there."

        self.mode = "explore"
        target = self.pick_explore_target()
        return self.step_towards(target), f"Unsure (confidence {confidence:.2f}). Walk towards {target} for a new scan angle."

    def belief_summary(self):
        # a small snapshot of what I currently believe (written into the trace)
        status = {}
        for state, p in self.belief.status.items():
            status[state] = round(p, 3)
        return {
            "best_guess": self.belief.best_guess(),
            "confidence": round(self.belief.confidence(), 3),
            "entropy": round(self.belief.entropy(), 3),
            "status": status,
        }

    # ---------- helpers ----------
    def scanned_near_here(self):
        for spot in self.scan_spots:
            if math.dist(spot, self.position) < 3:
                return True
        return False

    def nearest_safe_point(self):
        # the closest station that still has uses left, otherwise home
        options = [pos for pos, uses in self.stations.items() if uses > 0]
        if not options:
            return self.start
        return self.nearest(options)

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