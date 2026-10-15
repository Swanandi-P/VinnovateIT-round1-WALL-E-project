def ascii_map(config, trace, agent):
    """Top-down map of the mission: path, scan spots, clues, stations, and the answer."""
    width = config["map"]["width"]
    height = config["map"]["height"]
    grid = [["." for x in range(width)] for y in range(height)]

    # every cell the robot stood on
    path = [tuple(config["map"]["start"])]
    for entry in trace:
        path.append(tuple(entry["observation"]["position"]))
    for x, y in path:
        grid[y][x] = "+"

    # charging stations
    for station in config["map"]["stations"]:
        x, y = station["pos"]
        grid[y][x] = "S"

    # clues (this uses the hidden truth, so it is an evaluation view)
    hidden = config.get("hidden")
    if hidden:
        for clue in hidden["clues"]:
            pos = (clue["x"], clue["y"])
            if pos in agent.inspected:
                grid[pos[1]][pos[0]] = "c" if clue["genuine"] else "d"
            else:
                grid[pos[1]][pos[0]] = "?"

    # places where the agent scanned
    for x, y in agent.scan_spots:
        if grid[y][x] in ".+":
            grid[y][x] = "s"

    # the agent's final estimate (M) and, for evaluation, EVE's true position (E)
    gx, gy = agent.belief.best_guess()
    grid[gy][gx] = "M"
    if hidden:
        ex, ey = hidden["eve"]["x"], hidden["eve"]["y"]
        grid[ey][ex] = "X" if (gx, gy) == (ex, ey) else "E"

    # where the robot ended up
    fx, fy = path[-1]
    if grid[fy][fx] in ".+sS":
        grid[fy][fx] = "@"

    header = "    " + "".join(str(x % 10) for x in range(width))
    rows = [f"{y:>2} |" + "".join(grid[y]) + "|" for y in range(height)]
    return "\n".join([header] + rows)


LEGEND = ("S station, + path, s scan spot, c genuine clue found, d decoy found, "
          "? clue never found, M agent's final estimate, E EVE's true position, "
          "X estimate exactly on EVE, @ final position")