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

    done_exploring = False

    for state in general.get_updates():
        our_flag = state['player_index']
        try:
            general_r, general_c = state['generals'][our_flag]
            if main_army is None:
                main_army = (general_r, general_c)
                mode_settings["consolidate"]["curr_tile"] = main_army
        except KeyError:
            break

        rows, cols = state['rows'], state['cols']
        utils = GeneralUtils(rows, cols)

        turn, tiles, armies, cities, swamps, generals_list = state['turn'], state['tile_grid'], state['army_grid'], state['cities'], state['swamps'], state['generals']

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

                # print(a, b, c, d)
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

        elif mode == "consolidate":
            if len(mode_settings["consolidate"]["queued_path"]) == 0 or tiles[mode_settings["consolidate"]["queued_path"][0][0]][mode_settings["consolidate"]["queued_path"][0][1]] != our_flag or mode_settings["consolidate"]["queued_path"][0] == (general_r, general_c):
                while len(mode_settings["consolidate"]["queued_path"]) < 2:
                #     if len(mode_settings["consolidate"]["queued_path"]) == 1:
                #         assert mode_settings["consolidate"]["queued_path"][0] == (general_r, general_c)
                    mode_settings["consolidate"]["queued_path"] = utils.farthest4(general_r, general_c, our_flag, tiles, armies, cities)
                    print(f'changed to {mode_settings["consolidate"]["queued_path"]}')

            a, b = mode_settings["consolidate"]["queued_path"].pop(0)
            c, d = mode_settings["consolidate"]["queued_path"][0]
            print(a, b, c, d)
            general.move(a, b, c, d)

            if armies[general_r][general_c] > 300 and state["armies"][1 - our_flag] * 0.5 - armies[general_r][general_c] < turn / 2:
                mode = "rush"
                main_army = (general_r, general_c)

        elif mode == "rush":
            main_army=utils.find_main(tiles, armies, our_flag) #update main army to account for server lag

            if armies[main_army[0]][main_army[1]] < 100:
                print("consolidating because not enough troops")
                mode = "consolidate"
                main_army = (general_r, general_c)

            assert len(state["armies"]) == 2, "Assuming 1v1"
            enemy_flag = 1 - our_flag

            if generals_list[enemy_flag] != (-1, -1):
                print(f"Enemy general found at: {generals_list[enemy_flag]}")
                enemy_general = generals_list[enemy_flag]

            if rush_target is None or rush_target == main_army:
                far = utils.farthest(our_flag, tiles, cities)
                # far = utils.farthest2(general_r, general_c, our_flag, tiles, armies, cities)
                print(f"Updating rush target to {far}")
                rush_target = far

            if enemy_general is not None:
                rush_target = enemy_general

            a, b = main_army #best[2:4]
            c, d = rush_target
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