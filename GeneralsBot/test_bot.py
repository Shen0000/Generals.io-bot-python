import logging
import math

from flood_fill import GeneralUtils
from init_game import general


logging.basicConfig(level=logging.DEBUG)


OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def main():
    mode = "explore"
    main_army, enemy_general = None, None
    mode_settings = {"explore": {"complete": False}, "consolidate": {"queued_path": []}, "cities": {"queued_path": []}, "scout": {"scout_target": None}}

    for state in general.get_updates():
        our_flag = state['player_index']
        try:
            general_r, general_c = state['generals'][our_flag]
            if main_army is None:  # Should only run on initial update
                main_army = (general_r, general_c)
                mode_settings["consolidate"]["curr_tile"] = main_army
        except KeyError:
            break

        rows, cols = state['rows'], state['cols']
        utils = GeneralUtils(rows, cols)

        moves = []
        turn, tiles, armies, cities, swamps, generals_list, alive, army_size, land_size = state['turn'], state['tile_grid'], state['army_grid'], state['cities'], state['swamps'], state['generals'], state['alives'], state['armies'], state['lands']
        unoccupied_cities = []
        for (r, c) in cities:
            if tiles[r][c] != our_flag:
                unoccupied_cities.append((r, c))

        state['cities'] = unoccupied_cities
        cities = unoccupied_cities

        for i in range(len(generals_list)):
            if i != our_flag and generals_list[i] != (-1, -1) and alive[i]:
                enemy_general=generals_list[i]

        enemy_flags = []
        for i in range(len(generals_list)):
            if i != our_flag and alive[i]:
                enemy_flags.append(i)

        enemy_flags.sort(key=lambda x: armies[x])

        if mode != "scout":
            if turn > 800:
                mode = "consolidate"
            # elif turn > 150:
            #     if turn % 100 < 25:
            #         mode = "consolidate"
            #     else:
            #         mode = "explore"
            else:
                mode = "explore"

            if mode_settings["explore"]["complete"] and mode == "explore":
                unoccupied=False
                for (a, b) in cities:
                    if tiles[a][b] < 0:
                        mode = "cities"
                        unoccupied=True
                if not unoccupied:
                    mode = "consolidate"
            elif len(mode_settings["cities"]["queued_path"]) == 0 and mode == "cities":
                mode = "consolidate"

        print(mode)
        if mode == "explore":
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
                                  utils.manhattan_dist(r, c, general_r, general_c, state))
                                 )

            moved = False
            empty = sorted(empty, key=lambda x: (x[4], x[5]))
            for i in range(len(empty)):
                c, d, a, b = empty[i][:4]
                if armies[a][b] <= 1:
                    continue

                for offset in OFFSETS:
                    adj_r = a + offset[0]
                    adj_c = b + offset[1]
                    if utils.in_bounds(adj_r, adj_c) and tiles[adj_r][adj_c] >= -1:
                        moves.append((adj_r, adj_c, utils.manhattan_dist(adj_r, adj_c, c, d, state, attack=True)))

                moves = sorted(moves, key=lambda x: x[2])
                if len(moves):
                    bm = moves[0]
                    general.move(a, b, bm[0], bm[1])
                    moved = True
                    break

            if not moved and turn % 2 == 0:
                mode_settings["explore"]["complete"] = True

        elif mode == "consolidate":
            if len(mode_settings["consolidate"]["queued_path"]) == 0 or tiles[mode_settings["consolidate"]["queued_path"][0][0]][mode_settings["consolidate"]["queued_path"][0][1]] != our_flag or mode_settings["consolidate"]["queued_path"][0] == (general_r, general_c):
                while len(mode_settings["consolidate"]["queued_path"]) < 2:
                    mode_settings["consolidate"]["queued_path"] = utils.farthest4(general_r, general_c, state)

            a, b = mode_settings["consolidate"]["queued_path"].pop(0)
            c, d = mode_settings["consolidate"]["queued_path"][0]
            general.move(a, b, c, d)

            if armies[general_r][general_c] > 300 and state["armies"][1 - our_flag] * 0.5 - armies[general_r][general_c] < turn / 2:
                mode = "scout"
                main_army = (general_r, general_c)

        elif mode == "cities":
            if len(mode_settings["cities"]["queued_path"]) < 2 or tiles[mode_settings["cities"]["queued_path"][0][0]][mode_settings["cities"]["queued_path"][0][1]] != our_flag:
                closest_city = None
                cities.sort(key=lambda x: utils.nearest_city(x[0], x[1], general_r, general_c, tiles, cities))

                for r, c in cities:
                    if tiles[r][c] < 0:
                        closest_city = (r, c)
                        break

                if closest_city is None:
                    mode = "explore"
                    mode_settings[mode]["complete"]=False
                    continue

                while len(mode_settings["cities"]["queued_path"]) < 2:
                    unoccupied_cities = []
                    for (r, c) in cities:
                        if tiles[r][c] != our_flag and (r, c) != closest_city:  # TODO
                            unoccupied_cities.append((r, c))

                    state['cities'] = unoccupied_cities
                    cities = unoccupied_cities

                    mode_settings["cities"]["queued_path"] = utils.farthest4(closest_city[0], closest_city[1], state)
                    print(mode_settings["cities"]["queued_path"])

            a, b = mode_settings["cities"]["queued_path"].pop(0)
            c, d = mode_settings["cities"]["queued_path"][0]
            general.move(a, b, c, d)

            if armies[general_r][general_c] > 300 and state["armies"][enemy_flags[0]] * 0.5 - armies[general_r][general_c] < turn / 2:
                mode = "scout"
                main_army = (general_r, general_c)

        elif mode == "scout":
            main_army = utils.find_main(tiles, armies, our_flag)  # update main army to account for server lag

            if armies[main_army[0]][main_army[1]] < 100:
                print("consolidating because not enough troops")
                mode = "consolidate"
                main_army = (general_r, general_c)

            for flag in enemy_flags:
                if generals_list[flag] != (-1, -1) and alive[flag]:
                    print(f"Enemy general found at: {generals_list[flag]}")
                    enemy_general = generals_list[flag]

            if mode_settings["scout"]["scout_target"] is None or mode_settings["scout"]["scout_target"] == main_army:
                far = utils.farthest(our_flag, tiles, cities)
                # far = utils.farthest2(general_r, general_c, our_flag, tiles, armies, cities)
                print(f"Updating scout target to {far}")
                mode_settings["scout"]["scout_target"] = far

            if enemy_general is not None:
                mode_settings["scout"]["scout_target"] = enemy_general

            a, b = main_army
            c, d = mode_settings["scout"]["scout_target"]

            for offset in OFFSETS:
                adj_r = a + offset[0]
                adj_c = b + offset[1]
                if utils.in_bounds(adj_r, adj_c) and tiles[adj_r][adj_c] >= -1:
                    moves.append((adj_r, adj_c, utils.manhattan_dist(adj_r, adj_c, c, d, state, attack=True)))

            moves = sorted(moves, key=lambda x: x[2])

            assert len(moves)
            bm = moves[0]
            general.move(a, b, bm[0], bm[1])
            main_army = (bm[0], bm[1])


if __name__ == "__main__":
    main()