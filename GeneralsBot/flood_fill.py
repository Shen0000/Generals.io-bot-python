OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
OBSTACLES = [-2, -4]


class GeneralUtils:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def closest(self, r, c, our_flag, tiles, armies, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = [(r, c, 0)]
        while len(queue):
            curr = queue.pop(0)
            a, b = curr[:2]
            dist = curr[2] + 1
            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                continue
            vis[a][b] = True
            if armies[a][b] > 1 and tiles[a][b] == our_flag:
                return a, b, dist
            else:
                for offset in OFFSETS:
                    if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                        queue.append((a+offset[0], b+offset[1], dist))

        return -1, -1, -1


    def farthest2(self, r, c, our_flag, tiles, armies, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = [(r, c, 0)]
        prev_valid_tile = None  # TODO: change to (-1, -1)
        while len(queue) > 0:
            curr = queue.pop(0)
            a, b = curr[:2]
            dist = curr[2] + 1 # armies[r][c] - 1
            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                continue

            vis[a][b] = True
            if tiles[a][b] != our_flag:
                prev_valid_tile = (a, b)

            for offset in OFFSETS:
                if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                    queue.append((a+offset[0], b+offset[1], dist))

            if len(queue) == 1:
                curr = queue.pop(0)
                a, b = curr[:2]
                return a, b

        return prev_valid_tile


    def farthest(self, our_flag, tiles, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = []
        fringe = []
        for row in range(self.rows):
            for col in range(self.cols):
                if tiles[row][col] == our_flag:
                    queue.append((row, col))
                elif tiles[row][col] in OBSTACLES or (row, col) in cities:
                    vis[row][col] = True

        while True:
            a, b = queue.pop(0)
            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                if len(queue) == 0:
                    if len(fringe) == 0:
                        return a, b

                    queue = [(pair[0], pair[1]) for pair in fringe]  # deepcopy
                    fringe = []
                continue

            vis[a][b] = True

            for offset in OFFSETS:
                if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                    fringe.append((a+offset[0], b+offset[1]))

            if len(queue) == 0:
                if len(fringe) == 0:
                    return a, b

                queue = [(pair[0], pair[1]) for pair in fringe]  # deepcopy
                fringe = []

        return -1, -1

    def manhattan_dist(self, r, c, tr, tc, tiles, cities, id, attack=False):
        if (not attack) and (tiles[r][c] not in (-1, id) or (r, c) in cities):
            return 1000000
        elif attack and (tiles[r][c] in OBSTACLES or (r, c) in cities):
            return 1000000
        queue = [(r, c, 0)]
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        while len(queue):
            curr = queue.pop(0)
            dist = curr[2] + 1
            a , b = curr[:2]
            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                continue
            vis[a][b] = True
            if a == tr and b == tc:
                return dist
            else:
                for offset in OFFSETS:
                    if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                        queue.append((a+offset[0], b+offset[1], dist))

        return 1000000

    def nearest_city(self, r, c, tr, tc, tiles, cities):
        queue = [(r, c, 0)]
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        while len(queue):
            curr = queue.pop(0)
            dist = curr[2] + 1
            a , b = curr[:2]
            if vis[a][b] or tiles[a][b] in OBSTACLES or ((a, b) in cities and (a, b) != (r, c)):
                continue
            vis[a][b] = True
            if a == tr and b == tc:
                return dist
            else:
                for offset in OFFSETS:
                    if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                        queue.append((a+offset[0], b+offset[1], dist))

        return 1000000

    def find_main(self, tiles, armies, id):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        max_r=-1
        max_c=-1
        max=0
        for r in range(self.rows):
            for c in range(self.cols):
                if tiles[r][c]==id:
                    if armies[r][c]>max:
                        max_r=r
                        max_c=c
                        max=armies[r][c]
        return max_r, max_c
                

    def in_bounds(self, r=0, c=0):
        return 0 <= r < self.rows and 0 <= c < self.cols
