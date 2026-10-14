import json
import math
import random


class Environment:
    def __init__(self, config_path):
        # Read the mission file into a Python dictionary (a lookup table)
        with open(config_path) as file:
            config = json.load(file)

        # Things the agent is allowed to know
        self.width = config["map"]["width"]
        self.height = config["map"]["height"]
        self.position = tuple(config["map"]["start"])
        self.battery = config["resources"]["battery"]
        self.time_left = config["resources"]["time"]
        self.costs = config["resources"]["costs"]
        self.max_battery = self.battery
        self.recharge_amount = config["resources"]["recharge_amount"]
        self.stations = {}
        for station in config["map"]["stations"]:
            self.stations[tuple(station["pos"])] = station["uses"]
        self.done = False
        self.finish_reason = None
        self.scan_noise = config["sensors"]["scan_noise"]
        self.clue_noise = config["sensors"]["clue_noise"]
        self.clue_status_accuracy = config["sensors"]["clue_status_accuracy"]
        self.rng = random.Random(config["seed"])

        # The hidden truth. The underscore means "private: the agent must not touch this"
        self._eve_position = (config["hidden"]["eve"]["x"], config["hidden"]["eve"]["y"])
        self._eve_status = config["hidden"]["eve"]["status"]
        self._clues = {}
        for clue in config["hidden"]["clues"]:
            self._clues[(clue["x"], clue["y"])] = clue["genuine"]
        self._collected = set()


    def move(self, direction):
        steps = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        dx, dy = steps[direction]
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        bumped = True
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            self.position = (new_x, new_y)
            bumped = False

        self.battery -= self.costs["move"]["battery"]
        self.time_left -= self.costs["move"]["time"]

        return {
            "action": "move",
            "position": self.position,
            "bumped": bumped,
            "battery": self.battery,
            "time_left": self.time_left,
        }    

    def scan(self):
        distance = math.dist(self.position, self._eve_position)
        true_strength = 1 / (1 + distance)
        noise = self.rng.gauss(0, self.scan_noise)
        strength = max(0.0, min(1.0, true_strength + noise))

        # a scan also "pings" any clue within 3 cells that has not been collected yet
        pings = []
        for clue_pos in self._clues:
            if clue_pos not in self._collected and math.dist(self.position, clue_pos) <= 3:
                pings.append(clue_pos)

        self.battery -= self.costs["scan"]["battery"]
        self.time_left -= self.costs["scan"]["time"]

        return {
            "action": "scan",
            "position": self.position,
            "strength": round(strength, 3),
            "pings": pings,
            "battery": self.battery,
            "time_left": self.time_left,
        }


    def inspect(self):
        result = {
            "action": "inspect",
            "position": self.position,
            "eve_found": False,
            "clue": None,
        }

        if self.position == self._eve_position:
            result["eve_found"] = True
            result["eve_status"] = self._eve_status

        elif self.position in self._clues and self.position not in self._collected:
            self._collected.add(self.position)
            genuine = self._clues[self.position]
            statuses = ["active", "low_power", "damaged"]

            if genuine:
                hint_x = round(self._eve_position[0] + self.rng.gauss(0, self.clue_noise))
                hint_y = round(self._eve_position[1] + self.rng.gauss(0, self.clue_noise))
                if self.rng.random() < self.clue_status_accuracy:
                    status_hint = self._eve_status
                else:
                    wrong = []
                    for s in statuses:
                        if s != self._eve_status:
                            wrong.append(s)
                    status_hint = self.rng.choice(wrong)
            else:
                hint_x = self.rng.randrange(self.width)
                hint_y = self.rng.randrange(self.height)
                status_hint = self.rng.choice(statuses)

            hint_x = max(0, min(self.width - 1, hint_x))
            hint_y = max(0, min(self.height - 1, hint_y))
            result["clue"] = {
                "location_hint": (hint_x, hint_y),
                "status_hint": status_hint,
            }

        self.battery -= self.costs["inspect"]["battery"]
        self.time_left -= self.costs["inspect"]["time"]
        result["battery"] = self.battery
        result["time_left"] = self.time_left
        return result


    def recharge(self):
        uses_left = self.stations.get(self.position, 0)
        if uses_left > 0:
            self.battery = min(self.max_battery, self.battery + self.recharge_amount)
            self.stations[self.position] = uses_left - 1
            self.time_left -= self.costs["recharge"]["time"]
            ok = True
        else:
            ok = False  # not at a working station: nothing happens, nothing is charged

        return {
            "action": "recharge",
            "position": self.position,
            "ok": ok,
            "battery": self.battery,
            "time_left": self.time_left,
        }

    def step(self, action):
        if self.done:
            raise RuntimeError("the mission is already over")

        kind = action["type"]
        if kind == "move":
            obs = self.move(action["dir"])
        elif kind == "scan":
            obs = self.scan()
        elif kind == "inspect":
            obs = self.inspect()
            if obs["eve_found"]:
                self.done = True
                self.finish_reason = "eve_found"
        elif kind == "recharge":
            obs = self.recharge()
        elif kind == "end":
            self.done = True
            self.finish_reason = "agent_ended"
            obs = {
                "action": "end",
                "position": self.position,
                "battery": self.battery,
                "time_left": self.time_left,
            }
        else:
            raise ValueError("unknown action: " + str(kind))

        self.battery = max(0, self.battery)
        self.time_left = max(0, self.time_left)
        obs["battery"] = self.battery
        obs["time_left"] = self.time_left

        if not self.done:
            if self.battery <= 0:
                self.done = True
                self.finish_reason = "battery_depleted"
            elif self.time_left <= 0:
                self.done = True
                self.finish_reason = "time_expired"

        obs["done"] = self.done
        obs["finish_reason"] = self.finish_reason
        return obs

if __name__ == "__main__":
    env = Environment("configs/mission_01.json")
    print(env.step({"type": "move", "dir": "E"}))
    print(env.step({"type": "recharge"}))  # at (1, 0): no station here
    env.position = (0, 0)  # testing shortcuts: teleport and drain the battery
    env.battery = 20
    print(env.step({"type": "recharge"}))
    print(env.step({"type": "recharge"}))
    print(env.step({"type": "recharge"}))  # the station is used up
    env.battery = 1
    print(env.step({"type": "scan"}))  # costs 3, so the battery hits 0