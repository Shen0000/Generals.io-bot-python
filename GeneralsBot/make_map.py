import random

MIN, MAX = 15, 30

def flood(grid, flag):
    pass

def create_map(data):
    length, width, city_density, swamp_density, mountain_density, num_players = data
    grid = []
    cities = []
    rows, cols = 0, 0
    rows = MIN + int(MIN*length) + random.randint(-2, 2)
    cols = MIN + int(MIN*width) + random.randint(-2, 2)
    rows = min( max(rows, MIN), MAX) # make sure everything is in bounds
    cols = min( max(cols, MIN), MAX)
    print(rows, cols)
    for i in range(rows):
        grid.append([-1 for j in range(cols)])
    num_mountains = int(100 * mountain_density) + int((length + width)/2 * 40) + random.randint(-5, 5)
    num_cities = int(10 * city_density) * num_players + random.randint(0, num_players)
    print(num_mountains)
    print(num_cities)
    filled = set()
    cnt = 0
    while cnt < num_mountains:
        rand = random.randint(0, rows*cols-1)
        if rand not in filled:
            filled.add(rand)
            grid[rand // cols][rand % cols] = -2
            cnt+=1
    cnt = 0
    while cnt < num_cities:
        rand = random.randint(0, rows*cols-1)
        if rand not in filled:
            filled.add(rand)
            cities.append((rand // cols, rand % cols))
            cnt+=1
    tot = 0
    for row in grid:
        print(row)
        for n in row:
            if n==-2:
                tot+=1
    #print(tot)
    print(cities)
    
    return grid

def valid(grid):
    return True

if __name__ == "__main__":
    length = 0.75
    width = 0.75
    city_density = 1
    swamp_density = 0
    mountain_density = 0.5
    num_players = 2
    data = [length, width, city_density, swamp_density, mountain_density, num_players]
    grid = create_map(data)
    while not valid(grid):
        grid = create_map(data)

'''
Testing:
135 mountains for 1x mountains and 1 x 1 board
112 mountains for 1x mountains and 0.75 x 0.75 board
108 mountains for 1x mountains and 0.5 x 0.5 board
103 mountains for 1x mountains and 0 x 0 board
Result:
num_mountains is approximately 100 + (mountain_density) * 40

Testing:
20 cities for 1x cities and 0 x 0 board
20 cities for 1x cities and 0.25 x 0.25 board
all others were about 20 as well
Result:
num_cities is approximately (10 * city_density) x the number of players

'''
