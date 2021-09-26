import logging
import math

from flood_fill import closest, farthest, manhattan_dist
from init_game import general

logging.basicConfig(level=logging.DEBUG)

turn = 0
our_flag = 0

tiles = []
armies = []
cities = []
generals_list = []

def main():
    mode = "explore"
    main_army = (-1, -1)
    general_r, general_c = -1, -1
    rush_target = (-1, -1)
    done_exploring = False
    for state in general.get_updates():
        our_flag = state['player_index']
        try:
            general_r, general_c = state['generals'][our_flag]
            if main_army == (-1, -1):
                main_army = (general_r, general_c)
        except KeyError:
            break

        rows, cols = state['rows'], state['cols']

        turn = state['turn']
        tiles = state['tile_grid']
        armies = state['army_grid']
        cities = state['cities']
        swamps = state['swamps']
        generals_list = state['generals']

        if mode != "rush":
            if turn > 800:
                mode = "consolidate"
            # elif turn > 150:
            #     if turn % 100 < 25:
            #         mode = "consolidate"
            #     else:
            #         mode = "explore"
            else:
                mode = "explore"

            if done_exploring and mode == "explore":
                mode = "consolidate"

        print(mode)
        if mode == "explore":
            pre = []
            empty = []
            for x in range(rows):
                for y in range(cols):
                    t = tiles[x][y]
                    if t == our_flag:
                        pre.append((x, y + 1, armies[x][y]))
                        pre.append((x, y - 1, armies[x][y]))
                        pre.append((x + 1, y, armies[x][y]))
                        pre.append((x - 1, y, armies[x][y]))

            for pair in pre:
                if pair[0] < 0 or pair[0] >= rows or pair[1] < 0 or pair[1] >= cols:
                    continue
                if tiles[pair[0]][pair[1]] == -1:
                    a, b, d = closest(rows, cols, pair[0], pair[1], our_flag, tiles, armies, cities)
                    if a != -1 and b != -1 and d != -1:
                        # print(armies[a][b])
                        empty.append((pair[0], pair[1], a, b, d,
                                      manhattan_dist(rows, cols, pair[0], pair[1], general_r, general_c, tiles, cities,
                                                     our_flag)))

            moved = False
            for i in range(len(empty)):
                empty = sorted(empty, key=lambda x: (x[5]))
                best = empty[i]
                a, b = best[2:4]
                c, d = best[:2]
                if armies[a][b] == 0 or tiles[c][d] != -1:  # TODO: figure out why this is needed, tiles[c][d] should be empty
                    continue

                print(a, b, c, d)
                moves = []
                if a - 1 >= 0:
                    if tiles[a - 1][b] in (-1, our_flag):
                        moves.append((a - 1, b, manhattan_dist(rows, cols, a - 1, b, c, d, tiles, cities, our_flag)))
                if a + 1 < rows:
                    if tiles[a + 1][b] in (-1, our_flag):
                        moves.append((a + 1, b, manhattan_dist(rows, cols, a + 1, b, c, d, tiles, cities, our_flag)))
                if b - 1 >= 0:
                    if tiles[a][b - 1] in (-1, our_flag):
                        moves.append((a, b - 1, manhattan_dist(rows, cols, a, b - 1, c, d, tiles, cities, our_flag)))
                if b + 1 < cols:
                    if tiles[a][b + 1] in (-1, our_flag):
                        moves.append((a, b + 1, manhattan_dist(rows, cols, a, b + 1, c, d, tiles, cities, our_flag)))
                moves = sorted(moves, key=lambda x: x[2])
                if len(moves):
                    bm = moves[0]
                    general.move(a, b, bm[0], bm[1])
                    moved = True
                    break
            if not moved and turn % 2 == 0:
                done_exploring = True
        if mode == "consolidate":
            max_tiles = []
            max_army = 0
            for r in range(rows):
                for c in range(cols):
                    if r == general_r and c == general_c:  # ignore the army on capital
                        assert len(state["armies"]) == 2, "Assuming 1v1"
                        enemy_flag = 1 - our_flag
                        if armies[r][c] > 300 and state["armies"][enemy_flag] * 0.5 - armies[r][c] < 0:
                            mode = "rush"
                            main_army = (general_r, general_c)

                        continue

                    t = tiles[r][c]
                    if t == our_flag and armies[r][c] > 1:  # TODO: will break if all other armies are 1
                        # d = math.log(manhattan_dist(rows, cols, r, c, general_r, general_c, tiles, cities, our_flag, attack=True) * 10 + 1)
                        d = math.sqrt(manhattan_dist(rows, cols, r, c, general_r, general_c, tiles, cities, our_flag, attack=True) + 1)
                        if armies[r][c] * d > max_army:
                            max_army = armies[r][c] * d
                            max_tiles = [(r, c)]
            #             elif armies[r][c] == max_army:
            #                 max_tiles.append((r, c))
            #
            farthest_tile = max_tiles[0]
            # farthest_dist = manhattan_dist(rows, cols, farthest_tile[0], farthest_tile[1], general_r, general_c, tiles, cities, our_flag)
            # for max_tile in max_tiles[1:]:
            #     dist = manhattan_dist(rows, cols, max_tile[0], max_tile[1], general_r, general_c, tiles, cities, our_flag)
            #     if dist > farthest_dist:
            #         farthest_dist = dist
            #         farthest_tile = max_tile

            a, b = farthest_tile
            moves = []
            if a - 1 >= 0:
                if tiles[a - 1][b] in (-1, our_flag, 0 , 1):
                    moves.append(
                        (a - 1, b, manhattan_dist(rows, cols, a - 1, b, general_r, general_c, tiles, cities, our_flag, attack=True)))
            if a + 1 < rows:
                if tiles[a + 1][b] in (-1, our_flag, 0 , 1):
                    moves.append(
                        (a + 1, b, manhattan_dist(rows, cols, a + 1, b, general_r, general_c, tiles, cities, our_flag, attack=True)))
            if b - 1 >= 0:
                if tiles[a][b - 1] in (-1, our_flag, 0 , 1):
                    moves.append(
                        (a, b - 1, manhattan_dist(rows, cols, a, b - 1, general_r, general_c, tiles, cities, our_flag, attack=True)))
            if b + 1 < cols:
                if tiles[a][b + 1] in (-1, our_flag, 0 , 1):
                    moves.append(
                        (a, b + 1, manhattan_dist(rows, cols, a, b + 1, general_r, general_c, tiles, cities, our_flag, attack=True)))
            moves = sorted(moves, key=lambda x: x[2])
            if len(moves) and mode != "rush":
                bm = moves[0]
                general.move(a, b, bm[0], bm[1])
            else:
                print("out of moves, rushing")
                mode = "rush"
                main_army = (general_r, general_c)

        elif mode == "rush":
            if armies[main_army[0]][main_army[1]] < 100 and turn % 2 == 1:
                mode = "consolidate"
                main_army = (general_r, general_c)

            pre = []
            empty = []
            r, c = main_army

            assert len(state["armies"]) == 2, "Assuming 1v1"
            enemy_flag = 1 - our_flag

            if generals_list[enemy_flag] != (-1, -1):
                print(f"Enemy general found at: {generals_list[enemy_flag]}")
                rush_target = generals_list[enemy_flag]

            if rush_target == (-1, -1) or rush_target == main_army:
                far = farthest(rows, cols, our_flag, tiles, cities)
                print(f"Updating rush target to {far}")
                rush_target = far
                # for x in range(rows):
                #     for y in range(cols):
                #         t = tiles[x][y]
                #         if t == our_flag:
                #             pre.append((x, y + 1))
                #             pre.append((x, y - 1))
                #             pre.append((x + 1, y))
                #             pre.append((x - 1, y))
                #
                # for pair in pre:
                #     if pair[0] < 0 or pair[0] >= rows or pair[1] < 0 or pair[1] >= cols:
                #         continue
                #     if tiles[pair[0]][pair[1]] == -1 or (tiles[pair[0]][pair[1]] >= 0 and tiles[pair[0]][pair[1]] != our_flag):
                #         a, b, d = closest(rows, cols, pair[0], pair[1], tiles, armies, cities)
                #         if a != -1 and b != -1 and d != -1 and pair != (rush_target):
                #             empty.append((pair[0], pair[1], a, b, d,
                #                           manhattan_dist(rows, cols, pair[0], pair[1], r, c, tiles, cities,
                #                                          our_flag)))
                #
                # if len(empty):
                #     empty = sorted(empty, key=lambda x: (x[4], x[5]))
                #     best = empty[0]
                #
                # print(f"Updating rush target to {best[:2]}")
                # rush_target = best[:2]

            a, b = main_army #best[2:4]
            c, d = rush_target
            # print(a, b, c, d)
            moves = []
            if a - 1 >= 0:
                if tiles[a - 1][b] in (-1, 0, 1):
                    moves.append((a - 1, b, manhattan_dist(rows, cols, a - 1, b, c, d, tiles, cities, our_flag, attack=True)))
            if a + 1 < rows:
                if tiles[a + 1][b] in (-1, 0, 1):
                    moves.append((a + 1, b, manhattan_dist(rows, cols, a + 1, b, c, d, tiles, cities, our_flag, attack=True)))
            if b - 1 >= 0:
                if tiles[a][b - 1] in (-1, 0, 1):
                    moves.append((a, b - 1, manhattan_dist(rows, cols, a, b - 1, c, d, tiles, cities, our_flag, attack=True)))
            if b + 1 < cols:
                if tiles[a][b + 1] in (-1, 0, 1):
                    moves.append((a, b + 1, manhattan_dist(rows, cols, a, b + 1, c, d, tiles, cities, our_flag, attack=True)))

            moves = sorted(moves, key=lambda x: x[2])
            if len(moves):
                bm = moves[0]
                general.move(a, b, bm[0], bm[1])
                main_army = (bm[0], bm[1])
            else:
                assert False

if __name__ == "__main__":
    main()