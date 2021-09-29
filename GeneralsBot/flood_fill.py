OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
OBSTACLES = [-2, -4]


class GeneralUtils:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def closest(self, r, c, our_flag, tiles, armies, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = [(r, c, 0)]
        while len(queue) > 0:
            curr = queue.pop(0)
            a, b = curr[:2]
            dist = curr[2] + 1
            if vis[a][b] or tiles[a][b] == -2 or (a, b) in cities:
                continue
            vis[a][b] = True
            if armies[a][b] > 1 and tiles[a][b] == our_flag:
                return a, b, dist
            else:
                if a + 1 < self.rows and not vis[a + 1][b]:
                    queue.append((a + 1, b, dist))

                if a - 1 >= 0 and not vis[a - 1][b]:
                    queue.append((a - 1, b, dist))

                if b + 1 < self.cols and not vis[a][b + 1]:
                    queue.append((a, b + 1, dist))

                if b - 1 >= 0 and not vis[a][b - 1]:
                    queue.append((a, b - 1, dist))

        return -1, -1, -1

    def farthest4(self, r, c, our_flag, arr, armies, cities):
        dists = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        prev_tile = [[(-1, -1) for _ in range(self.cols)] for _ in range(self.rows)]
        fringe_lvls = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]

        dists[r][c] = armies[r][c]
        fringe_lvls[r][c] = 0
        fringe_level = 1

        queue = []
        fringe = []

        for offset in OFFSETS:
            adj_r = r + offset[0]
            adj_c = c + offset[1]
            if self.in_bounds(adj_r, adj_c) and not (arr[adj_r][adj_c] in OBSTACLES or (adj_r, adj_c) in cities):
                # dists[adj_r][adj_c] = armies[r][c]
                queue.append((adj_r, adj_c))

        while len(queue) > 0:
            a, b = queue.pop(0)
            if fringe_lvls[a][b] > -1 or arr[a][b] in OBSTACLES or (a, b) in cities:
                if len(queue) == 0 and len(fringe) > 0:
                    #queue = [(pair[0], pair[1]) for pair in fringe]  # deepcopy
                    queue = fringe
                    fringe = []
                    fringe_level += 1
                continue

            fringe_lvls[a][b] = fringe_level

            max_dist = 0
            adj_tile = (-1, -1)
            for offset in OFFSETS:
                adj_r = a + offset[0]
                adj_c = b + offset[1]
                if self.in_bounds(adj_r, adj_c) and not (arr[adj_r][adj_c] in OBSTACLES or (adj_r, adj_c) in cities):
                    if fringe_lvls[adj_r][adj_c] == -1:
                        fringe.append((adj_r, adj_c))
                    elif fringe_lvls[adj_r][adj_c] - fringe_level == -1 and max_dist < dists[adj_r][adj_c]:
                        max_dist = dists[adj_r][adj_c]
                        adj_tile = (adj_r, adj_c)
                    # fringe_lvls[adj_r][adj_c] = fringe_level

            dists[a][b] = max_dist + armies[a][b] - 1
            prev_tile[a][b] = adj_tile

            if len(queue) == 0 and len(fringe) > 0:
                queue = fringe #[(pair[0], pair[1]) for pair in fringe]  # deepcopy
                fringe = []
                fringe_level += 1

        max_dist = -1
        max_r, max_c = -1, -1
        for a in range(self.rows):
            for b in range(self.cols):
                if arr[a][b] == our_flag and dists[a][b] > max_dist:
                    max_r = a
                    max_c = b
                    max_dist = dists[a][b]

        max_path = [(max_r, max_c)]
        a = max_r
        b = max_c

        while (a, b) != (r, c):
            a, b = prev_tile[a][b]
            max_path.append((a, b))

        return max_path

    def farthest3(self, r, c, our_flag, tiles, armies, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = [(r, c, 0)]
        max_army = -1
        max_tile = None  # TODO: change to (-1, -1)
        while len(queue) > 0:
            curr = queue.pop(0)
            a, b = curr[:2]
            dist = curr[2] + armies[r][c] - 1
            if vis[a][b] or tiles[a][b] in (-2, -4) or (a, b) in cities:
                continue

            vis[a][b] = True
            if tiles[a][b] != our_flag and dist > max_army:
                max_tile = (a, b)

            for offset in OFFSETS:
                if self.in_bounds(a + offset[0], b + offset[1]) and not vis[a + offset[0]][b + offset[1]]:
                    queue.append((a + offset[0], b + offset[1], dist))

            if len(queue) == 1:
                curr = queue.pop(0)
                a, b = curr[:2]
                return a, b

        return max_tile

    def farthest2(self, r, c, our_flag, tiles, armies, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = [(r, c, 0)]
        prev_valid_tile = None  # TODO: change to (-1, -1)
        while len(queue) > 0:
            curr = queue.pop(0)
            a, b = curr[:2]
            dist = curr[2] + 1# armies[r][c] - 1
            if vis[a][b] or tiles[a][b] in (-2, -4) or (a, b) in cities:
                continue

            vis[a][b] = True
            if tiles[a][b] != our_flag:
                prev_valid_tile = (a, b)

            for offset in OFFSETS:
                if self.in_bounds(a + offset[0], b + offset[1]) and not vis[a + offset[0]][b + offset[1]]:
                    queue.append((a + offset[0], b + offset[1], dist))

            if len(queue) == 1:
                curr = queue.pop(0)
                a, b = curr[:2]
                return a, b

        return prev_valid_tile

    def farthest(self, our_flag, arr, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = []
        fringe = []
        for row in range(self.rows):
            for col in range(self.cols):
                if arr[row][col] == our_flag:
                    queue.append((row, col))
                elif arr[row][col] in (-4, -2) or (row, col) in cities:
                    vis[row][col] = True

        while True:
            a, b = queue.pop(0)
            if vis[a][b] or arr[a][b] == -2 or (a, b) in cities:
                if len(queue) == 0:
                    if len(fringe) == 0:
                        return a, b

                    queue = [(pair[0], pair[1]) for pair in fringe]  # deepcopy
                    fringe = []
                continue

            vis[a][b] = True
            if a + 1 < self.rows and not vis[a + 1][b]:
                fringe.append((a + 1, b))

            if a - 1 >= 0 and not vis[a - 1][b]:
                fringe.append((a - 1, b))

            if b + 1 < self.cols and not vis[a][b + 1]:
                fringe.append((a, b + 1))

            if b - 1 >= 0 and not vis[a][b - 1]:
                fringe.append((a, b - 1))

            if len(queue) == 0:
                if len(fringe) == 0:
                    return a, b

                queue = [(pair[0], pair[1]) for pair in fringe]  # deepcopy
                fringe = []

        return -1, -1

    def manhattan_dist(self, r, c, tr, tc, arr, cities, id, attack=False):
        if (not attack) and (arr[r][c] not in (-1, id) or (r, c) in cities):
            return 1000000
        elif attack and (arr[r][c] in OBSTACLES or (r, c) in cities):
            return 1000000
        queue = [(r, c, 0)]
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        while len(queue):
            curr = queue.pop(0)
            dist = curr[2] + 1
            a , b = curr[:2]
            if vis[a][b] or arr[a][b] in OBSTACLES or (a, b) in cities:
                continue
            vis[a][b] = True
            if a == tr and b == tc:
                return dist
            else:
                for offset in OFFSETS:
                    if self.in_bounds(a + offset[0], b + offset[1]) and arr[a + offset[0]][b + offset[1]] not in OBSTACLES:
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
