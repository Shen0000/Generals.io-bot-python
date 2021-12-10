import gym
from operator import itemgetter
import logging
import numpy as np
import time
import threading
import wx

from flood_fill import GeneralUtils

logging.basicConfig(level=logging.DEBUG)

env = gym.make("gym_basic:basic-v0")
env.reset()
env.step((1, 1, 1, 2))
# tiles, armies, cities, generals = itemgetter('tiles', 'armies', 'cities', 'generals')(env.state)

OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
ARROW_OFFSETS = {"shaft": [-0.25, 0.25], "head": [(-0.1, -0.1), (0.1, -0.1)]}
PLAYER_COLORS = ['#ea3323', '#4363d8', '#027f00', '#008080', '#f58231', '#f032e6', '#800080', '#800001', '#b09f30', '#9a6324', '#0000ff', '#483d8a']
TILE_SIZE = 30
FPS = 3


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 800))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#E6E6E6")
        self.panel.Bind(wx.EVT_PAINT, self.repaint)
        self.state = None
        self.info = {"mode": "Starting", "source": (-1, -1), "button": True}
        # self.image = wx.Image('/Users/kevin_zhao/PycharmProjects/Bot2/GeneralsBot/assets/pictures/logo.png', wx.BITMAP_TYPE_ANY)
        # self.imageBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(self.image))

        self.Centre()
        self.Show()

    def repaint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.DrawText(f"Mode: {self.info['mode']}", 900, 20)
        if self.state is not None:
            tiles, armies, alives, cities, generals_list, army_size, land_size, all_cities, all_generals = \
                self.state['tiles'], self.state['armies'], [True] * 2, \
                self.state['cities'], self.state['generals'], \
                self.state['total_army'], self.state['total_land'], self.state['cities'], self.state['generals']

            self.state["usernames"] = ["test"] * 2
            for i, username in enumerate(self.state["usernames"]):
                dc.DrawText(f"{username}'s Army: {army_size[i]}", 100, 700 + i * 20)
                dc.DrawText(f"{username}'s Land: {land_size[i]}", 400, 700 + i * 20)

            dc.SetPen(wx.Pen('#000000', width=1))
            for r in range(len(tiles)):
                for c in range(len(tiles[0])):
                    if tiles[r][c] == -3:
                        dc.SetBrush(wx.Brush('#393939'))
                    elif tiles[r][c] in (-4, -2):
                        dc.SetPen(wx.Pen('#000000', width=1))
                        dc.SetBrush(wx.Brush('#bbbbbb' if tiles[r][c] == -2 else '#393939'))
                        dc.DrawRectangle(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                        if (r, c) not in all_cities:
                            mountains = [(11, 8, 3, 24), (11, 8, 18, 22), (16, 18, 20, 12), (20, 12, 27, 24)]
                            for mountain in mountains:
                                dc.DrawLine(mountain[0] + c * TILE_SIZE, mountain[1] + r * TILE_SIZE,
                                            mountain[2] + c * TILE_SIZE, mountain[3] + r * TILE_SIZE)
                        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                    elif tiles[r][c] == -1:
                        if (r, c) in cities:
                            dc.SetBrush(wx.Brush('#bbbbbb'))
                        else:
                            dc.SetBrush(wx.Brush('#dcdcdc'))
                    elif tiles[r][c] >= 0:
                        dc.SetBrush(wx.Brush(PLAYER_COLORS[tiles[r][c]]))
                    else:
                        dc.SetBrush(wx.Brush('#00c56c'))

                    if tiles[r][c] <= -3:
                        dc.SetPen(wx.Pen('#393939', width=1))
                    else:
                        dc.SetPen(wx.Pen('#000000', width=1))
                    dc.DrawRectangle(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                    if (r, c) in all_generals:
                        dc.SetPen(wx.Pen('#000000', width=3))
                        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                        dc.DrawCircle(c * TILE_SIZE + int(TILE_SIZE // 2), r * TILE_SIZE + int(TILE_SIZE // 2),
                                      int(TILE_SIZE * 0.4))
                        dc.SetPen(wx.Pen('#000000', width=1))

                    if (r, c) in all_cities:
                        dc.SetPen(wx.Pen('#000000', width=2))
                        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                        points = [
                        (c * TILE_SIZE + int(TILE_SIZE/6), r * TILE_SIZE + int(TILE_SIZE/3)),
                        (c * TILE_SIZE + int(TILE_SIZE*5/6), r * TILE_SIZE + int(TILE_SIZE/3)),
                        (c * TILE_SIZE + int(TILE_SIZE/2), r * TILE_SIZE + int(TILE_SIZE/8))
                        ]
                        dc.DrawPolygon(points)
                        dc.DrawRectangle(c * TILE_SIZE + int(TILE_SIZE*7/24), r * TILE_SIZE + int(TILE_SIZE/3), int(TILE_SIZE/2), int(TILE_SIZE/2))
                        dc.SetPen(wx.Pen('#000000', width=1))

                    if tiles[r][c] >= 0 or ((r, c) in all_cities and tiles[r][c] >= -1):
                        dc.SetTextForeground((255, 255, 255))
                        temp = str(armies[r][c])
                        if len(temp) > 3:
                            temp = f"{temp[:3]}..."

                        tw, th = dc.GetTextExtent(temp)
                        dc.DrawText(temp, TILE_SIZE * c + (TILE_SIZE - tw) // 2,
                                    TILE_SIZE * r + (TILE_SIZE - th) // 2)

                if self.info["source"] != (-1, -1):
                    dc.SetPen(wx.Pen('#ffffff', width=2))
                    dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                    dc.DrawRectangle(self.info["source"][1] * TILE_SIZE, self.info["source"][0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    dc.SetPen(wx.Pen('#000000', width=1))

                if self.info["mode"] in ("consolidate", "cities", "scout"):
                    dc.SetPen(wx.Pen('#ffffff', width=1))
                    try:
                        for i in range(len(self.info["queued_path"][:-1])):
                            start = self.info["queued_path"][i]
                            end = self.info["queued_path"][i + 1]
                            assert start != end
                            if start[0] == end[0]:
                                sign = 1 if start[1] < end[1] else -1
                                head_x = end[1] * TILE_SIZE + TILE_SIZE // 2 \
                                         + int((sign * ARROW_OFFSETS["shaft"][0]) * TILE_SIZE)  # TODO: factor out TILE_SIZE
                                center_y = start[0] * TILE_SIZE + TILE_SIZE // 2
                                dc.DrawLine(start[1] * TILE_SIZE + TILE_SIZE // 2 + sign * int((ARROW_OFFSETS["shaft"][1]) * TILE_SIZE),
                                            center_y, head_x, center_y
                                )
                                for j in range(2):
                                    dc.DrawLine(head_x + sign * int(ARROW_OFFSETS["head"][j][1] * TILE_SIZE),
                                                center_y + int(ARROW_OFFSETS["head"][j][0] * TILE_SIZE), head_x, center_y
                                    )
                            else:
                                sign = 1 if start[0] < end[0] else -1
                                head_y = end[0] * TILE_SIZE + TILE_SIZE // 2 \
                                         + int((sign * ARROW_OFFSETS["shaft"][0]) * TILE_SIZE)
                                center_x = start[1] * TILE_SIZE + TILE_SIZE // 2
                                dc.DrawLine(center_x,
                                            start[0] * TILE_SIZE + TILE_SIZE // 2
                                            + sign * int((ARROW_OFFSETS["shaft"][1]) * TILE_SIZE), center_x, head_y
                                            )
                                for j in range(2):
                                    dc.DrawLine(center_x + int(ARROW_OFFSETS["head"][j][0] * TILE_SIZE),
                                            head_y + sign * int(ARROW_OFFSETS["head"][j][1] * TILE_SIZE), center_x, head_y
                                    )
                    except:
                        print("FAILING")

                    dc.SetPen(wx.Pen('#000000', width=1))

        self.Show(True)


def main(frame):
    mode = "explore"
    main_army, enemy_general = None, None
    mode_settings = {"explore": {"complete": False}, "consolidate": {"queued_path": []}, "cities": {"queued_path": [], "complete": False, "passed": False}, "scout": {"queued_path": [], "passed": False}}
    all_cities, all_generals = set(), set()
    won = False
    env.step((0, 0, 0, 0))
    tiles, armies, cities, generals, land, army, turn = \
        itemgetter('tiles', 'armies', 'cities', 'generals', 'total_land', 'total_army', 'turn')(env.state)
    generals[1] = (-1, -1)


    state = {"tile_grid": tiles, "army_grid": armies, "cities": cities, "generals": generals, "lands": land, "turn": turn,
             "armies": army, "swamps": [], "all_cities": all_cities, "all_generals": all_generals, "alives": [True, True],
             "player_index": 0, "usernames": ["test", "test"]
            }

    while True:
        our_flag = 0
        try:
            general_r, general_c = state['generals'][our_flag]
            if main_army is None:  # Should only run on initial update
                main_army = (general_r, general_c)
                mode_settings["consolidate"]["curr_tile"] = main_army
        except KeyError:
            break
        rows = env.SIZE
        cols = env.SIZE
        utils = GeneralUtils(rows, cols)

        masked_state = env.denoise()
        turn, tiles, armies, cities, generals_list, army_size, land_size = \
            masked_state['turn'], masked_state['tiles'], masked_state['armies'], masked_state['cities'], \
            masked_state['generals'], masked_state['total_army'], masked_state['total_land']
        alive = [True] * 2

        moves = []
        unoccupied_cities = []
        for (r, c) in cities:
            all_cities.add((r, c))
            if tiles[r][c] != our_flag:
                unoccupied_cities.append((r, c))

        state['all_cities'] = all_cities
        state['cities'] = unoccupied_cities
        cities = unoccupied_cities

        for i in range(len(generals_list)):
            if i != our_flag and generals_list[i] != (-1, -1) and alive[i]:
                enemy_general = generals_list[i]
                all_generals.add(generals_list[i])
        all_generals.add(generals_list[our_flag])
        state['all_generals'] = all_generals

        enemy_flags = []
        for i in range(len(generals_list)):
            if i != our_flag and alive[i]:
                enemy_flags.append(i)

        enemy_flags.sort(key=lambda x: armies[x])

        if mode not in ("scout", "cities"):
            if mode_settings["explore"]["complete"] and mode == "explore":
                if mode_settings["cities"]["complete"]:
                    mode = "consolidate"
                else:
                    mode = "cities"
            elif len(mode_settings["cities"]["queued_path"]) == 0 and mode == "cities":
                mode = "explore"
        
        frame.state = env.denoise()
        frame.info["mode"] = mode

        if mode == "explore":
            all_adj_tiles = set()
            empty_adj_tiles = []
            for r in range(rows):
                for c in range(cols):
                    if tiles[r][c] == our_flag:
                        for offset in OFFSETS:
                            all_adj_tiles.add((r + offset[0], c + offset[1]))

            for (r, c) in all_adj_tiles:
                if not utils.in_bounds(r, c) or tiles[r][c] != -1:
                    continue

                a, b, d = utils.closest(r, c, our_flag, tiles, armies, cities)
                if (a, b, d) != (-1, -1, -1):
                    empty_adj_tiles.append((r, c, a, b, d,
                                  utils.manhattan_dist(r, c, general_r, general_c, state))
                                 )
            moved = False
            empty_adj_tiles = sorted(empty_adj_tiles, key=lambda x: (x[4], x[5]))
            for i in range(len(empty_adj_tiles)):
                c, d, a, b = empty_adj_tiles[i][:4]
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
                    env.step((a, b, bm[0], bm[1]))
                    moved = True
                    break

            if not moved:  # and turn % 2 == 0:
                mode_settings["explore"]["complete"] = True

            for (r, c) in cities:  # check so that we explore everything
                if tiles[r][c] < 0:
                    mode_settings["cities"]["complete"] = False

        elif mode == "consolidate":
            if len(mode_settings["consolidate"]["queued_path"]) == 0 or tiles[mode_settings["consolidate"]["queued_path"][0][0]][mode_settings["consolidate"]["queued_path"][0][1]] != our_flag or mode_settings["consolidate"]["queued_path"][0] == (general_r, general_c):
                while len(mode_settings["consolidate"]["queued_path"]) < 2:
                    mode_settings["consolidate"]["queued_path"] = utils.farthest4(general_r, general_c, state)

            frame.info["queued_path"] = mode_settings["consolidate"]["queued_path"]
            a, b = mode_settings["consolidate"]["queued_path"].pop(0)
            c, d = mode_settings["consolidate"]["queued_path"][0]
            env.step((a, b, c, d))

            if armies[general_r][general_c] > 300 and state["armies"][1 - our_flag] * 0.5 - armies[general_r][general_c] < turn / 2:
                mode = "scout"
                main_army = (general_r, general_c)

        elif mode == "cities":
            if len(mode_settings["cities"]["queued_path"]) < 2 or tiles[mode_settings["cities"]["queued_path"][0][0]][mode_settings["cities"]["queued_path"][0][1]] != our_flag:
                if mode_settings["cities"]["passed"]:
                    mode_settings["cities"]["passed"] = False
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
                else:
                    mode_settings["cities"]["passed"] = True
                    time.sleep(0.25)
                    continue

            frame.info["queued_path"] = mode_settings["cities"]["queued_path"]
            a, b = mode_settings["cities"]["queued_path"].pop(0)
            c, d = mode_settings["cities"]["queued_path"][0]
            env.step((a, b, c, d))

            if armies[general_r][general_c] > 300 and state["armies"][enemy_flags[0]] * 0.5 - armies[general_r][general_c] < turn / 2:
                mode = "scout"
                main_army = (general_r, general_c)

        elif mode == "scout":
            main_army = utils.find_main(tiles, armies, our_flag)  # update main army to account for server lag
            if armies[main_army[0]][main_army[1]] < 100:
                mode = "consolidate"
                continue

            if len(mode_settings["scout"]["queued_path"]) <= 2:
                if mode_settings["scout"]["passed"]:
                    while len(mode_settings["scout"]["queued_path"]) < 2:
                        mode_settings["scout"]["queued_path"] = utils.farthest5(main_army[0], main_army[1], state)
                    print(f'New path: {mode_settings["scout"]["queued_path"]}')
                    mode_settings["scout"]["passed"] = False
                else:
                    mode_settings["scout"]["passed"] = True
                    time.sleep(0.25)
                    continue

            if enemy_general is not None and (len(mode_settings["scout"]["queued_path"]) == 0 or mode_settings["scout"]["queued_path"][-1] != enemy_general):
                if mode_settings["scout"]["passed"]:
                    mode_settings["scout"]["queued_path"] = utils.farthest5(main_army[0], main_army[1], state,
                                                                            enemy_general[0], enemy_general[1])
                    mode_settings["scout"]["passed"] = False
                else:
                    mode_settings["scout"]["passed"] = True
                    time.sleep(0.25)
                    continue

            frame.info["queued_path"] = mode_settings["scout"]["queued_path"]
            a, b = mode_settings["scout"]["queued_path"].pop(0)
            c, d = mode_settings["scout"]["queued_path"][0]
            env.step((a, b, c, d))

        for flag in enemy_flags:
            if generals_list[flag] in all_generals and alive[flag]:
                print(f"Enemy general found at: {generals_list[flag]}")
                enemy_general = generals_list[flag]

        # frame.info["source"] = (a, b)
        wx.CallAfter(frame.Refresh)
    time.sleep(1)
    if won:
        frame.info["mode"] = "Victory!"
    else:
        frame.info["mode"] = "Defeat!"
    wx.CallAfter(frame.Refresh)
    cnt = 0
    while True:
        time.sleep(1)
        print(cnt)
        cnt += 1

    wx.CallAfter(frame.Destroy)


if __name__ == "__main__":
    app = wx.App()
    f = MyFrame(None, "Bot Visualizer")
    thread = threading.Thread(target=main, args=[f])
    thread.setDaemon(True)
    thread.start()
    app.MainLoop()