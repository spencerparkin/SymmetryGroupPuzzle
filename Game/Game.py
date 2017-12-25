# Game.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from Math.Rectangle import Rectangle
from Math.Vector import Vector
from Puzzle.Level import MakePuzzle
from Puzzle.Texture import Texture

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Symmetry Group Puzzle')
        self.context = None
        self.level = 1
        self.puzzle = MakePuzzle(self.level)
        self.texture = Texture('Images/image0.png')
        self.adjusted_window = None
        self.selected_cutter = None

    def initializeGL(self):
        #self.context = QtGui.QOpenGLContext(self)
        #format = QtGui.QSurfaceFormat()
        #self.context.setFormat(format)
        #self.context.create()
        #self.context.makeCurrent(self)

        glShadeModel(GL_SMOOTH)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.7, 0.7, 0.7, 0.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        screen_rectangle = Rectangle(Vector(0.0, 0.0), Vector(float(width), float(height)))
        self.adjusted_window = self.puzzle.window.Clone()
        self.adjusted_window.ContractToMatchAspectRatioOf(screen_rectangle)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.adjusted_window.min_point.x,
                   self.adjusted_window.max_point.x,
                   self.adjusted_window.min_point.y,
                   self.adjusted_window.max_point.y)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.texture.Bind()
        glBegin(GL_QUADS)
        try:
            glTexCoord2f(0.0, 0.0)
            glVertex2f(self.puzzle.window.min_point.x, self.puzzle.window.min_point.y)
            glTexCoord2f(1.0, 0.0)
            glVertex2f(self.puzzle.window.max_point.x, self.puzzle.window.min_point.y)
            glTexCoord2f(1.0, 1.0)
            glVertex2f(self.puzzle.window.max_point.x, self.puzzle.window.max_point.y)
            glTexCoord2f(0.0, 1.0)
            glVertex2f(self.puzzle.window.min_point.x, self.puzzle.window.max_point.y)
        finally:
            glEnd()

        glDisable(GL_TEXTURE_2D)
        self.puzzle.RenderShadow()

        self.texture.Bind()
        self.puzzle.RenderShapes()

        if self.selected_cutter is not None:
            cutter = self.puzzle.cutter_list[self.selected_cutter]
            cutter.RenderOutline()

        glFlush()

    def resizeGL(self, width, height):
        pass # glViewport(0, 0, width, height)

    def mousePressEvent(self, event):
        # TODO: Selected cutter center to point click gives axis for reflection symmetry.
        pass # self.puzzle.ApplyCuttingPolygon(self.selected_cutter, symmetry)

    def mouseMoveEvent(self, event):
        if self.adjusted_window is not None:
            rectangle = Rectangle(Vector(0.0, 0.0), Vector(float(self.width()), float(self.height())))
            point = Vector(float(event.x()), float(event.y()))
            point = rectangle.Map(point, self.adjusted_window)
            self.selected_cutter = self.puzzle.NearestCutter(point)
            self.update()

    # TODO: Highlight nearest cutter to mouse at all times.
    #       Use mouse wheel for rotations; clicks for reflections.
    #       Based on click point, query cutter shape for reflection axis.

    # TODO: Let them choose any picture for any puzzle.
    #       Let them skip any level and go to the next.

    # TODO: Support puzzle saving and loading.  The puzzle object
    #       should serialize and deserialize to/from JSON.

def ExceptionHook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)

if __name__ == '__main__':
    sys.excepthook = ExceptionHook
    app = QtGui.QGuiApplication(sys.argv)
    win = Window()
    win.resize(640, 480)
    win.show()
    ret_code = app.exec_()
    sys.exit(ret_code)