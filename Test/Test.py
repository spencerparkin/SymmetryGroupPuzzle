# Test.py

# Here we test various algorithms and data-structures to be used in the web-app.
# It is a means to an end, not an end in and of itself.

import wx

class TestFrame(wx.Frame):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE
        super().__init__(parent, wx.ID_ANY, "Test", wx.DefaultPosition, wx.DefaultSize, style)

        attrib_list = [
            wx.glcanvas.WX_GL_RGBA,
            wx.glcanvas.WX_GL_DOUBLEBUFFER,
            wx.glcanvas.WX_GL_DEPTH_SIZE, 24
        ]

        self.canvas = wx.glcanvas.GLCanvas(self, attrib_list)

        self.canvas.Bind(wx.EVT_SIZE, self.OnCanvasResize)
        self.canvas.Bind(wx.EVT_PAINT, self.OnCanvasPaint)

    def OnCanvasResize(self):
        pass

    def OnCanvasPaint(self):
        pass

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = TestFrame(None)
    frame.Show()
    app.MainLoop()
    app.Destroy()