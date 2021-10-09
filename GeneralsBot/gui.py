import wx
from make_map import create_map


tiles, cities = create_map(data=[1, 1, 1, 0, 1, 2])
rows = len(tiles)
cols = len(tiles[0])
armies = [[0 for _ in range(cols)] for __ in range(rows)]
assert rows == len(armies) and cols == len(armies[0])

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 400))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#E6E6E6")
        self.panel.Bind(wx.EVT_PAINT, self.repaint)

        self.Centre()
        self.Show()

    def repaint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetPen(wx.Pen('#000000'))
        for r in range(rows):
            for c in range(cols):
                if tiles[r][c] in (-3, -4):
                    dc.SetBrush(wx.Brush('#393939'))
                elif tiles[r][c] == -2:
                    dc.SetBrush(wx.Brush('#bbbbbb'))
                elif tiles[r][c] == -1:
                    if (r, c) in cities:
                        dc.SetBrush(wx.Brush('#c0ff00'))
                    else:
                        dc.SetBrush(wx.Brush('#dcdcdc'))
                elif tiles[r][c] == 0:
                    dc.SetBrush(wx.Brush('#ea3323'))
                elif tiles[r][c] == 1:
                    dc.SetBrush(wx.Brush('#4a62d1'))
                else:
                    dc.SetBrush(wx.Brush('#00c56c'))
                dc.DrawRectangle(c * 30, r * 30, 30, 30)

        self.Show(True)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, "Test")
    app.MainLoop()