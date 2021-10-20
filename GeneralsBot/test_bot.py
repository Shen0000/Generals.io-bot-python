import logging
import time
import threading

from flood_fill import GeneralUtils
from init_game import general
from config import GAME_ID
import wx


logging.basicConfig(level=logging.DEBUG)
OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
PLAYER_COLORS = ['#ea3323', '#4a62d1']
TILE_SIZE = 30



class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 800))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#E6E6E6")
        self.panel.Bind(wx.EVT_PAINT, self.repaint)
        self.state = None
        self.info = {"mode": "Starting", "source": (-1, -1), "button": True}
        self.button = wx.Button(self.panel, wx.ID_ANY, "Toggle force start", (50, 50))
        self.button.Bind(wx.EVT_BUTTON, self.onButtonForce)
        self.speedp25 = wx.Button(self.panel, .25, "0.25", (300, 50))
        self.speedp5 = wx.Button(self.panel, .5, "0.5", (300, 100))
        self.speedp75 = wx.Button(self.panel, .75, "0.75", (300, 150))
        self.speed1 = wx.Button(self.panel, 1, "1", (300, 200))
        self.speed1p5 = wx.Button(self.panel, 1.5, "1.5", (300, 250))
        self.speed2 = wx.Button(self.panel, 2, "2", (300, 300))
        self.speed3 = wx.Button(self.panel, 3, "3", (300, 350))
        self.speed4 = wx.Button(self.panel, 4, "4", (300, 400))
        self.speedp25.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.speedp5.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.speedp75.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.speed1.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.speed1p5.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.speed2.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.speed3.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.speed4.Bind(wx.EVT_BUTTON, self.onButtonSpeed)
        self.Centre()
        self.Show()

    def repaint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.DrawText(f"Mode: {self.info['mode']}", 600, 20)
        if self.state is not None:
            if self.info['button']:
                self.button.Destroy()
                self.speedp25.Destroy()
                self.speedp5.Destroy()
                self.speedp75.Destroy()
                self.speed1.Destroy()
                self.speed1p5.Destroy()
                self.speed2.Destroy()
                self.speed3.Destroy()
                self.speed4.Destroy()
                self.info['button'] = False

            turn, tiles, armies, cities, swamps, generals_list, alive, army_size, land_size, all_cities, all_generals = \
                self.state['turn'], self.state['tile_grid'], self.state['army_grid'], \
                self.state['cities'], self.state['swamps'], self.state['generals'], \
                self.state['alives'], self.state['armies'], self.state['lands'], \
                self.state['all_cities'], self.state['all_generals']

            for i, username in enumerate(self.state["usernames"]):
                dc.DrawText(f"{username}'s Army: {army_size[i]}", 600, 40 + i * 20)
                dc.DrawText(f"{username}'s Land: {land_size[i]}", 800, 40 + i * 20)

            dc.SetPen(wx.Pen('#000000', width=1))
            for r in range(len(tiles)):
                for c in range(len(tiles[0])):
                    if tiles[r][c] in (-3, -4):
                        dc.SetBrush(wx.Brush('#393939'))
                    elif tiles[r][c] == -2:
                        dc.SetBrush(wx.Brush('#bbbbbb'))
                        dc.DrawRectangle(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
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
                    dc.DrawRectangle(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                    if (r, c) in all_generals:
                        dc.SetPen(wx.Pen('#000000', width=3))
                        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                        dc.DrawCircle(c * TILE_SIZE + int(TILE_SIZE // 2), r * TILE_SIZE + int(TILE_SIZE // 2), int(TILE_SIZE * 0.4))
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
                    dc.SetPen(wx.Pen('#ffffff', width=3))
                    dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                    dc.DrawRectangle(self.info["source"][1] * TILE_SIZE, self.info["source"][0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    dc.SetPen(wx.Pen('#000000', width=1))
        else:
            dc.DrawText("Speed: ", 320, 25)
            if general.force:
                dc.DrawText("Forcing", 100, 100)
            else:
                dc.DrawText("Not Forcing", 100, 100)
        self.Show(True)

    def onButtonForce(self, event):
        if general.force:
            general.force_start(GAME_ID, False)
            general.force = False
        else:
            general.force_start(GAME_ID, True)
            general.force = True
        self.Refresh()
    
    def onButtonSpeed(self, event):
        btn = event.GetEventObject().GetLabel() 
        general.set_game_speed(btn)


def main(frame):
    mode = "explore"
    main_army, enemy_general = None, None
    mode_settings = {"explore": {"complete": False}, "consolidate": {"queued_path": []}, "cities": {"queued_path": [], "complete": False}, "scout": {"scout_target": None}}
    all_cities, all_generals = set(), set()

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

            for (r, c) in cities: # check so that we explore everything
                if tiles[r][c] < 0:
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

        for flag in enemy_flags:
            if generals_list[flag] in all_generals and alive[flag]:
                print(f"Enemy general found at: {generals_list[flag]}")
                enemy_general = generals_list[flag]

        frame.state = state
        frame.info["mode"] = mode
        frame.info["source"] = (a, b)
        wx.CallAfter(frame.Refresh)

    wx.CallAfter(frame.Destroy)


if __name__ == "__main__":
    app = wx.App()
    f = MyFrame(None, "Bot Visualizer")
    thread = threading.Thread(target=main, args=[f])
    thread.setDaemon(True)
    thread.start()
    app.MainLoop()