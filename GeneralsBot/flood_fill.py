def closest(r, c, x, y, arr, armies, cities):
    vis = [[False for _ in range(c)] for _ in range(r)]
    queue=[(x, y, 0)]
    while (len(queue)>0):
        curr = queue[0]
        queue.pop(0)
        a=curr[0]
        b=curr[1]
        dist = curr[2]+1
        if (vis[a][b] or arr[a][b]==-2 or (a, b) in cities):
            continue
        vis[a][b]=True
        if (armies[a][b]>1 and (arr[a][b] >= 0)):  # should be arr[a][b] == our_flag
            return (a, b, dist)
        else:
            if (a+1<r):
                if(not vis[a+1][b]):
                    queue.append((a+1, b, dist))

            if (a-1>=0):
                if (not vis[a-1][b]):
                    queue.append((a-1, b, dist))

            if (b+1<c):
                if (not vis[a][b+1]):
                    queue.append((a, b+1, dist))

            if (b-1>=0):
                if (not vis[a][b-1]):
                    queue.append((a, b-1, dist))
    return (-1, -1, -1)


def manhattan_dist(r, c, x, y, gx, gy, arr, cities, id, attack=False):
    if (not attack) and (arr[x][y] not in (-1, id) or (x,y) in cities):
        return 1000000
    elif (not attack) and (arr[x][y] not in (-1, 0, 1) or (x,y) in cities):
        return 1000000
    queue=[(x, y, 0)]
    vis=[[False for _ in range(c)] for _ in range(r)]
    while (len(queue)):
        curr=queue[0]
        queue.pop(0)
        dist=curr[2]+1
        a=curr[0]
        b=curr[1]
        if (vis[a][b] or arr[a][b]==-2 or (a, b) in cities):
            continue
        vis[a][b]=True
        if (a==gx and b==gy):
            return dist
        else:
            if (a+1<r):
                if(not vis[a+1][b]):
                    queue.append((a+1, b, dist))

            if (a-1>=0):
                if (not vis[a-1][b]):
                    queue.append((a-1, b, dist))

            if (b+1<c):
                if (not vis[a][b+1]):
                    queue.append((a, b+1, dist))

            if (b-1>=0):
                if (not vis[a][b-1]):
                    queue.append((a, b-1, dist))

    return 1000000
