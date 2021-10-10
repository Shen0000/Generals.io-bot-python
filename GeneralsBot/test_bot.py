import logging
import math
import threading

from flood_fill import GeneralUtils
from init_game import general
import wx


logging.basicConfig(level=logging.DEBUG)
OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
TILE_SIZE = 30


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000, 1000))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#E6E6E6")
        self.panel.Bind(wx.EVT_PAINT, self.repaint)
        self.tiles = None
        self.cities = None
        self.armies = None

        self.Centre()
        self.Show()

    def repaint(self, event):
        if self.tiles is not None:
            dc = wx.PaintDC(self.panel)
            dc.SetPen(wx.Pen('#000000'))
            for r in range(len(self.tiles)):
                for c in range(len(self.tiles[0])):
                    if self.tiles[r][c] in (-3, -4):
                        dc.SetBrush(wx.Brush('#393939'))
                    elif self.tiles[r][c] == -2:
                        dc.SetBrush(wx.Brush('#bbbbbb'))
                    elif self.tiles[r][c] == -1:
                        if (r, c) in self.cities:
                            dc.SetBrush(wx.Brush('#c0ff00'))
                        else:
                            dc.SetBrush(wx.Brush('#dcdcdc'))
                    elif self.tiles[r][c] == 0:
                        dc.SetBrush(wx.Brush('#ea3323'))
                    elif self.tiles[r][c] == 1:
                        dc.SetBrush(wx.Brush('#4a62d1'))
                    else:
                        dc.SetBrush(wx.Brush('#00c56c'))
                    dc.DrawRectangle(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.tiles[r][c] >=-1:
                        dc.DrawText(str(self.armies[r][c]), TILE_SIZE * c + 10, TILE_SIZE * r + 8)

        self.Show(True)


def main(frame):
    mode = "explore"
    main_army, enemy_general = None, None
    mode_settings = {"explore": {"complete": False}, "consolidate": {"queued_path": []}, "cities": {"queued_path": [], "complete": False}, "scout": {"scout_target": None}}

    for state in general.get_updates():
        our_flag = state['player_index']
        try:
            general_r, general_c = state['generals'][our_flag]
            if main_army is None:  # Should only run on initial update
                main_army = (general_r, general_c)
                mode_settings["consolidate"]["curr_tile"] = main_army
        except KeyError:
            break
        rows = state['rows']
        cols = state['cols']
        utils = GeneralUtils(rows, cols)

        turn, tiles, armies, cities, swamps, generals_list, alive, army_size, land_size = \
            state['turn'], state['tile_grid'], state['army_grid'], state['cities'], state['swamps'], \
            state['generals'], state['alives'], state['armies'], state['lands']

        frame.tiles = tiles
        frame.cities = cities
        frame.armies = armies
        wx.CallAfter(frame.Refresh)

        moves = []
        unoccupied_cities = []
        for (r, c) in cities:
            if tiles[r][c] != our_flag:
                unoccupied_cities.append((r, c))

        state['cities'] = unoccupied_cities
        cities = unoccupied_cities

        for i in range(len(generals_list)):
            if i != our_flag and generals_list[i] != (-1, -1) and alive[i]:
                enemy_general = generals_list[i]

        enemy_flags = []
        for i in range(len(generals_list)):
            if i != our_flag and alive[i]:
                enemy_flags.append(i)

        enemy_flags.sort(key=lambda x: armies[x])

        if mode != "scout":
            if turn > 800:
                mode = "consolidate"
            else:
                mode = "explore"

            if mode_settings["explore"]["complete"] and mode == "explore":
                if mode_settings["cities"]["complete"]:
                    mode = "consolidate"
                else:
                    mode = "cities"
            elif len(mode_settings["cities"]["queued_path"]) == 0 and mode == "cities":
                mode = "explore"

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

            for (a, b) in cities: # check so that we explore everything
                if tiles[a][b] < 0:
                    mode_settings["cities"]["complete"] = False

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
                    if tiles[r][c] == -1:
                        closest_city = (r, c)
                        break

                if closest_city is None:
                    mode = "explore"
                    mode_settings["cities"]["complete"] = True
                    mode_settings["explore"]["complete"] = False
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
                mode = "consolidate"
                main_army = (general_r, general_c)

            for flag in enemy_flags:
                if generals_list[flag] != (-1, -1) and alive[flag]:
                    print(f"Enemy general found at: {generals_list[flag]}")
                    enemy_general = generals_list[flag]

            if mode_settings["scout"]["scout_target"] is None or mode_settings["scout"]["scout_target"] == main_army:
                far = utils.farthest(our_flag, tiles, cities)
                mode_settings["scout"]["scout_target"] = far

            if enemy_general is not None:
                mode_settings["scout"]["scout_target"] = enemy_general

            a, b = main_army
            c, d = mode_settings["scout"]["scout_target"]

            for offset in OFFSETS:
                adj_r, adj_c = a + offset[0], b + offset[1]
                if utils.in_bounds(adj_r, adj_c) and tiles[adj_r][adj_c] >= -1:
                    moves.append((adj_r, adj_c, utils.manhattan_dist(adj_r, adj_c, c, d, state, attack=True)))

            moves = sorted(moves, key=lambda x: x[2])

            assert len(moves)
            bm = moves[0]
            general.move(a, b, bm[0], bm[1])
            main_army = (bm[0], bm[1])
    wx.CallAfter(frame.Destroy)


if __name__ == "__main__":
    app = wx.App()
    f = MyFrame(None, "Bot Visualizer")
    thread = threading.Thread(target=main, args=[f])
    thread.setDaemon(True)
    thread.start()
    app.MainLoop()
