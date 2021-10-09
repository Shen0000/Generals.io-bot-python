import random

MIN, MAX = 15, 30

def create_map(length, width, city_density, swamp_density):
    grid = []
    rows, cols = 0, 0
    rows = MIN + int(MIN*length) + random.randint(-2, 2)
    cols = MIN + int(MIN*width) + random.randint(-2, 2)
    rows = min( max(rows, MIN), MAX) # make sure everything is in bounds
    cols = min( max(cols, MIN), MAX)
    print(rows, cols)
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            grid[i].append(-1)
    for row in grid:
        print(row)

if __name__ == "__main__":
    length = 0.75
    width = 0.75
    city_density = 0
    swamp_density = 0
    create_map(length, width, city_density, swamp_density)

