import logging
import math

from flood_fill import GeneralUtils
from init_game import general


logging.basicConfig(level=logging.DEBUG)


OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def main():
    mode = "explore"
    main_army, rush_target, enemy_general = None, None, None
    mode_settings = {"explore": {"complete": False}, "consolidate": {"queued_path": []}}

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

        turn, tiles, armies, cities, swamps, generals_list = state['turn'], state['tile_grid'], state['army_grid'], state['cities'], state['swamps'], state['generals']
        moves = []

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

            if mode_settings["explore"]["complete"] and mode == "explore":
                mode = "consolidate"

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
                mode = "rush"
                main_army = (general_r, general_c)

        elif mode == "rush":
            main_army = utils.find_main(tiles, armies, our_flag)  # update main army to account for server lag

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

            a, b = main_army
            c, d = rush_target

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