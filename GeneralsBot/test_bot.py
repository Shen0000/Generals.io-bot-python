import logging
import math

from flood_fill import GeneralUtils
from init_game import general


logging.basicConfig(level=logging.DEBUG)


OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def main():
    MODE = "explore"
    main_army, scout_target, enemy_general = None, None, None
    done_exploring, done_cities = False, False

    for state in general.get_updates():
        our_flag = state['player_index']
        try:
            general_r, general_c = state['generals'][our_flag]
            if main_army is None:
                main_army = (general_r, general_c)
        except KeyError:
            break

        rows, cols = state['rows'], state['cols']
        utils = GeneralUtils(rows, cols)

        turn, tiles, armies, cities, swamps, generals_list, alive, army_size, land_size = state['turn'], state['tile_grid'], state['army_grid'], state['cities'], state['swamps'], state['generals'], state['alives'], state['armies'], state['lands']
        for i in range(len(generals_list)):
            if i != our_flag and generals_list[i] != (-1, -1) and alive[i]:
                enemy_general=generals_list[i]

        if MODE != "scout":
            if turn > 800:
                MODE = "consolidate"
            # elif turn > 150:
            #     if turn % 100 < 25:
            #         mode = "consolidate"
            #     else:
            #         mode = "explore"
            else:
                MODE = "explore"

            if done_exploring and MODE == "explore":
                MODE = "cities"
            
            if done_cities and MODE == "cities":
                MODE = "consolidate"

        print(MODE)
        if MODE == "explore":
            pre = []
            empty = []
            for r in range(rows):
                for c in range(cols):
                    if tiles[r][c] == our_flag:
                        for offset in OFFSETS:
                            pre.append((r + offset[0], c + offset[1]))

            for (r, c) in pre:
                if not utils.in_bounds(r, c) or tiles[r][c] != -1:
                    continue

                a, b, d = utils.closest(r, c, our_flag, tiles, armies, cities)
                if (a, b, d) != (-1, -1, -1):
                    empty.append((r, c, a, b, d,
                                  utils.manhattan_dist(r, c, general_r, general_c, tiles, cities, our_flag))
                                 )

            moved = False
            empty = sorted(empty, key=lambda x: (x[4], x[5]))
            for i in range(len(empty)):
                best = empty[i]
                a, b = best[2:4]
                c, d = best[:2]
                if armies[a][b] <= 1 or tiles[c][d] != -1:  # TODO: figure out why this is needed, tiles[c][d] should be empty
                    continue

                print(a, b, c, d)
                moves = []

                for offset in OFFSETS:
                    if utils.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] >= -1:
                        moves.append(
                            (a + offset[0], b + offset[1], utils.manhattan_dist(a + offset[0], b + offset[1], c, d, tiles, cities, our_flag, attack=True))
                        )

                moves = sorted(moves, key=lambda x: x[2])
                if len(moves):
                    bm = moves[0]
                    general.move(a, b, bm[0], bm[1])
                    moved = True
                    break

            if not moved and turn % 2 == 0:
                done_exploring = True

        elif MODE == "cities":
            cities.sort(key=lambda x: utils.nearest_city(x[0], x[1], general_r, general_c, tiles, our_flag))
            done=True
            for (r, c) in cities:
                if tiles[r][c]<0:
                    done=False
                    strength = armies[r][c]
                    # TODO : add check to see if we can take the city, then consolidate and take the city
                    break
            
            if done:
                done_cities=True
                break

        elif MODE == "consolidate":
            max_tiles = []
            max_army = 0
            for r in range(rows):
                for c in range(cols):
                    if r == general_r and c == general_c:  # ignore the army on capital
                        enemy_flags = []
                        for i in range(len(generals_list)):
                            if i != our_flag:
                                enemy_flags.append(i)
                        enemy_armies = [(army_size[flag], flag) for flag in enemy_flags]
                        enemy_armies.sort()
                        if armies[r][c] > 300 and enemy_armies[-1][0] * 0.5 - armies[r][c] < 0:
                            MODE = "scout"
                            main_army = (general_r, general_c)

                        continue

                    t = tiles[r][c]
                    if t == our_flag and armies[r][c] > 1:  # TODO: will break if all other armies are 1
                        # d = math.log(manhattan_dist(rows, cols, r, c, general_r, general_c, tiles, cities, our_flag, attack=True) * 10 + 1)
                        d = math.sqrt(utils.manhattan_dist(r, c, general_r, general_c, tiles, cities, our_flag, attack=True) + 1)
                        if armies[r][c] * d > max_army:
                            max_army = armies[r][c] * d
                            max_tiles = [(r, c)]

            farthest_tile = max_tiles[0]

            a, b = farthest_tile
            moves = []
            for offset in OFFSETS:
                if utils.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] >= -1:
                    moves.append(
                        (a + offset[0], b + offset[1],
                         utils.manhattan_dist(a + offset[0], b + offset[1], general_r, general_c, tiles, cities, our_flag, attack=True))
                    )

            moves = sorted(moves, key=lambda x: x[2])
            if len(moves) and MODE != "scout":
                bm = moves[0]
                general.move(a, b, bm[0], bm[1])
            else:
                print("out of moves, scouting")
                MODE = "scout"
                main_army = (general_r, general_c)

        elif MODE == "scout":
            main_army=utils.find_main(tiles, armies, our_flag) #update main army to account for server lag

            if armies[main_army[0]][main_army[1]] < 100:
                print("consolidating because not enough troops")
                MODE = "consolidate"
                main_army = (general_r, general_c)

            enemy_flags = []
            for i in range(len(generals_list)):
                if i != our_flag:
                    enemy_flags.append(i)


            for flag in enemy_flags:
                if generals_list[flag] != (-1, -1) and alive[flag]:
                    print(f"Enemy general found at: {generals_list[flag]}")
                    enemy_general = generals_list[flag]

            if scout_target is None or scout_target == main_army:
                far = utils.farthest(our_flag, tiles, cities)
                # far = utils.farthest2(general_r, general_c, our_flag, tiles, armies, cities)
                print(f"Updating scout target to {far}")
                scout_target = far

            if enemy_general is not None:
                scout_target = enemy_general

            a, b = main_army #best[2:4]
            c, d = scout_target
            print(a, b, c, d)
            moves = []
            for offset in OFFSETS:
                if utils.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] >= -1:
                    moves.append(
                        (a + offset[0], b + offset[1],
                         utils.manhattan_dist(a + offset[0], b + offset[1], c, d, tiles, cities, our_flag, attack=True))
                    )

            moves = sorted(moves, key=lambda x: x[2])
            if len(moves):
                bm = moves[0]
                general.move(a, b, bm[0], bm[1])
                main_army = (bm[0], bm[1])
            else:
                assert False


if __name__ == "__main__":
    main()