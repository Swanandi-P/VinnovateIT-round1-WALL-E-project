import json


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

        # The hidden truth. The underscore means "private: the agent must not touch this"
        self._eve_position = (config["hidden"]["eve"]["x"], config["hidden"]["eve"]["y"])
        self._eve_status = config["hidden"]["eve"]["status"]
        self._clues = []
        for clue in config["hidden"]["clues"]:
            self._clues.append((clue["x"], clue["y"]))


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


if __name__ == "__main__":
    env = Environment("configs/mission_01.json")
    print(env.move("E"))
    print(env.move("N"))