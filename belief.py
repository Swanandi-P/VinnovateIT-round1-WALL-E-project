import math


class Belief:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # every cell starts equally likely
        self.p = [[1 / (width * height) for x in range(width)] for y in range(height)]
        self.status = {"active": 1 / 3, "low_power": 1 / 3, "damaged": 1 / 3}

    def total(self):
        return sum(sum(row) for row in self.p)

    def normalise(self):
        t = self.total()
        for y in range(self.height):
            for x in range(self.width):
                self.p[y][x] = self.p[y][x] / t

    def set_prior(self, cx, cy, sigma):
        # cells near (cx, cy) get a bigger score; far cells get a smaller one
        for y in range(self.height):
            for x in range(self.width):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                self.p[y][x] = math.exp(-d2 / (2 * sigma ** 2))
        self.normalise()


    def update_scan(self, pos, strength, sigma=0.03):
        # Bayes: new belief = old belief x how well this reading fits each cell
        for y in range(self.height):
            for x in range(self.width):
                distance = math.dist(pos, (x, y))
                expected = 1 / (1 + distance)
                error = strength - expected
                likelihood = math.exp(-(error ** 2) / (2 * sigma ** 2))
                self.p[y][x] = self.p[y][x] * likelihood
        self.normalise()



    def update_clue(self, hx, hy, sigma=1.5, reliability=0.75):
        # A clue hint might be real (near EVE) or a decoy (random).
        # likelihood = real-chance x "near the hint" + decoy-chance x "anywhere is equally likely"
        flat = 1 / (self.width * self.height)
        for y in range(self.height):
            for x in range(self.width):
                d2 = (x - hx) ** 2 + (y - hy) ** 2
                near = math.exp(-d2 / (2 * sigma ** 2)) / (2 * math.pi * sigma ** 2)
                likelihood = reliability * near + (1 - reliability) * flat
                self.p[y][x] = self.p[y][x] * likelihood
        self.normalise()

    def update_negative(self, x, y, factor=0.02):
        # I looked in this cell and EVE was not there, so shrink it (but not to exactly 0)
        self.p[y][x] = self.p[y][x] * factor
        self.normalise()

    def update_status(self, hint, accuracy=0.7):
        # a status hint is right with probability `accuracy`, otherwise it is one of the other two
        for state in self.status:
            if state == hint:
                likelihood = accuracy
            else:
                likelihood = (1 - accuracy) / 2
            self.status[state] = self.status[state] * likelihood
        total = sum(self.status.values())
        for state in self.status:
            self.status[state] = self.status[state] / total

    def status_estimate(self):
        best = max(self.status, key=self.status.get)
        return best, self.status[best]

    
    def best_guess(self):
        best = (0, 0)
        best_p = -1
        for y in range(self.height):
            for x in range(self.width):
                if self.p[y][x] > best_p:
                    best_p = self.p[y][x]
                    best = (x, y)
        return best

    def confidence(self, radius=2):
        # how much probability sits within `radius` cells of the best guess
        bx, by = self.best_guess()
        mass = 0
        for y in range(self.height):
            for x in range(self.width):
                if abs(x - bx) <= radius and abs(y - by) <= radius:
                    mass += self.p[y][x]
        return mass

    def show(self):
        for row in self.p:
            print(" ".join(f"{v * 100:4.1f}" for v in row))


if __name__ == "__main__":
    import json

    with open("configs/mission_01.json") as f:
        cfg = json.load(f)
    sig = cfg["initial_signal"]
    b = Belief(cfg["map"]["width"], cfg["map"]["height"])
    print("before prior -> confidence:", round(b.confidence(), 3))
    b.set_prior(sig["x"], sig["y"], 2.5)
    print("total:", round(b.total(), 3))
    print("best guess:", b.best_guess())
    print("after prior -> confidence:", round(b.confidence(), 3))
    b.show()