# Game.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from Math.Rectangle import Rectangle
from Math.Vector import Vector
from Puzzle.Level import MakePuzzle

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Symmetry Group Puzzle')
        self.context = None
        self.level = 1
        self.puzzle = MakePuzzle(self.level)

    def initializeGL(self):
        self.context = QtGui.QOpenGLContext(self)
        format = QtGui.QSurfaceFormat()
        self.context.setFormat(format)
        self.context.create()
        self.context.makeCurrent(self)

        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.7, 0.7, 0.7, 0.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        screen_rectangle = Rectangle(Vector(0.0, 0.0), Vector(float(width), float(height)))
        adjusted_window = self.puzzle.window.Clone()
        adjusted_window.ContractToMatchAspectRatioOf(screen_rectangle)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(adjusted_window.min_point.x,
                   adjusted_window.max_point.x,
                   adjusted_window.min_point.y,
                   adjusted_window.max_point.y)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        # TODO: Bind texture here.
        # TODO: Draw the entire texture across the whole screen.
        # TODO: Draw the cutter shapes black.
        # TODO: Now render puzzle over the black.  The black serves to show what's cut out of the background.

        #self.puzzle.Render()

        glFlush()

    def mousePressEvent(self, event):
        pass

    # TODO: Highlight nearest cutter to mouse at all times.
    #       Use mouse wheel for rotations; clicks for reflections.

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