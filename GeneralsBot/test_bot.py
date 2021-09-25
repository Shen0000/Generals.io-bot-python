from flood_fill import closest, manhattan_dist
from init_game import general
import logging
from generals_client import generals
import math

INF = 1e9

enemy_capital_value=INF
enemy_city_value=100
empty_city_value=INF
our_city_value=10
empty_tile_value=4
enemy_tile_value=2

logging.basicConfig(level=logging.DEBUG)

turn=0
rows=40
cols=40
our_flag=0

general_y, general_x =0,0
general_position=(general_x,general_y)
tiles=[]
armies=[]
cities=[]
generals_list=[]

def get_distance(position1,position2):
    return abs(position1[0]-position2[0])+abs(position1[1]-position2[1])

def how_far_from_general(position):
    return (get_distance(position, general_position))

mode="explore"


for state in general.get_updates():
    our_flag = state['player_index']
    try:
        general_x, general_y = state['generals'][our_flag]
    except KeyError:
        break

    rows, cols = state['rows'], state['cols']

    turn = state['turn']
    tiles = state['tile_grid']
    armies = state['army_grid']
    cities = state['cities']
    swamps = state['swamps']
    generals_list = state['generals']
    print(state)
    if mode=="explore":
        pre=[]
        empty=[]
        best=[]
        for x in range(rows):
            for y in range(cols):
                t = tiles[x][y]
                if t==1 or t==0:
                    pre.append((x, y+1))
                    pre.append((x, y-1))
                    pre.append((x+1, y))
                    pre.append((x-1, y))

        for pair in pre:
            if pair[0]<0 or pair[0]>=rows or pair[1]<0 or pair[1]>=cols:
                continue
            if tiles[pair[0]][pair[1]]==-1:
                a, b, d = closest(rows, cols, pair[0], pair[1], tiles, armies, cities)
                if (a!=-1 and b!=-1 and d!=-1):
                    empty.append((pair[0], pair[1], a, b, d, manhattan_dist(rows, cols, pair[0], pair[1], general_x, general_y, tiles, cities, our_flag)))

        if (len(empty)):
            empty = sorted(empty, key=lambda x: (x[4], x[5]))
            best = empty[0]
            a=best[2]
            b=best[3]
            c=best[0]
            d=best[1]
            print(a, b)
            print(c, d)
            moves=[]
            if (a-1>=0):
                if (tiles[a-1][b] in (-1, our_flag)):
                    moves.append((a-1, b, manhattan_dist(rows, cols, a-1, b, c, d, tiles, cities, our_flag)))
            if (a+1<rows):
                if (tiles[a+1][b] in (-1, our_flag)):
                    moves.append((a+1, b, manhattan_dist(rows, cols, a+1, b, c, d, tiles, cities, our_flag)))
            if (b-1>=0):
                if (tiles[a][b-1] in (-1, our_flag)):
                    moves.append((a, b-1, manhattan_dist(rows, cols, a, b-1, c, d, tiles, cities, our_flag)))
            if (b+1<cols):
                if (tiles[a][b+1] in (-1, our_flag)):
                    moves.append((a, b+1, manhattan_dist(rows, cols, a, b+1, c, d, tiles, cities, our_flag)))
            moves = sorted(moves, key=lambda x: x[2])
            if (len(moves)):
                bm = moves[0]
                general.move(a, b, bm[0], bm[1])