def closest(r, c, x, y, our_flag, arr, armies, cities):
    vis = [[False for _ in range(c)] for _ in range(r)]
    queue = [(x, y, 0)]
    while len(queue) > 0:
        curr = queue.pop(0)
        a, b = curr[:2]
        dist = curr[2] + 1
        if vis[a][b] or arr[a][b] == -2 or (a, b) in cities:
            continue
        vis[a][b] = True
        if armies[a][b] > 1 and arr[a][b] == our_flag:
            return a, b, dist
        else:
            if a + 1 < r and not vis[a + 1][b]:
                queue.append((a + 1, b, dist))

            if a - 1 >= 0 and not vis[a - 1][b]:
                queue.append((a - 1, b, dist))

            if b + 1 < c and not vis[a][b + 1]:
                queue.append((a, b + 1, dist))

            if b - 1 >= 0 and not vis[a][b - 1]:
                queue.append((a, b - 1, dist))

    return -1, -1, -1


def farthest(rows, cols, our_flag, arr, cities):
    vis = [[False for _ in range(cols)] for _ in range(rows)]
    queue = []
    fringe = []
    for row in range(rows):
        for col in range(cols):
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
        if a + 1 < rows and not vis[a + 1][b]:
            fringe.append((a + 1, b))

        if a - 1 >= 0 and not vis[a - 1][b]:
            fringe.append((a - 1, b))

        if b + 1 < cols and not vis[a][b + 1]:
            fringe.append((a, b + 1))

        if b - 1 >= 0 and not vis[a][b - 1]:
            fringe.append((a, b - 1))

        if len(queue) == 0:
            if len(fringe) == 0:
                return a, b

            queue = [(pair[0], pair[1]) for pair in fringe]  # deepcopy
            fringe = []

    return -1, -1


def manhattan_dist(r, c, x, y, gx, gy, arr, cities, id, attack=False):
    if (not attack) and (arr[x][y] not in (-1, id) or (x, y) in cities):
        return 1000000
    elif attack and (arr[x][y] not in (-1, 0, 1) or (x, y) in cities):
        return 1000000
    queue = [(x, y, 0)]
    vis = [[False for _ in range(c)] for _ in range(r)]
    while (len(queue)):
        curr = queue[0]
        queue.pop(0)
        dist = curr[2] + 1
        a = curr[0]
        b = curr[1]
        if (vis[a][b] or arr[a][b] == -2 or (a, b) in cities):
            continue
        vis[a][b] = True
        if (a == gx and b == gy):
            return dist
        else:
            if (a + 1 < r):
                if (not vis[a + 1][b]):
                    queue.append((a + 1, b, dist))

            if (a - 1 >= 0):
                if (not vis[a - 1][b]):
                    queue.append((a - 1, b, dist))

            if (b + 1 < c):
                if (not vis[a][b + 1]):
                    queue.append((a, b + 1, dist))

            if (b - 1 >= 0):
                if (not vis[a][b - 1]):
                    queue.append((a, b - 1, dist))

    return 1000000
